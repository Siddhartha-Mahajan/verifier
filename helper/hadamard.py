"""
Hadamard Maximal Determinant -- Verification Module

Given an n x n matrix with entries +1 or -1, verify that the claimed
determinant matches the actual determinant. Score = percentage of the
theoretical determinant bound for the given n (higher is better).

Verification:
  1. n is in the allowed list
  2. Matrix is square n x n
  3. Every entry is exactly +1 or -1
  4. Exact integer determinant computed via sympy
  5. |det| == claimed_det
"""

from decimal import Decimal, localcontext
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
CURRENT_RECORDS: Dict[int, int] = {
    23: 2779447296000000,
    27: 13293406466724593664,
    29: 1188957517256767569920,
    31: 81562485683814255296512,
    33: 8330254475782054156959744,
    34: 77371252455336267181195264,
    35: 643148536034982720943685632,
    39: 6601231871033942749550047395840,
    45: 11586605067716613057778332690823512064,
    47: 1188404862211877937953272796440166400000,
    53: 3336820778920401326051559490739795041651261440,
    63: 301544826499080300175294464000000000000000000000000000000,
    67: 8411937322623226705059250176000000000000000000000000000000000,
    69: 1841559726932497391068193644892508058646701259493290992111452160,
    73: 70671875153440590676763519679804730029991902842347514447013429116928,
    75: 11619252818798818304359179223040000000000000000000000000000000000000000,
    77: 2848485384514909987228371683783391053834432432133638731675260616842412032,
    79: 507628599035959194093046357557248000000000000000000000000000000000000000000,
    83: 24521826048842101677073289227272192000000000000000000000000000000000000000000000,
    87: 1303760429915618477835427465176023040000000000000000000000000000000000000000000000000,
    91: 76068505561747875249092216679364034560000000000000000000000000000000000000000000000000000,
    93: 22434176008231870683469640496687296814730821989127842710796075781171503140772894367067144192,
    95: 4830318118464677460375777979471075737600000000000000000000000000000000000000000000000000000000,
    99: 337731524395589406897742022272511334022965678835094355779271284764343191867786606928894941521248256,
}

TIMEOUT_SECONDS = 60
SCORE_DECIMALS = Decimal("0.0001")

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


def _pow_half_integer(base: Decimal, exponent_numer: int) -> Decimal:
    """
    Compute base^(exponent_numer/2) exactly enough for scoring.

    exponent_numer is a non-negative integer.
    """
    if exponent_numer < 0:
        raise ValueError("exponent_numer must be non-negative")
    result = base ** (exponent_numer // 2)
    if exponent_numer % 2:
        result *= base.sqrt()
    return result


def _ehlich_s_candidates(n: int) -> tuple[int, ...]:
    """Block-count candidates s for Ehlich's n % 4 == 3 bound."""
    if n == 3:
        return (3,)
    if n == 7:
        return (5,)
    if n == 11:
        return (5, 6)
    if 15 <= n <= 59:
        return (6,)
    if n >= 63:
        return (7,)
    raise ValueError(f"No Ehlich s-candidate rule for n={n}")


def _ehlich_bound_mod3(n: int) -> Decimal:
    """
    Ehlich's bound for n % 4 == 3, using the block formulation:

    det(R) <= (n-3)^((n-s)/2) (n-3+4r)^(u/2) (n+1+4r)^(v/2)
              * sqrt(1 - ur/(n-3+4r) - v(r+1)/(n+1+4r))

    where r=floor(n/s), v=n-rs, u=s-v.
    For n=11 there are two s options; the tighter bound is used.
    """
    candidates: list[Decimal] = []
    for s in _ehlich_s_candidates(n):
        r = n // s
        v = n - r * s
        u = s - v

        n_minus_3 = Decimal(n - 3)
        a = Decimal(n - 3 + 4 * r)
        b = Decimal(n + 1 + 4 * r)
        tail = Decimal(1) - (Decimal(u * r) / a) - (Decimal(v * (r + 1)) / b)
        if tail <= 0:
            continue

        bound = (
            _pow_half_integer(n_minus_3, n - s)
            * _pow_half_integer(a, u)
            * _pow_half_integer(b, v)
            * tail.sqrt()
        )
        candidates.append(bound)

    if not candidates:
        raise RuntimeError(f"Could not compute Ehlich bound for n={n}")
    return min(candidates)


def get_theoretical_bound(n: int) -> Decimal:
    """Return the theoretical determinant upper bound for the given n."""
    if n <= 0:
        raise ValueError("n must be positive")

    with localcontext() as ctx:
        # Enough precision for n <= 99 and robust 4-decimal score reporting.
        ctx.prec = 160
        mod4 = n % 4
        if mod4 == 0:
            return Decimal(n) ** (n // 2)
        if mod4 == 1:
            return Decimal(2 * n - 1).sqrt() * (Decimal(n - 1) ** ((n - 1) // 2))
        if mod4 == 2:
            return Decimal(2 * n - 2) * (Decimal(n - 2) ** ((n - 2) // 2))
        return _ehlich_bound_mod3(n)


def _bound_ratio_percent(abs_det: int, n: int) -> float:
    """Score as 100 * |det| / bound(n), rounded to 4 decimals."""
    with localcontext() as ctx:
        ctx.prec = 80
        bound = get_theoretical_bound(n)
        ratio = (Decimal(abs_det) * Decimal(100)) / bound
        if ratio < 0:
            ratio = Decimal(0)
        return float(ratio.quantize(SCORE_DECIMALS))


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
    result["score"] = _bound_ratio_percent(abs_det, n)

    if current_record is not None and abs_det > current_record:
        result["is_record"] = True

    return result
