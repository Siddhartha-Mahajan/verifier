# Percentile Calculation Logic

This document describes how percentiles are computed for submissions.

## 1) Scope of comparison

Percentiles are calculated across rows with the same `problem_name` and `instance`.

When a new submission is stored, rows in that same `problem_name + instance` bucket are recalculated and their `percentile` values are overwritten.

## 2) Score direction groups

Two explicit groups are used:

- `HIGHER_SCORE_BETTER_PROBLEMS` (currently: `hadamard`, `conway`, `stilllife`, `hpprotein`)
- `LOWER_SCORE_BETTER_PROBLEMS` (currently: `tensor`)

## 3) Fallback score for invalid + missing score

If `is_valid == false` and `score is None`, a fallback score is used for ranking:

- Higher-is-better problems: `0`
- Lower-is-better problems: `+Infinity`

If a row already has a score (even when `is_valid == false`), that score is preserved.

Note: the current implementation also persists this fallback into the `score` column for rows that were invalid with `score = None`.

## 4) Imaginary worst entry

For percentile ranking, one extra **imaginary worst** entry is always included in the denominator.

If there are `N` ranked real entries, percentile is computed against `N + 1` total entries.

This prevents edge behavior at the low end and keeps ranking stable for early submissions.

## 5) Tie-breaking rule

Ties are broken deterministically by submission order:

1. Better score first (based on problem direction)
2. Earlier `created_at` first
3. `submission_id` as final deterministic tie-breaker

So when two submissions have equal score, the one submitted earlier gets higher percentile.

## 6) Percentile formula used

After sorting from best to worst, for each entry at zero-based position `index` in the ranked list of size `N`:

- `worse_count_including_imaginary = N - index`
- `percentile = 100 * worse_count_including_imaginary / (N + 1)`

Rounded to 4 decimal places.

## 7) First-entry example

If there is only one real entry (`N = 1`):

- `index = 0`
- `worse_count_including_imaginary = 1`
- `percentile = 100 * 1 / 2 = 50`

So the first entry gets percentile `50.0` under this logic.
