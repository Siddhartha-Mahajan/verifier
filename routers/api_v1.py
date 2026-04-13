import asyncio
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hmac import compare_digest
from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import (
	API_VERSION,
	LEADERBOARD_PASSWORD,
	RATE_LIMIT_PER_DAY,
	RATE_LIMIT_PER_HOUR,
	RATE_LIMIT_PER_MINUTE,
	RATE_LIMIT_PER_SECOND,
)
from database import get_db
from helper.conway import verify as verify_conway
from helper.hadamard import ALLOWED_N as HADAMARD_ALLOWED_N
from helper.hadamard import get_record as hadamard_record
from helper.hadamard import verify as verify_hadamard
from helper.hpprotein import get_instances as hpprotein_instances
from helper.hpprotein import get_record as hpprotein_record
from helper.hpprotein import verify as verify_hpprotein
from helper.stilllife import ALLOWED_N as STILLLIFE_ALLOWED_N
from helper.stilllife import get_record as stilllife_record
from helper.stilllife import verify as verify_stilllife
from helper.tensor import ALLOWED_SIZES as TENSOR_ALLOWED_SIZES
from helper.tensor import get_record as tensor_record
from helper.tensor import verify as verify_tensor
from models import Submission
from schema import (
	ErrorResponse,
	HealthResponse,
	LeaderboardEntryResponse,
	LeaderboardRequest,
	LeaderboardResponse,
	ProblemInstancesResponse,
	SubmissionResponse,
	SubmitFailureResponse,
	SubmitRequest,
	SubmitSuccessResponse,
)


def _as_int(value: Any, default: int) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		return default


RATE_LIMIT_PER_SECOND = _as_int(RATE_LIMIT_PER_SECOND, 1)
RATE_LIMIT_PER_MINUTE = _as_int(RATE_LIMIT_PER_MINUTE, 5)
RATE_LIMIT_PER_HOUR = _as_int(RATE_LIMIT_PER_HOUR, 10)
RATE_LIMIT_PER_DAY = _as_int(RATE_LIMIT_PER_DAY, 100)
API_VERSION = API_VERSION or "1.0.0"
PROBLEM_TIMEOUTS = {
	"hadamard": 60,
	"conway": 10,
	"tensor": 30,
	"stilllife": 10,
	"hpprotein": 10,
}
HIGHER_SCORE_BETTER_PROBLEMS = ["hadamard", "conway", "stilllife", "hpprotein"]
LOWER_SCORE_BETTER_PROBLEMS = ["tensor"]
PROBLEM_MAX_PAYLOAD_BYTES = {
	"hadamard": 500 * 1024,
	"conway": 100 * 1024,
	"tensor": 200 * 1024,
	"stilllife": 50 * 1024,
	"hpprotein": 100 * 1024,
}


def _json_error(status_code: int, error_code: str, message: str, **extra: Any) -> JSONResponse:
	payload: dict[str, Any] = {"success": False, "error_code": error_code, "message": message}
	payload.update(extra)
	return JSONResponse(status_code=status_code, content=payload)


def _to_json_number(value: Any) -> Any:
	if value is None:
		return None
	if isinstance(value, Decimal):
		if value == value.to_integral_value():
			return int(value)
		return float(value)
	return value


def _utc_now() -> datetime:
	return datetime.now(timezone.utc)


def _iso_utc(value: datetime) -> str:
	return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_instance(problem_name: str, instance: dict[str, Any]) -> dict[str, Any]:
	if problem_name == "conway":
		return {}
	if problem_name in {"hadamard", "stilllife"}:
		return {"n": _as_int(instance.get("n"), -1)}
	if problem_name == "tensor":
		return {
			"n": _as_int(instance.get("n"), -1),
			"m": _as_int(instance.get("m"), -1),
			"p": _as_int(instance.get("p"), -1),
		}
	if problem_name == "hpprotein":
		sequence_id = instance.get("sequence_id")
		if isinstance(sequence_id, str):
			sequence_id = sequence_id.strip().upper()
		return {"sequence_id": sequence_id}
	return instance


def _is_valid_email(email: str) -> bool:
	if not isinstance(email, str):
		return False
	if "@" not in email:
		return False
	_, domain = email.rsplit("@", 1)
	return "." in domain and len(domain.split(".")[-1]) > 0


def _valid_scored_entries(submissions: list[Submission]) -> list[tuple[Submission, Decimal]]:
	entries: list[tuple[Submission, Decimal]] = []
	for submission in submissions:
		if not submission.is_valid:
			continue
		if submission.score is None:
			continue
		entries.append((submission, Decimal(str(submission.score))))
	return entries


def _calculate_percentile_map(problem_name: str, submissions: list[Submission]) -> dict[UUID, float]:
	direction = _score_direction_for_problem(problem_name)
	valid_entries = _valid_scored_entries(submissions)
	if not valid_entries:
		return {}

	total = len(valid_entries)
	score_counts = Counter(score for _, score in valid_entries)
	sorted_scores = sorted(score_counts.keys())

	score_to_percentile: dict[Decimal, float] = {}
	if direction == "low":
		cumulative = 0
		for score in reversed(sorted_scores):
			cumulative += score_counts[score]
			score_to_percentile[score] = round((100.0 * cumulative) / total, 4)
	else:
		cumulative = 0
		for score in sorted_scores:
			cumulative += score_counts[score]
			score_to_percentile[score] = round((100.0 * cumulative) / total, 4)

	percentiles: dict[UUID, float] = {}
	for submission, score in valid_entries:
		percentiles[submission.submission_id] = score_to_percentile[score]
	return percentiles


async def _compute_percentile(
	db: AsyncSession,
	problem_name: str,
	instance: dict[str, Any],
	score: Any,
	score_direction: str,
	submission_id: UUID | None = None,
) -> float | None:
	if score is None and submission_id is None:
		return None

	stmt = select(Submission).where(
		Submission.problem_name == problem_name,
		Submission.instance == instance,
	)
	result = await db.execute(stmt)
	submissions = result.scalars().all()
	percentile_map = _calculate_percentile_map(problem_name, submissions)

	if submission_id is not None:
		return percentile_map.get(submission_id)

	if score is None:
		return None

	valid_entries = _valid_scored_entries(submissions)
	if not valid_entries:
		return None

	direction = score_direction if score_direction in {"high", "low"} else _score_direction_for_problem(problem_name)
	score_num = Decimal(str(score))
	if direction == "low":
		worse_or_equal_count = sum(1 for _, entry_score in valid_entries if entry_score >= score_num)
	else:
		worse_or_equal_count = sum(1 for _, entry_score in valid_entries if entry_score <= score_num)

	return round((100.0 * worse_or_equal_count) / len(valid_entries), 4)


async def _recompute_instance_percentiles(
	db: AsyncSession,
	problem_name: str,
	instance: dict[str, Any],
) -> None:
	stmt = select(Submission).where(
		Submission.problem_name == problem_name,
		Submission.instance == instance,
	)
	result = await db.execute(stmt)
	submissions = result.scalars().all()

	percentile_map = _calculate_percentile_map(problem_name, submissions)
	for submission in submissions:
		submission.percentile = percentile_map.get(submission.submission_id)

	await db.commit()


async def _check_rate_limit(
	db: AsyncSession,
	ip_address: str,
	problem_name: str,
) -> tuple[bool, str | None, int | None]:
	now = _utc_now()
	checks = [
		(
			RATE_LIMIT_PER_SECOND,
			timedelta(seconds=1),
			f"Rate limit exceeded: {RATE_LIMIT_PER_SECOND} submission(s) per second per problem",
			True,
		),
		(
			RATE_LIMIT_PER_MINUTE,
			timedelta(minutes=1),
			f"Rate limit exceeded: {RATE_LIMIT_PER_MINUTE} submissions per minute per problem",
			True,
		),
		(
			RATE_LIMIT_PER_HOUR,
			timedelta(hours=1),
			f"Rate limit exceeded: {RATE_LIMIT_PER_HOUR} submissions per hour per problem",
			True,
		),
		(
			RATE_LIMIT_PER_DAY,
			timedelta(days=1),
			f"Rate limit exceeded: {RATE_LIMIT_PER_DAY} submissions per day per problem",
			True,
		),
	]

	for limit, window, message, include_problem in checks:
		if limit <= 0:
			continue
		stmt = select(func.count()).select_from(Submission).where(
			Submission.ip_address == ip_address,
			Submission.created_at >= now - window,
		)
		if include_problem:
			stmt = stmt.where(Submission.problem_name == problem_name)
		count = int((await db.execute(stmt)).scalar_one() or 0)
		if count >= limit:
			return False, message, int(window.total_seconds())

	return True, None, None


def _extract_client_ip(request: Request) -> str:
	client_ip = request.client.host if request.client else "unknown"
	forwarded_for = request.headers.get("X-Forwarded-For")
	if forwarded_for:
		client_ip = forwarded_for.split(",")[0].strip()
	return client_ip


def _get_problem_instances(problem_name: str) -> list[dict[str, Any]] | None:
	if problem_name == "hadamard":
		return [{"n": n} for n in HADAMARD_ALLOWED_N]
	if problem_name == "conway":
		return [{}]
	if problem_name == "tensor":
		return [{"n": n, "m": m, "p": p} for n, m, p in TENSOR_ALLOWED_SIZES]
	if problem_name == "stilllife":
		return [{"n": n} for n in STILLLIFE_ALLOWED_N]
	if problem_name == "hpprotein":
		return hpprotein_instances()
	return None


def _is_allowed_instance(problem_name: str, instance: dict[str, Any]) -> bool:
	if problem_name == "conway":
		return instance == {}
	if problem_name == "hadamard":
		return instance.get("n") in HADAMARD_ALLOWED_N
	if problem_name == "stilllife":
		return instance.get("n") in STILLLIFE_ALLOWED_N
	if problem_name == "tensor":
		size = (instance.get("n"), instance.get("m"), instance.get("p"))
		return size in TENSOR_ALLOWED_SIZES
	if problem_name == "hpprotein":
		sequence_id = instance.get("sequence_id")
		allowed = {
			item.get("sequence_id")
			for item in hpprotein_instances()
			if isinstance(item, dict)
		}
		return sequence_id in allowed
	return False


def _verify_submission(problem_name: str, instance: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
	if problem_name == "hadamard":
		return verify_hadamard(instance, submission, current_record=hadamard_record(instance.get("n")))
	if problem_name == "conway":
		return verify_conway(instance, submission, current_record_score=0.0)
	if problem_name == "tensor":
		return verify_tensor(
			instance,
			submission,
			current_record=tensor_record(instance.get("n"), instance.get("m"), instance.get("p")),
		)
	if problem_name == "stilllife":
		return verify_stilllife(instance, submission, current_record=stilllife_record(instance.get("n")))
	if problem_name == "hpprotein":
		return verify_hpprotein(
			instance,
			submission,
			current_record=hpprotein_record(str(instance.get("sequence_id", ""))),
		)
	return {
		"is_valid": False,
		"error_code": "PROBLEM_NOT_FOUND",
		"error_message": f"Unknown problem_name: {problem_name}",
	}


def _score_direction_for_problem(problem_name: str) -> str:
	if problem_name in LOWER_SCORE_BETTER_PROBLEMS:
		return "low"
	return "high"



router = APIRouter(prefix="/api/v1", tags=["Verifier API v1"])
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
	return HealthResponse(
		status="healthy",
		timestamp=_iso_utc(_utc_now()),
		version=API_VERSION,
	)


@router.get(
	"/problems/{problem_name}/instances",
	response_model=ProblemInstancesResponse,
	responses={404: {"model": ErrorResponse}},
)
async def list_problem_instances(problem_name: str) -> ProblemInstancesResponse | JSONResponse:
	instances = _get_problem_instances(problem_name)
	if instances is None:
		return _json_error(
			status_code=404,
			error_code="PROBLEM_NOT_FOUND",
			message=f"Unknown problem_name: {problem_name}",
		)
	return ProblemInstancesResponse(problem_name=problem_name, instances=instances)


@router.post(
	"/submit",
	response_model=SubmitSuccessResponse,
	responses={
		400: {"model": SubmitFailureResponse},
		404: {"model": ErrorResponse},
		408: {"model": ErrorResponse},
		413: {"model": ErrorResponse},
		429: {"model": ErrorResponse},
	},
)
async def submit(submit_payload: SubmitRequest, request: Request, db: db_dependency) -> SubmitSuccessResponse | JSONResponse:
	raw_body = await request.body()

	email = submit_payload.email
	problem_name = submit_payload.problem_name
	instance = submit_payload.instance
	submission = submit_payload.submission

	if not _is_valid_email(email):
		return _json_error(400, "INVALID_EMAIL", "Invalid email format", field="email")

	if problem_name not in PROBLEM_TIMEOUTS:
		return _json_error(404, "PROBLEM_NOT_FOUND", f"Unknown problem_name: {problem_name}")

	if not isinstance(instance, dict):
		return _json_error(400, "INVALID_FORMAT", "instance must be an object", field="instance")
	if not isinstance(submission, dict):
		return _json_error(400, "INVALID_FORMAT", "submission must be an object", field="submission")

	max_payload = PROBLEM_MAX_PAYLOAD_BYTES[problem_name]
	if len(raw_body) > max_payload:
		return _json_error(
			413,
			"SIZE_LIMIT_EXCEEDED",
			f"Payload exceeds maximum size for problem {problem_name}",
			max_bytes=max_payload,
		)

	normalized_instance = _normalize_instance(problem_name, instance)
	client_ip = _extract_client_ip(request)

	allowed, message, retry_after = await _check_rate_limit(db, client_ip, problem_name)
	if not allowed:
		response = _json_error(
			429,
			"RATE_LIMITED",
			message or "Rate limit exceeded",
			retry_after_seconds=retry_after,
		)
		if retry_after is not None:
			response.headers["Retry-After"] = str(retry_after)
		return response

	try:
		verifier_result = await asyncio.wait_for(
			asyncio.to_thread(_verify_submission, problem_name, normalized_instance, submission),
			timeout=PROBLEM_TIMEOUTS[problem_name],
		)
	except asyncio.TimeoutError:
		record = Submission(
			email=email,
			ip_address=client_ip,
			problem_name=problem_name,
			instance=normalized_instance,
			submission=submission,
			is_valid=False,
			score=None,
			score_direction=_score_direction_for_problem(problem_name),
			error_message="Verification timeout",
			percentile=None,
			is_record=False,
		)
		db.add(record)
		await db.commit()
		await _recompute_instance_percentiles(db, problem_name, normalized_instance)
		return _json_error(408, "TIMEOUT", "Verification exceeded the allowed time limit")

	is_valid = bool(verifier_result.get("is_valid"))
	score = verifier_result.get("score")
	is_record = bool(verifier_result.get("is_record", False))
	error_message = verifier_result.get("error_message")
	score_direction = _score_direction_for_problem(problem_name)
	if (not is_valid) and score is None:
		score = None

	record = Submission(
		email=email,
		ip_address=client_ip,
		problem_name=problem_name,
		instance=normalized_instance,
		submission=submission,
		is_valid=is_valid,
		score=score,
		score_direction=score_direction,
		error_message=error_message,
		percentile=None,
		is_record=is_record,
	)
	db.add(record)
	await db.commit()
	await db.refresh(record)
	await _recompute_instance_percentiles(db, problem_name, normalized_instance)
	await db.refresh(record)

	if is_valid:
		percentile = _to_json_number(record.percentile)

		return SubmitSuccessResponse(
			success=True,
			submission_id=str(record.submission_id),
			problem_name=problem_name,
			instance=normalized_instance,
			score=_to_json_number(score),
			percentile=percentile,
			is_record=is_record,
			message=verifier_result.get("message", "Verification passed"),
		)

	error_code = verifier_result.get("error_code") or "VERIFICATION_FAILED"
	details = verifier_result.get("error_details")
	response = SubmitFailureResponse(
		success=False,
		error_code=error_code,
		message=error_message or "Verification failed",
	)
	if details is not None:
		response.details = details
	return JSONResponse(status_code=400, content=response.model_dump(exclude_none=True))


@router.get(
	"/submission/{submission_id}",
	response_model=SubmissionResponse,
	responses={404: {"model": ErrorResponse}},
)
async def get_submission(submission_id: UUID, db: db_dependency) -> SubmissionResponse | JSONResponse:
	stmt = select(Submission).where(Submission.submission_id == submission_id)
	result = await db.execute(stmt)
	submission = result.scalar_one_or_none()

	if submission is None:
		return _json_error(404, "NOT_FOUND", "Submission not found")

	percentile = None
	if submission.is_valid and submission.score is not None:
		percentile = await _compute_percentile(
			db,
			problem_name=submission.problem_name,
			instance=submission.instance,
			score=submission.score,
			score_direction=submission.score_direction,
			submission_id=submission.submission_id,
		)

	return SubmissionResponse(
		submission_id=str(submission.submission_id),
		created_at=_iso_utc(submission.created_at),
		problem_name=submission.problem_name,
		instance=submission.instance,
		is_valid=submission.is_valid,
		score=_to_json_number(submission.score),
		percentile=percentile,
		is_record=submission.is_record,
	)


@router.post(
	"/leaderboard",
	response_model=LeaderboardResponse,
	responses={
		400: {"model": ErrorResponse},
		401: {"model": ErrorResponse},
		404: {"model": ErrorResponse},
	},
)
async def get_leaderboard(
	leaderboard_request: LeaderboardRequest,
	request: Request,
	db: db_dependency,
) -> LeaderboardResponse | JSONResponse:
	provided_password = request.headers.get("X-Leaderboard-Password")
	expected_password = LEADERBOARD_PASSWORD or ""
	if (not provided_password) or (not compare_digest(provided_password, expected_password)):
		return _json_error(401, "UNAUTHORIZED", "Invalid leaderboard password")

	problem_name = leaderboard_request.problem_name
	if problem_name not in PROBLEM_TIMEOUTS:
		return _json_error(404, "PROBLEM_NOT_FOUND", f"Unknown problem_name: {problem_name}")

	instance = leaderboard_request.instance
	if not isinstance(instance, dict):
		return _json_error(400, "INVALID_FORMAT", "instance must be an object", field="instance")

	normalized_instance = _normalize_instance(problem_name, instance)
	if not _is_allowed_instance(problem_name, normalized_instance):
		return _json_error(
			400,
			"INVALID_INSTANCE",
			"Invalid instance for specified problem",
			instance=normalized_instance,
		)

	k = _as_int(leaderboard_request.k, 10)
	if k < 1 or k > 200:
		return _json_error(400, "INVALID_K", "k must be between 1 and 200", field="k")

	if _score_direction_for_problem(problem_name) == "low":
		order_clause = (Submission.score.asc(), Submission.created_at.asc(), Submission.submission_id.asc())
	else:
		order_clause = (Submission.score.desc(), Submission.created_at.asc(), Submission.submission_id.asc())

	stmt = (
		select(Submission)
		.where(
			Submission.problem_name == problem_name,
			Submission.instance == normalized_instance,
			Submission.is_valid.is_(True),
			Submission.score.is_not(None),
		)
		.order_by(*order_clause)
		.limit(k)
	)
	result = await db.execute(stmt)
	rows = result.scalars().all()

	entries = [
		LeaderboardEntryResponse(
			submission_id=str(row.submission_id),
			created_at=_iso_utc(row.created_at),
			email=row.email,
			ip_address=row.ip_address,
			problem_name=row.problem_name,
			instance=row.instance,
			submission=row.submission,
			is_valid=row.is_valid,
			score=_to_json_number(row.score),
			score_direction=row.score_direction,
			error_message=row.error_message,
			percentile=_to_json_number(row.percentile),
			is_record=row.is_record,
		)
		for row in rows
	]

	return LeaderboardResponse(
		success=True,
		problem_name=problem_name,
		instance=normalized_instance,
		k=k,
		returned=len(entries),
		entries=entries,
	)
