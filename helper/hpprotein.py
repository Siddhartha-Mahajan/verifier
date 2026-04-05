"""
HP Protein Folding -- Verification Module

Given an HP sequence and a lattice embedding, verify a valid 2D self-avoiding
fold and score it by H-H topological contacts (higher is better).

A contact is a pair (i, j) such that:
  - i and j are both hydrophobic residues (H)
  - |i - j| > 1 (not chain-adjacent in sequence)
  - Manhattan distance between coordinates is 1
"""

from __future__ import annotations

from typing import Any


# Warm-up + open benchmark instances (proven-optimal instances are excluded).
SEQUENCES: dict[str, dict[str, Any]] = {
    "WARMUP_6H": {
        "sequence": "HHHHHH",
        "best": 2,
        "note": "Warm-up all-H chain",
    },
    "S5": {
        "sequence": "PPHPPHHPPHHPPPPPHHHHHHHHHHPPPPPPHHPPHHPPHPPHHHHH",
        "best": 23,
        "note": "Open; best known since ~2004",
    },
    "S6": {
        "sequence": "PPHPPHPHPHHHHPHPPPHPPPHPPPPHPPPHPPPHPHHHHPHPHPHPHH",
        "best": 21,
        "note": "Open; best known since ~2000",
    },
    "S7": {
        "sequence": "PPHHHPHHHHHHHHPPPHHHHHHHHHHPHPPPHHHHHHHHHHHHPPPPHHHHHHPHHPHP",
        "best": 36,
        "note": "Open; likely suboptimal",
    },
    "S8": {
        "sequence": "HHHHHHHHHHHHPHPHPPHHPPHHPPHPPHHPPHHPPHPPHHPPHHPPHPHPHHHHHHHHHHHH",
        "best": 42,
        "note": "Open; largest well-studied sequence",
    },
    "S9": {
        "sequence": "HHHHPPPPHHHHHHHHHHHHPPPPPPHHHHHHHHHHHHPPPHHHHHHHHHHHHPPPHHHHHHHHHHHHPPPHPPHHPPHHPPHPH",
        "best": 53,
        "note": "Open; putative ground state",
    },
    "S10": {
        "sequence": "PPPHHPPHHHHPPHHHPHHPHHPHHHHPPPPPPPPHHHHHHPPHHHHHHPPPPPPPPPHPHHPHHHHHHHHHHHPPHHHPHHPHPPHPHHHPPPPPPHHH",
        "best": 50,
        "note": "Open; longest standard benchmark",
    },
}

ALLOWED_SEQUENCE_IDS = list(SEQUENCES.keys())
TIMEOUT_SECONDS = 10


def get_sequence(sequence_id: str) -> str | None:
    item = SEQUENCES.get(sequence_id)
    if item is None:
        return None
    return str(item["sequence"])


def get_record(sequence_id: str) -> int | None:
    item = SEQUENCES.get(sequence_id)
    if item is None:
        return None
    best = item.get("best")
    return int(best) if isinstance(best, int) else None


def get_instances() -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []
    for sequence_id in ALLOWED_SEQUENCE_IDS:
        sequence = get_sequence(sequence_id)
        best = get_record(sequence_id)
        if sequence is None:
            continue
        instances.append(
            {
                "sequence_id": sequence_id,
                "length": len(sequence),
                "best": best,
            }
        )
    return instances


def _normalize_sequence_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("instance.sequence_id must be a string")
    sequence_id = value.strip().upper()
    if not sequence_id:
        raise ValueError("instance.sequence_id must be non-empty")
    return sequence_id


def _coerce_int_strict(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _parse_coord(coord: Any, index: int) -> tuple[int, int]:
    if not isinstance(coord, list) or len(coord) != 2:
        raise ValueError(f"coords[{index}] must be [x, y]")
    x = _coerce_int_strict(coord[0], f"coords[{index}][0]")
    y = _coerce_int_strict(coord[1], f"coords[{index}][1]")
    return x, y


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _count_hh_contacts(sequence: str, coords: list[tuple[int, int]]) -> int:
    count = 0
    n = len(sequence)
    for i in range(n):
        if sequence[i] != "H":
            continue
        for j in range(i + 2, n):
            if sequence[j] != "H":
                continue
            if _manhattan(coords[i], coords[j]) == 1:
                count += 1
    return count


def _radius_of_gyration_squared(coords: list[tuple[int, int]]) -> float:
    n = len(coords)
    mean_x = sum(x for x, _ in coords) / n
    mean_y = sum(y for _, y in coords) / n
    return sum((x - mean_x) ** 2 + (y - mean_y) ** 2 for x, y in coords) / n


def verify(
    instance: dict[str, Any],
    submission: dict[str, Any],
    current_record: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "is_valid": False,
        "score": None,
        "error_code": None,
        "error_message": None,
        "error_details": None,
        "is_record": False,
        "compactness_rg2": None,
    }

    if "sequence_id" not in instance:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "instance must contain 'sequence_id'"
        return result

    try:
        sequence_id = _normalize_sequence_id(instance["sequence_id"])
    except ValueError as exc:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(exc)
        return result

    if sequence_id not in SEQUENCES:
        result["error_code"] = "INVALID_INSTANCE"
        result["error_message"] = f"sequence_id={sequence_id} is not in the allowed list"
        return result

    sequence = get_sequence(sequence_id)
    if sequence is None:
        result["error_code"] = "INVALID_INSTANCE"
        result["error_message"] = f"sequence_id={sequence_id} is not in the allowed list"
        return result

    lattice = submission.get("lattice", "2D")
    if not isinstance(lattice, str) or lattice.strip().upper() != "2D":
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "submission.lattice must be '2D'"
        return result

    if "coords" not in submission:
        result["error_code"] = "MISSING_FIELD"
        result["error_message"] = "submission must contain 'coords'"
        return result

    raw_coords = submission["coords"]
    if not isinstance(raw_coords, list):
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = "submission.coords must be a list of [x, y] pairs"
        return result

    expected_len = len(sequence)
    if len(raw_coords) != expected_len:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = (
            f"coords length must equal sequence length ({expected_len}), got {len(raw_coords)}"
        )
        return result

    coords: list[tuple[int, int]] = []
    try:
        for idx, coord in enumerate(raw_coords):
            coords.append(_parse_coord(coord, idx))
    except ValueError as exc:
        result["error_code"] = "INVALID_FORMAT"
        result["error_message"] = str(exc)
        return result

    visited = set(coords)
    if len(visited) != len(coords):
        result["error_code"] = "VERIFICATION_FAILED"
        result["error_message"] = "Fold is not self-avoiding: duplicate coordinates found"
        return result

    for i in range(len(coords) - 1):
        if _manhattan(coords[i], coords[i + 1]) != 1:
            result["error_code"] = "VERIFICATION_FAILED"
            result["error_message"] = (
                f"Chain connectivity failed between residues {i} and {i + 1}: "
                "consecutive residues must be lattice-adjacent"
            )
            return result

    contacts = _count_hh_contacts(sequence, coords)
    rg2 = _radius_of_gyration_squared(coords)

    result["is_valid"] = True
    result["score"] = contacts
    result["compactness_rg2"] = round(rg2, 6)

    if current_record is not None and contacts > current_record:
        result["is_record"] = True

    result["message"] = (
        f"Verification passed. {contacts} H-H contacts, compactness_rg2={result['compactness_rg2']}"
    )

    return result
