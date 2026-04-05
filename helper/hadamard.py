"""
Hadamard Maximal Determinant -- Verification Module

Given an n x n matrix with entries +1 or -1, verify that the claimed
determinant matches the actual determinant.  Score = |det| (higher is better).

Verification:
  1. n is in the allowed list
  2. Matrix is square n x n
  3. Every entry is exactly +1 or -1
  4. Exact integer determinant computed via sympy
  5. |det| == claimed_det
"""

from typing import Dict, Any, Optional

try:
    from sympy import Matrix as SympyMatrix
except ImportError:
    raise ImportError(
        "sympy is required for Hadamard verification. Install with: pip install sympy"
    )

# ---------------------------------------------------------------------------
# Allowed instances and current records (Orrick et al. 2003, arXiv:math/0304410)
# ---------------------------------------------------------------------------

ALLOWED_N = [
    23, 27, 29, 31, 33, 34, 35, 39, 45, 47,
    53, 63, 67, 69, 73, 75, 77, 79, 83, 87,
    91, 93, 95, 99,
]

# Best known |det| for each n.  None means no factored form is published.
CURRENT_RECORDS: Dict[int, Optional[int]] = {
    23: 2779447296000000,
    27: None,
    29: 6240837824260096,
    31: 5883288963353600,
    33: 229160936893272576,
    34: 15474242441455104,
    35: 499608912746737664,
    39: 587797550817388672,
    45: None,
    47: None,
    53: None,
    63: None,
    67: None,
    69: None,
    73: None,
    75: None,
    77: None,
    79: None,
    83: None,
    87: None,
    91: None,
    93: None,
    95: None,
    99: None,
}

TIMEOUT_SECONDS = 60

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _coerce_int(val: Any) -> int:
    """Coerce a value to int.  Accepts int or float with no fractional part."""
    if isinstance(val, int):
        return val
    if isinstance(val, float) and val == int(val):
        return int(val)
    raise ValueError(f"Expected integer, got {type(val).__name__}: {val!r}")


def _validate_matrix(matrix: Any, n: int) -> list:
    """Validate shape and entries.  Returns matrix as list of lists of int."""
    if not isinstance(matrix, list) or len(matrix) == 0:
        raise ValueError("matrix must be a non-empty list of lists")
    if len(matrix) != n:
        raise ValueError(f"Matrix must be {n}x{n}, got {len(matrix)} rows")

    coerced = []
    for i, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(
                f"Row {i}: expected list of {n} elements, got "
                f"{'not a list' if not isinstance(row, list) else f'{len(row)} elements'}"
            )
        coerced_row = []
        for j, val in enumerate(row):
            try:
                v = _coerce_int(val)
            except ValueError:
                raise ValueError(f"Entry ({i},{j}): expected +1 or -1, got {val!r}")
            if v not in (1, -1):
                raise ValueError(f"Entry ({i},{j}): expected +1 or -1, got {v}")
            coerced_row.append(v)
        coerced.append(coerced_row)
    return coerced


def _exact_determinant(matrix: list) -> int:
    """Compute the exact integer determinant using sympy."""
    return int(SympyMatrix(matrix).det())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_allowed_n(n: int) -> bool:
    return n in ALLOWED_N


def get_record(n: int) -> Optional[int]:
    return CURRENT_RECORDS.get(n)


def verify(
    instance: Dict[str, Any],
    submission: Dict[str, Any],
    current_record: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Verify a Hadamard submission.

    Args:
        instance:  {"n": <int>}
        submission: {"claimed_det": <int>, "matrix": [[...]]}
        current_record: best known |det| for this n (None if unknown)

    Returns dict with: is_valid, score, error_code, error_message,
                       error_details, is_record, computed_det
    """
    result: Dict[str, Any] = {
        "is_valid": False,
        "score": None,
        "error_code": None,
        "error_message": None,
        "error_details": None,
        "is_record": False,
        "computed_det": None,
    }

    # -- instance validation --
    if "n" not in instance:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "instance must contain 'n'"
        return result

    try:
        n = _coerce_int(instance["n"])
    except ValueError:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = f"instance.n must be an integer, got {instance['n']!r}"
        return result

    if n not in ALLOWED_N:
        result["error_code"] = "INVALID_INSTANCE"
        result["error_message"] = f"n={n} is not in the allowed list"
        return result

    # -- submission field checks --
    if "claimed_det" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'claimed_det'"
        return result

    try:
        claimed_det = _coerce_int(submission["claimed_det"])
    except ValueError:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "claimed_det must be a positive integer"
        return result

    if claimed_det <= 0:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "claimed_det must be positive"
        return result

    if "matrix" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'matrix'"
        return result

    # -- matrix validation --
    try:
        matrix = _validate_matrix(submission["matrix"], n)
    except ValueError as e:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(e)
        return result

    # -- determinant computation --
    try:
        det = _exact_determinant(matrix)
    except Exception as e:
        result["error_code"] = "VERIFICATION_ERROR"
        result["error_message"] = f"Determinant computation failed: {e}"
        return result

    result["computed_det"] = det
    abs_det = abs(det)

    if abs_det != claimed_det:
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = (
            f"Claimed determinant {claimed_det} does not match computed |det| = {abs_det}"
        )
        result["error_details"] = {
            "claimed_det": claimed_det,
            "computed_det": abs_det,
        }
        return result

    # -- success --
    result["is_valid"] = True
    result["score"] = abs_det

    if current_record is not None and abs_det > current_record:
        result["is_record"] = True

    return result
