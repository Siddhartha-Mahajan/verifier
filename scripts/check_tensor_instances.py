#!/usr/bin/env python3
"""
Check Tensor page/open-instance sync with verifier constants.

Rules:
- All page rows should exist in verifier ALLOWED_SIZES.
- All page rows marked as "open" should exist in verifier ALLOWED_SIZES.
- Verifier CURRENT_RECORDS should match page best values.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helper.tensor import ALLOWED_SIZES, CURRENT_RECORDS


def _is_open_row(note: str) -> bool:
    low = note.strip().lower()
    if "optimal" in low:
        return False
    if "matches lower bound" in low:
        return False
    return True


def main() -> int:
    page_json = (
        REPO_ROOT.parent
        / "Siddhartha-Mahajan.github.io"
        / "problems"
        / "matrix-multiplication-tensor-rank.json"
    )
    if not page_json.exists():
        print(f"ERROR: could not find problem page JSON at {page_json}")
        return 2

    data = json.loads(page_json.read_text(encoding="utf-8"))
    rows = data["leaderboard"]["rows"]

    page_all = set()
    page_open = set()
    page_best = {}
    for row in rows:
        key = row["n"]
        tup = tuple(int(x) for x in key.split(","))
        note = str(row.get("note", ""))

        page_all.add(tup)
        if _is_open_row(note):
            page_open.add(tup)
        page_best[key] = int(row["best"])

    allowed = set(ALLOWED_SIZES)

    failures = 0

    missing_any = sorted(page_all - allowed)
    if missing_any:
        failures += 1
        print(f"MISSING page instances in ALLOWED_SIZES: {missing_any}")

    missing_open = sorted(page_open - allowed)
    if missing_open:
        failures += 1
        print(f"MISSING OPEN instances in ALLOWED_SIZES: {missing_open}")

    for key, best in sorted(page_best.items()):
        got = CURRENT_RECORDS.get(key)
        if got != best:
            failures += 1
            print(f"MISMATCH record {key}: verifier={got} page={best}")

    if failures:
        print(f"FAILED with {failures} issue(s)")
        return 1

    print("OK: Tensor instances and records are synchronized.")
    print(f"Open instances checked: {len(page_open)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
