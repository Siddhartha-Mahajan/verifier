"""
Test suite for CAISc 2026 Verifiable Problems verifiers.

Run:  python -m pytest test_verifiers.py -v
  or: python test_verifiers.py          (runs all tests with basic output)

Each problem has:
  - At least one valid submission per allowed instance
  - Rejection tests for malformed inputs
  - Edge cases

These tests double as example API payloads. Every test_valid_* function
shows exactly what a correct submission looks like.
"""

import sys
import os

# Allow running from verifier/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper.hadamard import verify as verify_hadamard, ALLOWED_N as HADAMARD_ALLOWED_N
from helper.conway import verify as verify_conway
from helper.tensor import verify as verify_tensor, ALLOWED_SIZES as TENSOR_ALLOWED_SIZES
from helper.stilllife import verify as verify_stilllife, ALLOWED_N as STILLLIFE_ALLOWED_N

# ===================================================================
#  HADAMARD MAXIMAL DETERMINANT
# ===================================================================

# Record-holding 23x23 matrix from Orrick et al. (2003)
# det = 2,779,447,296,000,000
WITNESS_23 = [
    [ 1,-1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [-1, 1, 1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
    [ 1, 1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
    [-1,-1, 1, 1,-1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1],
    [-1,-1, 1,-1, 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1],
    [-1, 1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1,-1],
    [-1, 1,-1,-1,-1,-1,-1, 1, 1,-1, 1,-1,-1,-1,-1, 1,-1,-1, 1, 1,-1,-1, 1],
    [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1,-1,-1,-1, 1,-1,-1, 1,-1, 1, 1,-1],
    [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1, 1,-1,-1,-1, 1, 1,-1, 1,-1,-1, 1],
    [-1,-1, 1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1, 1,-1, 1,-1],
    [-1,-1, 1, 1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1,-1, 1,-1, 1],
    [-1, 1,-1, 1, 1,-1,-1, 1,-1,-1,-1, 1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1],
    [-1, 1,-1, 1, 1,-1,-1,-1, 1,-1,-1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1],
    [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1, 1, 1, 1, 1,-1,-1],
    [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1,-1, 1, 1, 1,-1,-1,-1,-1, 1, 1],
    [ 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1],
    [ 1, 1, 1, 1,-1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1, 1,-1,-1,-1,-1],
    [ 1, 1, 1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1,-1],
    [ 1, 1, 1,-1, 1,-1, 1, 1,-1, 1,-1,-1, 1, 1,-1, 1, 1,-1, 1,-1,-1,-1,-1],
    [ 1, 1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1,-1,-1,-1,-1,-1, 1,-1, 1, 1],
    [ 1, 1, 1, 1,-1, 1,-1, 1,-1,-1, 1,-1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1, 1],
    [ 1, 1, 1,-1, 1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1,-1,-1, 1, 1,-1, 1],
    [ 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1,-1,-1, 1, 1, 1,-1],
]


def test_hadamard_valid_n23_witness():
    """The known record-holding matrix for n=23 (Orrick et al. 2003)."""
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 2779447296000000, "matrix": WITNESS_23},
        current_record=2779447296000000,
    )
    assert r["is_valid"] is True
    # Score is now 100 * |det| / theoretical bound(n), rounded to 4 decimals.
    assert abs(r["score"] - 93.1983) < 1e-4
    assert r["is_record"] is False  # matches but doesn't beat record


def test_hadamard_valid_n23_beats_record():
    """Same matrix but with a lower current_record, so it should flag as record."""
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 2779447296000000, "matrix": WITNESS_23},
        current_record=1000000000000000,
    )
    assert r["is_valid"] is True
    assert r["is_record"] is True


def test_hadamard_valid_all_ones():
    """n=23 all-ones matrix. det of all-ones n×n matrix is 0 for n>1.
    This should fail because claimed_det must be positive."""
    matrix = [[1] * 23 for _ in range(23)]
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 1, "matrix": matrix},
    )
    # det is 0, which != 1
    assert r["is_valid"] is False
    assert r["error_code"] == "VERIFICATION_FAILED"


def test_hadamard_reject_bad_n():
    """n=5 is not in the allowed list."""
    r = verify_hadamard(
        instance={"n": 5},
        submission={"claimed_det": 1, "matrix": [[1] * 5 for _ in range(5)]},
    )
    assert r["error_code"] == "INVALID_INSTANCE"


def test_hadamard_reject_wrong_entries():
    """Matrix with a 0 entry (only +1/-1 allowed)."""
    matrix = [[1] * 23 for _ in range(23)]
    matrix[0][0] = 0
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 1, "matrix": matrix},
    )
    assert r["error_code"] == "INVALID_FORMAT"
    assert "+1 or -1" in r["error_message"]


def test_hadamard_reject_wrong_size():
    """22x22 matrix submitted for n=23."""
    matrix = [[1] * 22 for _ in range(22)]
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 1, "matrix": matrix},
    )
    assert r["error_code"] == "INVALID_FORMAT"


def test_hadamard_reject_wrong_claim():
    """Correct matrix, wrong claimed_det."""
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 9999999999999999, "matrix": WITNESS_23},
    )
    assert r["is_valid"] is False
    assert r["error_code"] == "VERIFICATION_FAILED"
    assert r["computed_det"] is not None


def test_hadamard_reject_missing_fields():
    r1 = verify_hadamard(instance={}, submission={"claimed_det": 1, "matrix": []})
    assert r1["error_code"] == "MISSING_FIELD"

    r2 = verify_hadamard(instance={"n": 23}, submission={"matrix": []})
    assert r2["error_code"] == "MISSING_FIELD"

    r3 = verify_hadamard(instance={"n": 23}, submission={"claimed_det": 1})
    assert r3["error_code"] == "MISSING_FIELD"


def test_hadamard_float_coercion():
    """1.0 should be accepted as 1, 1.5 should not."""
    matrix = [[1.0, -1.0], [-1.0, 1.0]]  # won't match n=23 but tests coercion path
    r = verify_hadamard(
        instance={"n": 23},
        submission={"claimed_det": 1, "matrix": matrix},
    )
    # Should fail on size, not on entry type
    assert r["error_code"] == "INVALID_FORMAT"
    assert "23x23" in r["error_message"]


# ===================================================================
#  CONWAY'S 99-GRAPH
# ===================================================================

def test_conway_valid_zero_matrix():
    """All-zero matrix (no edges). Structurally valid, low score."""
    matrix = [[0] * 99 for _ in range(99)]
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["is_valid"] is True
    assert r["score"] == 0.0  # no degree constraints met, no pair constraints met


def test_conway_valid_partial():
    """A random 14-regular-ish graph. Build a simple one: connect vertex i
    to its 7 nearest neighbors in each direction (mod 99). This is regular
    degree 14 but won't satisfy lambda/mu constraints well."""
    import numpy as np
    matrix = [[0] * 99 for _ in range(99)]
    for i in range(99):
        for d in range(1, 8):
            j = (i + d) % 99
            matrix[i][j] = 1
            matrix[j][i] = 1
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["is_valid"] is True
    assert r["score"] > 0  # at least degree constraints should be partially met
    assert r["constraint_report"] is not None
    print(f"  Conway circular graph: score={r['score']:.2f}%")


def test_conway_reject_wrong_size():
    """98x98 matrix."""
    matrix = [[0] * 98 for _ in range(98)]
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["error_code"] == "INVALID_FORMAT"


def test_conway_reject_not_symmetric():
    """Asymmetric matrix."""
    matrix = [[0] * 99 for _ in range(99)]
    matrix[0][1] = 1
    matrix[1][0] = 0  # asymmetry
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["error_code"] == "INVALID_FORMAT"
    assert "symmetric" in r["error_message"].lower()


def test_conway_reject_nonzero_diagonal():
    matrix = [[0] * 99 for _ in range(99)]
    matrix[5][5] = 1
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["error_code"] == "INVALID_FORMAT"
    assert "diagonal" in r["error_message"].lower()


def test_conway_reject_non_binary():
    matrix = [[0] * 99 for _ in range(99)]
    matrix[0][1] = 2
    matrix[1][0] = 2
    r = verify_conway(instance={}, submission={"matrix": matrix})
    assert r["error_code"] == "INVALID_FORMAT"
    assert "0 or 1" in r["error_message"]


def test_conway_reject_missing_matrix():
    r = verify_conway(instance={}, submission={})
    assert r["error_code"] == "MISSING_FIELD"


def test_conway_record_detection():
    """A matrix scoring above current_record_score should flag is_record."""
    matrix = [[0] * 99 for _ in range(99)]
    for i in range(99):
        for d in range(1, 8):
            j = (i + d) % 99
            matrix[i][j] = 1
            matrix[j][i] = 1
    r = verify_conway(instance={}, submission={"matrix": matrix}, current_record_score=0.0)
    assert r["is_record"] is True


# ===================================================================
#  MATRIX MULTIPLICATION TENSOR RANK
# ===================================================================

# --- Strassen's algorithm: R(2,2,2) = 7 ---

STRASSEN_U = [
    [[1,0],[0,1]],   # M1: a+d
    [[0,0],[1,1]],   # M2: c+d
    [[1,0],[0,0]],   # M3: a
    [[0,0],[0,1]],   # M4: d
    [[1,1],[0,0]],   # M5: a+b
    [[-1,0],[1,0]],  # M6: c-a
    [[0,1],[0,-1]],  # M7: b-d
]
STRASSEN_V = [
    [[1,0],[0,1]],   # M1: e+h
    [[1,0],[0,0]],   # M2: e
    [[0,1],[0,-1]],  # M3: f-h
    [[-1,0],[1,0]],  # M4: g-e
    [[0,0],[0,1]],   # M5: h
    [[1,1],[0,0]],   # M6: e+f
    [[0,0],[1,1]],   # M7: g+h
]
STRASSEN_W = [
    [[1,0],[0,1]],   # M1 -> C11+, C22+
    [[0,0],[1,-1]],  # M2 -> C21+, C22-
    [[0,1],[0,1]],   # M3 -> C12+, C22+
    [[1,0],[1,0]],   # M4 -> C11+, C21+
    [[-1,1],[0,0]],  # M5 -> C11-, C12+
    [[0,0],[0,1]],   # M6 -> C22+
    [[1,0],[0,0]],   # M7 -> C11+
]


def test_tensor_valid_strassen():
    """Strassen's 7-multiplication algorithm for 2x2."""
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={"num_multiplications": 7, "U": STRASSEN_U, "V": STRASSEN_V, "W": STRASSEN_W},
        current_record=7,
    )
    assert r["is_valid"] is True
    assert r["score"] == 7
    assert r["tests_passed"] == 100
    assert r["is_record"] is False  # matches record, doesn't beat it


def _build_naive_decomposition(n, m, p):
    """
    Build the naive (schoolbook) tensor decomposition for (n,m,p) multiplication.
    Uses n*m*p multiplications. Term (i,k,j) computes A[i,k]*B[k,j] and adds to C[i,j].
    """
    R = n * m * p
    U, V, W = [], [], []
    for i in range(n):
        for k in range(m):
            for j in range(p):
                u = [[0]*m for _ in range(n)]
                u[i][k] = 1
                v = [[0]*p for _ in range(m)]
                v[k][j] = 1
                w = [[0]*p for _ in range(n)]
                w[i][j] = 1
                U.append(u)
                V.append(v)
                W.append(w)
    return R, U, V, W


def test_tensor_valid_naive_all_sizes():
    """Naive decomposition for every allowed (n,m,p). Slow but correct."""
    for n, m, p in TENSOR_ALLOWED_SIZES:
        R, U, V, W = _build_naive_decomposition(n, m, p)
        r = verify_tensor(
            instance={"n": n, "m": m, "p": p},
            submission={"num_multiplications": R, "U": U, "V": V, "W": W},
        )
        assert r["is_valid"] is True, f"Naive ({n},{m},{p}) failed: {r['error_message']}"
        assert r["score"] == R
        assert r["tests_passed"] == 100
        print(f"  Tensor naive ({n},{m},{p}): R={R}, passed")


def test_tensor_valid_rational_coefficients():
    """Test that rational string coefficients like '1/2' are accepted."""
    # Trivially: multiply by 2 then divide by 2 in W
    # For 2x2: use 8 naive terms but with halved U and doubled W
    n, m, p = 2, 2, 2
    R = 8
    U, V, W = [], [], []
    for i in range(n):
        for k in range(m):
            for j in range(p):
                u = [["0"]*m for _ in range(n)]
                u[i][k] = "2"
                v = [[0]*p for _ in range(m)]
                v[k][j] = 1
                w = [["0"]*p for _ in range(n)]
                w[i][j] = "1/2"
                U.append(u)
                V.append(v)
                W.append(w)
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={"num_multiplications": R, "U": U, "V": V, "W": W},
    )
    assert r["is_valid"] is True
    assert r["score"] == 8
    assert r["tests_passed"] == 100


def test_tensor_reject_bad_size():
    r = verify_tensor(
        instance={"n": 9, "m": 9, "p": 9},
        submission={"num_multiplications": 1, "U": [[[0]]], "V": [[[0]]], "W": [[[0]]]},
    )
    assert r["error_code"] == "INVALID_INSTANCE"


def test_tensor_reject_wrong_dimensions():
    """U has wrong inner dimensions."""
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={
            "num_multiplications": 1,
            "U": [[[1, 0, 0], [0, 0, 0]]],  # 2x3, should be 2x2
            "V": [[[0, 0], [0, 0]]],
            "W": [[[0, 0], [0, 0]]],
        },
    )
    assert r["error_code"] == "INVALID_FORMAT"


def test_tensor_reject_float_coefficient():
    """Float 0.5 should be rejected (must use string '1/2')."""
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={
            "num_multiplications": 1,
            "U": [[[0.5, 0], [0, 0]]],
            "V": [[[0, 0], [0, 0]]],
            "W": [[[0, 0], [0, 0]]],
        },
    )
    assert r["error_code"] == "INVALID_FORMAT"
    assert "rational string" in r["error_message"].lower() or "float" in r["error_message"].lower()


def test_tensor_reject_wrong_result():
    """A decomposition that doesn't compute the right product."""
    # All-zero U/V/W produces zero output, which is wrong
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={
            "num_multiplications": 1,
            "U": [[[0, 0], [0, 0]]],
            "V": [[[0, 0], [0, 0]]],
            "W": [[[1, 0], [0, 1]]],
        },
    )
    assert r["error_code"] == "VERIFICATION_FAILED"
    assert r["tests_passed"] < 100


def test_tensor_reject_missing_fields():
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={"num_multiplications": 1, "U": [[[0]]]},
    )
    assert r["error_code"] == "MISSING_FIELD"


def test_tensor_record_detection():
    """Strassen with current_record=8 should flag as new record (7 < 8)."""
    r = verify_tensor(
        instance={"n": 2, "m": 2, "p": 2},
        submission={"num_multiplications": 7, "U": STRASSEN_U, "V": STRASSEN_V, "W": STRASSEN_W},
        current_record=8,
    )
    assert r["is_record"] is True


# ===================================================================
#  CONNECTED STILL LIFE
# ===================================================================

def _make_grid(n, live_cells):
    """Create an n×n grid with specific cells alive."""
    grid = [[0] * n for _ in range(n)]
    for r, c in live_cells:
        grid[r][c] = 1
    return grid


def _block(r, c):
    """A 2x2 block at (r,c). 4 cells. Stable and connected."""
    return [(r, c), (r, c+1), (r+1, c), (r+1, c+1)]


def _beehive(r, c):
    """A beehive at (r,c). 6 cells. Stable and connected.
      .##.
      #..#
      .##.
    """
    return [(r, c+1), (r, c+2), (r+1, c), (r+1, c+3), (r+2, c+1), (r+2, c+2)]


def _loaf(r, c):
    """A loaf at (r,c). 7 cells. Stable and connected.
      .##.
      #..#
      .#.#
      ..#.
    """
    return [(r, c+1), (r, c+2), (r+1, c), (r+1, c+3), (r+2, c+1), (r+2, c+3), (r+3, c+2)]


def _boat(r, c):
    """A boat at (r,c). 5 cells. Stable and connected.
      ##.
      #.#
      .#.
    """
    return [(r, c), (r, c+1), (r+1, c), (r+1, c+2), (r+2, c+1)]


def _tub(r, c):
    """A tub at (r,c). 4 cells. Stable and connected.
      .#.
      #.#
      .#.
    """
    return [(r, c+1), (r+1, c), (r+1, c+2), (r+2, c+1)]


def _ship(r, c):
    """A ship at (r,c). 6 cells. Stable and connected.
      ##.
      #.#
      .##
    """
    return [(r, c), (r, c+1), (r+1, c), (r+1, c+2), (r+2, c+1), (r+2, c+2)]


def _connect_blocks_horizontal(r, c1, c2):
    """Connect two blocks at (r,c1) and (r,c2) using a snake/bridge pattern.
    Both blocks are 2x2. We bridge them with a boat-like connector.
    The gap between them (c1+2 to c2-1) must be at least 3 columns.
    Returns additional cells that form the bridge. The bridge is:
      block1  .#.  block2
              #.#
              .#.
    Placed so the bridge column is between the two blocks.
    """
    mid = (c1 + 2 + c2) // 2
    # Use a tub shape as bridge, connected diagonally to both blocks
    return [(r, mid), (r+1, mid-1), (r+1, mid+1), (r+2, mid)]


def test_stilllife_valid_block_n8():
    """Single block (2x2) in 8x8 grid."""
    cells = _block(3, 3)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 4, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 4


def test_stilllife_valid_beehive_n8():
    """Single beehive in 8x8 grid."""
    cells = _beehive(2, 2)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 6, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 6


def test_stilllife_valid_loaf_n8():
    """Single loaf in 8x8 grid."""
    cells = _loaf(2, 2)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 7, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 7


def test_stilllife_valid_boat_n8():
    """Single boat in 8x8 grid."""
    cells = _boat(2, 2)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 5, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 5


def test_stilllife_valid_ship_n8():
    """Single ship in 8x8 grid."""
    cells = _ship(2, 2)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 6, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 6


def test_stilllife_valid_tub_n10():
    """Single tub in 10x10 grid."""
    cells = _tub(4, 4)
    grid = _make_grid(10, cells)
    r = verify_stilllife(
        instance={"n": 10},
        submission={"claimed_cells": 4, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 4


def test_stilllife_valid_beehive_n10():
    """Single beehive in 10x10 grid."""
    cells = _beehive(3, 3)
    grid = _make_grid(10, cells)
    r = verify_stilllife(
        instance={"n": 10},
        submission={"claimed_cells": 6, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 6


def test_stilllife_valid_block_n16():
    """Single block in 16x16 grid."""
    cells = _block(7, 7)
    grid = _make_grid(16, cells)
    r = verify_stilllife(
        instance={"n": 16},
        submission={"claimed_cells": 4, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 4


def test_stilllife_valid_loaf_n20():
    """Single loaf in 20x20 grid."""
    cells = _loaf(8, 8)
    grid = _make_grid(20, cells)
    r = verify_stilllife(
        instance={"n": 20},
        submission={"claimed_cells": 7, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 7


def test_stilllife_valid_block_n32():
    """Single block in 32x32 grid."""
    cells = _block(15, 15)
    grid = _make_grid(32, cells)
    r = verify_stilllife(
        instance={"n": 32},
        submission={"claimed_cells": 4, "grid": grid},
    )
    assert r["is_valid"] is True
    assert r["score"] == 4


def test_stilllife_reject_bad_n():
    r = verify_stilllife(
        instance={"n": 5},
        submission={"claimed_cells": 1, "grid": [[0]*5]*5},
    )
    assert r["error_code"] == "INVALID_INSTANCE"


def test_stilllife_reject_wrong_size():
    """7x7 grid for n=8."""
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 1, "grid": [[0]*7]*7},
    )
    assert r["error_code"] == "INVALID_FORMAT"


def test_stilllife_reject_unstable_single_cell():
    """Single cell dies (0 neighbors, needs 2-3)."""
    grid = _make_grid(8, [(4, 4)])
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 1, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"
    assert "stability" in r["error_message"].lower() or "still life" in r["error_message"].lower()


def test_stilllife_reject_unstable_line():
    """Three in a row oscillates (blinker), not a still life."""
    grid = _make_grid(8, [(3, 3), (3, 4), (3, 5)])
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 3, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"


def test_stilllife_reject_disconnected():
    """Two separate blocks (not 8-connected)."""
    cells = _block(1, 1) + _block(5, 5)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 8, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"
    assert "connected" in r["error_message"].lower()


def test_stilllife_reject_wrong_cell_count():
    """Claimed 10 cells but grid has 4."""
    cells = _block(3, 3)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 10, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"
    assert "4" in r["error_message"]  # actual count


def test_stilllife_reject_birth_violation():
    """Pattern where a dead cell has exactly 3 live neighbors (would be born).
    L-tromino: ##
               #.
    Cell (0,1),(1,0),(0,0) alive. Dead cell (1,1) has 3 neighbors -> birth."""
    grid = _make_grid(8, [(2, 2), (2, 3), (3, 2)])
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 3, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"


def test_stilllife_reject_birth_outside_box_boundary():
    """Reject patterns that create births just outside the n x n box.

    This pattern is stable inside the box but causes a birth at (-1, 1)
    on the infinite board.
    """
    cells = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 3)]
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 6, "grid": grid},
    )
    assert r["error_code"] == "VERIFICATION_FAILED"


def test_stilllife_reject_missing_fields():
    r1 = verify_stilllife(instance={"n": 8}, submission={"grid": [[0]*8]*8})
    assert r1["error_code"] == "MISSING_FIELD"

    r2 = verify_stilllife(instance={"n": 8}, submission={"claimed_cells": 1})
    assert r2["error_code"] == "MISSING_FIELD"

    r3 = verify_stilllife(instance={}, submission={"claimed_cells": 1, "grid": []})
    assert r3["error_code"] == "MISSING_FIELD"


def test_stilllife_record_detection():
    """Block with current_record=3 should flag as record (4 > 3)."""
    cells = _block(3, 3)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 4, "grid": grid},
        current_record=3,
    )
    assert r["is_record"] is True


def test_stilllife_diagonally_connected():
    """Two blocks connected only diagonally (should pass 8-connectivity).
    Block at (1,1) and block at (3,3) share a diagonal corner."""
    cells = _block(1, 1) + _block(3, 3)
    grid = _make_grid(8, cells)
    r = verify_stilllife(
        instance={"n": 8},
        submission={"claimed_cells": 8, "grid": grid},
    )
    # These blocks overlap at diagonal: (2,2) is in block1 and (3,3) is in block2
    # Block1: (1,1),(1,2),(2,1),(2,2).  Block2: (3,3),(3,4),(4,3),(4,4).
    # (2,2) and (3,3) are diagonally adjacent -> 8-connected.
    # But we need to check if they're still a valid still life together.
    # (2,2) has neighbors: (1,1),(1,2),(2,1) from block1 + (3,3) from block2 = 4 neighbors.
    # 4 is too many for survival (needs 2 or 3). So this is NOT a valid still life.
    assert r["error_code"] == "VERIFICATION_FAILED"


# ===================================================================
#  RUNNER
# ===================================================================

def _run_all():
    """Run all test functions and report results."""
    import inspect
    this_module = sys.modules[__name__]
    tests = sorted(
        [(name, obj) for name, obj in inspect.getmembers(this_module, inspect.isfunction)
         if name.startswith("test_")],
        key=lambda x: x[0]
    )

    passed = 0
    failed = 0
    errors = []

    for name, func in tests:
        try:
            func()
            passed += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            errors.append((name, e))
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            errors.append((name, e))
            print(f"  ERROR {name}: {type(e).__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"  {passed} passed, {failed} failed, {passed + failed} total")
    if errors:
        print(f"\nFailures:")
        for name, e in errors:
            print(f"  {name}: {e}")
    print()
    return failed == 0


if __name__ == "__main__":
    print("CAISc 2026 Verifier Test Suite\n")
    success = _run_all()
    sys.exit(0 if success else 1)
