from typing import Any, Literal

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error_code: str
    message: str
    field: str | None = None
    details: Any | None = None
    retry_after_seconds: int | None = None
    max_bytes: int | None = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class ProblemInstancesResponse(BaseModel):
    problem_name: str
    instances: list[dict[str, Any]]


class SubmitRequest(BaseModel):
    email: str
    problem_name: str
    instance: dict[str, Any]
    submission: dict[str, Any]


class SubmitSuccessResponse(BaseModel):
    success: Literal[True] = True
    submission_id: str
    problem_name: str
    instance: dict[str, Any]
    score: int | float | None = None
    percentile: float | None = None
    is_record: bool
    message: str


class SubmitFailureResponse(BaseModel):
    success: Literal[False] = False
    error_code: str
    message: str
    details: Any | None = None


class SubmissionResponse(BaseModel):
    submission_id: str
    created_at: str
    problem_name: str
    instance: dict[str, Any]
    is_valid: bool
    score: int | float | None = None
    percentile: float | None = None
    is_record: bool


class LeaderboardRequest(BaseModel):
    problem_name: str
    instance: dict[str, Any]
    k: int = 10


class LeaderboardEntryResponse(BaseModel):
    submission_id: str
    created_at: str
    email: str
    ip_address: str
    problem_name: str
    instance: dict[str, Any]
    is_valid: bool
    score: int | float | None = None
    score_direction: str
    error_message: str | None = None
    percentile: float | None = None
    is_record: bool


class LeaderboardResponse(BaseModel):
    success: Literal[True] = True
    problem_name: str
    instance: dict[str, Any]
    k: int
    returned: int
    entries: list[LeaderboardEntryResponse]
