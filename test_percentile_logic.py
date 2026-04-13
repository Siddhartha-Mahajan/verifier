from types import SimpleNamespace
from uuid import uuid4

from routers.api_v1 import _calculate_percentile_map


def _submission(score: int | float | None, is_valid: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        submission_id=uuid4(),
        is_valid=is_valid,
        score=score,
    )


def test_higher_is_better_best_ties_get_100_and_invalid_excluded() -> None:
    s1 = _submission(10, True)
    s2 = _submission(10, True)
    s3 = _submission(8, True)
    s4 = _submission(None, False)

    percentile_map = _calculate_percentile_map("stilllife", [s1, s2, s3, s4])

    assert percentile_map[s1.submission_id] == 100.0
    assert percentile_map[s2.submission_id] == 100.0
    assert percentile_map[s3.submission_id] == 33.3333
    assert s4.submission_id not in percentile_map


def test_lower_is_better_best_ties_get_100() -> None:
    s1 = _submission(7, True)
    s2 = _submission(7, True)
    s3 = _submission(9, True)

    percentile_map = _calculate_percentile_map("tensor", [s1, s2, s3])

    assert percentile_map[s1.submission_id] == 100.0
    assert percentile_map[s2.submission_id] == 100.0
    assert percentile_map[s3.submission_id] == 33.3333


def test_valid_only_denominator() -> None:
    s1 = _submission(10, True)
    s2 = _submission(8, True)
    s3 = _submission(999, False)

    percentile_map = _calculate_percentile_map("hadamard", [s1, s2, s3])

    assert percentile_map[s1.submission_id] == 100.0
    assert percentile_map[s2.submission_id] == 50.0
    assert s3.submission_id not in percentile_map
