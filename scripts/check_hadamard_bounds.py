#!/usr/bin/env python3
"""
Check Hadamard record sync and bound-ratio calculations.

This script compares verifier constants against the problem page JSON and
validates that each page record is below the implemented theoretical bound.
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal, localcontext
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helper.hadamard import CURRENT_RECORDS, get_theoretical_bound


def main() -> int:
    page_json = (
        REPO_ROOT.parent
        / "Siddhartha-Mahajan.github.io"
        / "problems"
        / "hadamard-maximal-determinant.json"
    )
    if not page_json.exists():
        print(f"ERROR: could not find problem page JSON at {page_json}")
        return 2

    data = json.loads(page_json.read_text(encoding="utf-8"))
    rows = data["leaderboard"]["rows"]

    failures = 0
    with localcontext() as ctx:
        ctx.prec = 160
        for row in rows:
            n = int(row["n"])
            page_best = int(row["best_abs"])
            page_pct = Decimal(str(row["pct"]))
            code_best = CURRENT_RECORDS.get(n)

            if code_best != page_best:
                failures += 1
                print(
                    f"MISMATCH record n={n}: verifier={code_best} page={page_best}"
                )

            bound = get_theoretical_bound(n)
            if Decimal(page_best) > bound:
                failures += 1
                print(f"BOUND VIOLATION n={n}: record exceeds theoretical bound")

            calc_pct = (Decimal(page_best) * Decimal(100)) / bound
            delta = abs(calc_pct - page_pct)
            # Page stores rounded integer percentages; allow half-percent drift.
            if delta > Decimal("0.51"):
                failures += 1
                print(
                    f"PERCENT mismatch n={n}: page={page_pct} calc={calc_pct:.4f} delta={delta:.4f}"
                )

    if failures:
        print(f"FAILED with {failures} issue(s)")
        return 1

    print("OK: Hadamard records and bounds are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
