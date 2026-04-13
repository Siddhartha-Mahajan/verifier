"""
Matrix Multiplication Tensor Rank -- Verification Module

A bilinear algorithm for multiplying an (n x m) matrix by an (m x p) matrix
is defined by a tensor decomposition into R rank-1 terms.  Each term t has
three coefficient matrices: U[t] (n x m), V[t] (m x p), W[t] (n x p).

For input matrices A (n x m) and B (m x p), the algorithm computes:
    s_t = (sum of U[t] * A element-wise) * (sum of V[t] * B element-wise)
    C   = sum over t of  s_t * W[t]

where * between scalars is ordinary multiplication, and C should equal A @ B.

Verification: run on 100 random integer matrix pairs, check exact equality.
Score = R (num_multiplications), lower is better.
"""

from typing import Dict, Any, List, Optional, Union
from fractions import Fraction
import hashlib
import secrets

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_SIZES = [
    (2, 2, 2), (2, 2, 3), (2, 3, 3), (2, 3, 4), (2, 4, 5),
    (3, 3, 3), (3, 3, 4), (3, 3, 6),
    (4, 4, 4), (4, 4, 5),
    (5, 5, 5),
]

CURRENT_RECORDS: Dict[str, int] = {
    "2,2,2": 7,
    "2,2,3": 11,
    "2,3,3": 15,
    "2,3,4": 20,
    "2,4,5": 32,
    "3,3,3": 23,
    "3,3,4": 29,
    "3,3,6": 40,
    "4,4,4": 48,
    "4,4,5": 61,
    "5,5,5": 93,
}

NUM_TESTS = 100
ENTRY_RANGE = 10   # random entries in [-ENTRY_RANGE, ENTRY_RANGE]
TIMEOUT_SECONDS = 30

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_coefficient(val: Any) -> Fraction:
    """
    Parse a coefficient into an exact Fraction.
    Accepts: int, or string like "1/2", "-3/4", "7".
    Rejects: float, anything else.
    """
    if isinstance(val, int):
        return Fraction(val)
    if isinstance(val, str):
        try:
            return Fraction(val)
        except (ValueError, ZeroDivisionError):
            raise ValueError(f"Cannot parse coefficient: {val!r}")
    raise ValueError(
        f"Coefficient must be int or rational string (e.g. '1/2'), got {type(val).__name__}: {val!r}"
    )


def _parse_matrix(data: Any, rows: int, cols: int, label: str) -> List[List[Fraction]]:
    """Parse a 2D list into a rows x cols Fraction matrix."""
    if not isinstance(data, list) or len(data) != rows:
        raise ValueError(f"{label}: expected {rows} rows, got {len(data) if isinstance(data, list) else 'not a list'}")
    result = []
    for i, row in enumerate(data):
        if not isinstance(row, list) or len(row) != cols:
            raise ValueError(
                f"{label} row {i}: expected {cols} elements, got "
                f"{'not a list' if not isinstance(row, list) else f'{len(row)} elements'}"
            )
        result.append([_parse_coefficient(v) for v in row])
    return result


def _mat_element_sum(coeff: List[List[Fraction]], mat: List[List[int]]) -> Fraction:
    """Compute sum of coeff[i][j] * mat[i][j] over all i, j."""
    s = Fraction(0)
    for i in range(len(coeff)):
        for j in range(len(coeff[0])):
            if coeff[i][j] != 0:
                s += coeff[i][j] * mat[i][j]
    return s


def _standard_multiply(A: List[List[int]], B: List[List[int]], n: int, m: int, p: int) -> List[List[int]]:
    """Standard matrix multiplication A (n x m) @ B (m x p) -> C (n x p)."""
    C = [[0] * p for _ in range(n)]
    for i in range(n):
        for k in range(m):
            if A[i][k] == 0:
                continue
            for j in range(p):
                C[i][j] += A[i][k] * B[k][j]
    return C


def _random_test_matrices(n: int, m: int, p: int, seed_str: Optional[str] = None):
    """
    Generate NUM_TESTS pairs of random integer matrices.
    If seed_str is provided, test cases are reproducible for that seed.
    If not provided, a random seed is generated.
    Yields (A, B) pairs where A is n x m and B is m x p.
    """
    import random
    if seed_str is None:
        seed_str = secrets.token_hex(16)
    rng = random.Random(hashlib.sha256(seed_str.encode()).hexdigest())
    for _ in range(NUM_TESTS):
        A = [[rng.randint(-ENTRY_RANGE, ENTRY_RANGE) for _ in range(m)] for _ in range(n)]
        B = [[rng.randint(-ENTRY_RANGE, ENTRY_RANGE) for _ in range(p)] for _ in range(m)]
        yield A, B


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_allowed_size(n: int, m: int, p: int) -> bool:
    return (n, m, p) in ALLOWED_SIZES


def get_record(n: int, m: int, p: int) -> Optional[int]:
    return CURRENT_RECORDS.get(f"{n},{m},{p}")


def verify(
    instance: Dict[str, Any],
    submission: Dict[str, Any],
    current_record: Optional[int] = None,
    seed_str: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify a tensor decomposition for matrix multiplication.

    Args:
        instance: {"n": int, "m": int, "p": int}
        submission: {"num_multiplications": int, "U": [...], "V": [...], "W": [...]}
        current_record: best known R for this size (None if unknown)
        seed_str: optional seed for random test matrices (use submission_id for reproducibility)

    Returns dict with: is_valid, score, error_code, error_message,
                       error_details, is_record, tests_passed
    """
    result: Dict[str, Any] = {
        "is_valid": False,
        "score": None,
        "error_code": None,
        "error_message": None,
        "error_details": None,
        "is_record": False,
        "tests_passed": 0,
    }

    # -- instance validation --
    for field in ("n", "m", "p"):
        if field not in instance:
            result["error_code"] = "MISSING_FIELD"
            result["error_message"] = f"instance must contain '{field}'"
            return result

    try:
        n, m, p = int(instance["n"]), int(instance["m"]), int(instance["p"])
    except (ValueError, TypeError):
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "instance n, m, p must be integers"
        return result

    if (n, m, p) not in ALLOWED_SIZES:
        result["error_code"] = "INVALID_INSTANCE"
        result["error_message"] = f"Size ({n},{m},{p}) is not in the allowed list"
        return result

    # -- submission field checks --
    if "num_multiplications" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'num_multiplications'"
        return result

    try:
        R = int(submission["num_multiplications"])
    except (ValueError, TypeError):
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "num_multiplications must be an integer"
        return result

    if R <= 0:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "num_multiplications must be positive"
        return result

    for field in ("U", "V", "W"):
        if field not in submission:
            result["error_code"] = "MISSING_FIELD"
            result["error_message"] = f"submission must contain '{field}'"
            return result

    raw_U, raw_V, raw_W = submission["U"], submission["V"], submission["W"]

    for name, data in [("U", raw_U), ("V", raw_V), ("W", raw_W)]:
        if not isinstance(data, list) or len(data) != R:
            result["error_code"] = "INVALID_FORMAT"
            result["error_message"] = f"{name} must be a list of {R} matrices, got {len(data) if isinstance(data, list) else 'not a list'}"
            return result

    # -- parse coefficients as exact rationals --
    try:
        U = [_parse_matrix(raw_U[t], n, m, f"U[{t}]") for t in range(R)]
        V = [_parse_matrix(raw_V[t], m, p, f"V[{t}]") for t in range(R)]
        W = [_parse_matrix(raw_W[t], n, p, f"W[{t}]") for t in range(R)]
    except ValueError as e:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(e)
        return result

    # -- test on random matrix pairs --
    tests_passed = 0
    first_failure = None

    for test_idx, (A, B) in enumerate(_random_test_matrices(n, m, p, seed_str)):
        expected = _standard_multiply(A, B, n, m, p)

        # Run the submitted algorithm
        C = [[Fraction(0)] * p for _ in range(n)]
        for t in range(R):
            s = _mat_element_sum(U[t], A) * _mat_element_sum(V[t], B)
            for i in range(n):
                for j in range(p):
                    C[i][j] += s * W[t][i][j]

        # Check exact equality
        ok = True
        for i in range(n):
            for j in range(p):
                if C[i][j] != expected[i][j]:
                    ok = False
                    if first_failure is None:
                        first_failure = {
                            "test": test_idx,
                            "position": (i, j),
                            "expected": int(expected[i][j]),
                            "got": str(C[i][j]),
                        }
                    break
            if not ok:
                break

        if ok:
            tests_passed += 1

    result["tests_passed"] = tests_passed

    if tests_passed < NUM_TESTS:
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = (
            f"Algorithm produced wrong output on {NUM_TESTS - tests_passed} of {NUM_TESTS} test cases"
        )
        result["error_details"] = first_failure
        return result

    # -- success --
    result["is_valid"] = True
    result["score"] = R

    if current_record is not None and R < current_record:
        result["is_record"] = True

    return result
