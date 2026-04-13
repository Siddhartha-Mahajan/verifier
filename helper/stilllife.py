"""
Connected Still Life -- Verification Module

A still life in Conway's Game of Life is a pattern that is stable:
  - Every live cell has exactly 2 or 3 live neighbors (survival).
  - No dead cell has exactly 3 live neighbors (no births).

A connected still life further requires all live cells to form a
single 8-connected component.

Score = number of live cells (higher is better).
"""

from typing import Dict, Any, Optional, List, Tuple
from collections import deque

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_N = [8, 10, 16, 20, 32]

# Records are intentionally unset until independently verified.
CURRENT_RECORDS: Dict[int, int] = {}

TIMEOUT_SECONDS = 10

# 8-connected neighbors (including diagonals)
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_grid(grid: Any, n: int) -> List[List[int]]:
    """
    Validate grid is n x n with entries 0 or 1.
    Returns grid as list of lists of int.
    """
    if not isinstance(grid, list) or len(grid) != n:
        raise ValueError(
            f"Grid must be {n}x{n}, got {len(grid) if isinstance(grid, list) else 'not a list'} rows"
        )
    result = []
    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(
                f"Row {i}: expected {n} elements, got "
                f"{'not a list' if not isinstance(row, list) else f'{len(row)} elements'}"
            )
        coerced = []
        for j, val in enumerate(row):
            if isinstance(val, float) and val == int(val):
                val = int(val)
            if val not in (0, 1):
                raise ValueError(f"Entry ({i},{j}) must be 0 or 1, got {val!r}")
            coerced.append(val)
        result.append(coerced)
    return result


def _count_live_neighbors(grid: List[List[int]], n: int, r: int, c: int) -> int:
    """Count live neighbors of cell (r, c)."""
    count = 0
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            count += grid[nr][nc]
    return count


def _check_stability(grid: List[List[int]], n: int) -> Tuple[bool, List[Dict]]:
    """
    Check Game of Life stability rules.

    We evaluate cells in the n x n box plus a one-cell outer ring. This
    catches births just outside the submitted box, matching infinite-grid
    still-life semantics.

    Returns (all_ok, list of violations).
    Only collects up to 20 violations for reporting.
    """
    violations = []

    for r in range(-1, n + 1):
        for c in range(-1, n + 1):
            nb = _count_live_neighbors(grid, n, r, c)
            alive = 0 <= r < n and 0 <= c < n and grid[r][c] == 1
            if alive:
                # Live cell: must have 2 or 3 neighbors to survive
                if nb not in (2, 3):
                    if len(violations) < 20:
                        violations.append({
                            "cell": (r, c),
                            "type": "survival",
                            "neighbors": nb,
                            "message": f"Live cell ({r},{c}) has {nb} neighbors, needs 2 or 3",
                        })
            else:
                # Dead cell: must NOT have exactly 3 neighbors (would be born)
                if nb == 3:
                    if len(violations) < 20:
                        violations.append({
                            "cell": (r, c),
                            "type": "birth",
                            "neighbors": nb,
                            "message": f"Dead cell ({r},{c}) has 3 live neighbors and would be born",
                        })

    return len(violations) == 0, violations


def _check_stability_full(grid: List[List[int]], n: int) -> Tuple[bool, int]:
    """
    Check stability and return (all_ok, total_violation_count).

    Includes the one-cell exterior ring around the n x n box so births outside
    the box are counted as violations.

    Does not collect individual violations, just counts.
    """
    count = 0
    for r in range(-1, n + 1):
        for c in range(-1, n + 1):
            nb = _count_live_neighbors(grid, n, r, c)
            alive = 0 <= r < n and 0 <= c < n and grid[r][c] == 1
            if alive:
                if nb not in (2, 3):
                    count += 1
            else:
                if nb == 3:
                    count += 1
    return count == 0, count


def _check_connectivity(grid: List[List[int]], n: int) -> Tuple[bool, int]:
    """
    BFS to check all live cells are 8-connected.
    Returns (is_connected, num_components_found).
    If there are no live cells, returns (False, 0).
    """
    # Find first live cell
    start = None
    live_count = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                live_count += 1
                if start is None:
                    start = (r, c)

    if live_count == 0:
        return False, 0

    # BFS from the first live cell
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited and grid[nr][nc] == 1:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return len(visited) == live_count, 1 if len(visited) == live_count else 2


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
    Verify a connected still life submission.

    Args:
        instance: {"n": int}
        submission: {"claimed_cells": int, "grid": [[0,1,...], ...]}
        current_record: best known live cell count for this n (None if unknown)

    Returns dict with: is_valid, score, error_code, error_message,
                       error_details, is_record
    """
    result: Dict[str, Any] = {
        "is_valid": False,
        "score": None,
        "error_code": None,
        "error_message": None,
        "error_details": None,
        "is_record": False,
    }

    # -- instance validation --
    if "n" not in instance:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "instance must contain 'n'"
        return result

    try:
        n = int(instance["n"])
    except (ValueError, TypeError):
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "instance.n must be an integer"
        return result

    if n not in ALLOWED_N:
        result["error_code"] = "INVALID_INSTANCE"
        result["error_message"] = f"n={n} is not in the allowed list"
        return result

    # -- submission field checks --
    if "claimed_cells" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'claimed_cells'"
        return result

    try:
        claimed_cells = int(submission["claimed_cells"])
    except (ValueError, TypeError):
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "claimed_cells must be a positive integer"
        return result

    if claimed_cells <= 0:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "claimed_cells must be positive"
        return result

    if "grid" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'grid'"
        return result

    # -- grid validation --
    try:
        grid = _validate_grid(submission["grid"], n)
    except ValueError as e:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(e)
        return result

    # -- count live cells --
    actual_cells = sum(row.count(1) for row in grid)
    if actual_cells != claimed_cells:
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = (
            f"Claimed {claimed_cells} live cells but grid has {actual_cells}"
        )
        result["error_details"] = {"claimed": claimed_cells, "actual": actual_cells}
        return result

    if actual_cells == 0:
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = "Grid has no live cells"
        return result

    # -- stability check --
    stable, violations = _check_stability(grid, n)
    if not stable:
        _, total_violations = _check_stability_full(grid, n)
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = (
            f"Pattern is not a still life: {total_violations} cells violate stability rules"
        )
        result["error_details"] = {
            "total_violations": total_violations,
            "sample_violations": violations,
        }
        return result

    # -- connectivity check --
    connected, _ = _check_connectivity(grid, n)
    if not connected:
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = "Live cells are not all 8-connected"
        return result

    # -- success --
    result["is_valid"] = True
    result["score"] = actual_cells

    if current_record is not None and actual_cells > current_record:
        result["is_record"] = True

    return result
