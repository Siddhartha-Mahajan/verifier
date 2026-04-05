"""
Conway's 99-Graph -- Verification Module

Find a strongly regular graph srg(99, 14, 1, 2):
  - 99 vertices, each with degree 14
  - Every adjacent pair shares exactly 1 common neighbor (lambda = 1)
  - Every non-adjacent pair shares exactly 2 common neighbors (mu = 2)

Scoring: percentage of constraints satisfied (0-100).
  - 99 degree constraints + 4851 pair constraints = 4950 total.
  - Partial solutions are accepted and scored.
  - 100.0 means the graph is found.

A submission is valid (gets a score) as long as the matrix passes
structural checks (99x99, symmetric, binary, zero diagonal).
"""

from typing import Dict, Any

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N = 99
DEGREE = 14
LAMBDA = 1
MU = 2
TOTAL_PAIRS = N * (N - 1) // 2          # 4851
TOTAL_CONSTRAINTS = N + TOTAL_PAIRS      # 4950
TIMEOUT_SECONDS = 10

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_structure(matrix: Any) -> np.ndarray:
    """
    Validate that matrix is 99x99, symmetric, binary, zero-diagonal.
    Returns numpy int64 array.
    Raises ValueError on any structural failure.
    """
    if not isinstance(matrix, list) or len(matrix) != N:
        raise ValueError(f"Matrix must be {N}x{N}, got {len(matrix) if isinstance(matrix, list) else 'not a list'} rows")

    for i, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != N:
            raise ValueError(
                f"Row {i}: expected list of {N} elements, got "
                f"{'not a list' if not isinstance(row, list) else f'{len(row)} elements'}"
            )

    arr = np.array(matrix, dtype=np.int64)

    # Binary check
    bad = np.argwhere((arr != 0) & (arr != 1))
    if len(bad) > 0:
        i, j = int(bad[0][0]), int(bad[0][1])
        raise ValueError(f"Entry ({i},{j}) must be 0 or 1, got {arr[i,j]}")

    # Zero diagonal
    diag_bad = np.where(np.diag(arr) != 0)[0]
    if len(diag_bad) > 0:
        raise ValueError(f"Diagonal must be all zeros. Non-zero at vertex {int(diag_bad[0])}")

    # Symmetry
    if not np.array_equal(arr, arr.T):
        diff = np.argwhere(arr != arr.T)
        i, j = int(diff[0][0]), int(diff[0][1])
        raise ValueError(f"Matrix must be symmetric: A[{i},{j}]={arr[i,j]} but A[{j},{i}]={arr[j,i]}")

    return arr


def _score_constraints(arr: np.ndarray) -> Dict[str, Any]:
    """
    Count how many of the 4950 constraints are satisfied.
    Returns a report dict.
    """
    # Degree constraints (99 of them)
    degrees = arr.sum(axis=1)
    degree_ok = int(np.sum(degrees == DEGREE))
    degree_violations = [
        {"vertex": int(v), "degree": int(degrees[v])}
        for v in np.where(degrees != DEGREE)[0][:20]
    ]

    # Pair constraints via A-squared
    A2 = arr @ arr

    # Edges: A[i,j]=1 means A2[i,j] should be LAMBDA
    # Non-edges (i!=j, A[i,j]=0) means A2[i,j] should be MU
    lambda_ok = 0
    lambda_violations = []
    mu_ok = 0
    mu_violations = []

    for i in range(N):
        for j in range(i + 1, N):
            common = int(A2[i, j])
            if arr[i, j] == 1:
                if common == LAMBDA:
                    lambda_ok += 1
                elif len(lambda_violations) < 20:
                    lambda_violations.append({"edge": (i, j), "expected": LAMBDA, "got": common})
            else:
                if common == MU:
                    mu_ok += 1
                elif len(mu_violations) < 20:
                    mu_violations.append({"pair": (i, j), "expected": MU, "got": common})

    edge_count = int(arr.sum()) // 2
    nonedge_count = TOTAL_PAIRS - edge_count
    lambda_fail = edge_count - lambda_ok
    mu_fail = nonedge_count - mu_ok

    satisfied = degree_ok + lambda_ok + mu_ok
    score = (satisfied / TOTAL_CONSTRAINTS) * 100

    return {
        "satisfied": satisfied,
        "total": TOTAL_CONSTRAINTS,
        "score": round(score, 4),
        "degree": {
            "satisfied": degree_ok,
            "total": N,
            "violations": degree_violations,
        },
        "lambda": {
            "satisfied": lambda_ok,
            "failed": lambda_fail,
            "total": edge_count,
            "violations": lambda_violations,
        },
        "mu": {
            "satisfied": mu_ok,
            "failed": mu_fail,
            "total": nonedge_count,
            "violations": mu_violations,
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify(
    instance: Dict[str, Any],
    submission: Dict[str, Any],
    current_record_score: float = 0.0,
) -> Dict[str, Any]:
    """
    Verify a Conway's 99-Graph submission.

    Args:
        instance: {} (ignored, problem is fixed)
        submission: {"matrix": [[0,1,...], ...]}
        current_record_score: best constraint-satisfaction % seen so far

    Returns dict with: is_valid, score, error_code, error_message,
                       error_details, constraint_report, is_record, is_perfect
    """
    result: Dict[str, Any] = {
        "is_valid": False,
        "score": None,
        "error_code": None,
        "error_message": None,
        "error_details": None,
        "constraint_report": None,
        "is_record": False,
        "is_perfect": False,
    }

    if "matrix" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'matrix'"
        return result

    # Structural validation (shape, binary, symmetric, zero diagonal)
    try:
        arr = _validate_structure(submission["matrix"])
    except ValueError as e:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(e)
        return result

    # If structure is valid, score the constraints.
    # Partial solutions are accepted.
    report = _score_constraints(arr)
    result["is_valid"] = True
    result["score"] = report["score"]
    result["constraint_report"] = report

    if report["satisfied"] == report["total"]:
        result["is_perfect"] = True

    if report["score"] > current_record_score:
        result["is_record"] = True

    # Add a human-readable message
    result["error_message"] = None
    msg = f"{report['satisfied']} of {report['total']} constraints satisfied"
    if result["is_perfect"]:
        result["message"] = f"Perfect solution found. {msg}."
    else:
        result["message"] = msg

    return result
