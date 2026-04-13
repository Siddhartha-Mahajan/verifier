# Percentile Calculation Logic

This document describes how percentiles are computed for submissions.

## 1) Scope of comparison

Percentiles are calculated across rows with the same `problem_name` and `instance`.

When a new submission is stored, rows in that same `problem_name + instance` bucket are recalculated and their `percentile` values are overwritten.

## 2) Score direction groups

Two explicit groups are used:

- `HIGHER_SCORE_BETTER_PROBLEMS` (currently: `hadamard`, `conway`, `stilllife`, `hpprotein`)
- `LOWER_SCORE_BETTER_PROBLEMS` (currently: `tensor`)

## 3) Which rows are included

Only submissions with both conditions are included in percentile computation:

- `is_valid == true`
- `score is not None`

Invalid submissions are excluded from the percentile denominator and their stored `percentile` is `null`.

## 4) Tie behavior

Submissions with identical score receive the same percentile.

This means all best-score ties receive `100.0`.

## 5) Percentile formula used

Let `N` be the number of valid submissions in the same `problem_name + instance` bucket.

For a submission with score `s`:

- Higher-is-better problems:
	- `percentile = 100 * count(score <= s) / N`
- Lower-is-better problems:
	- `percentile = 100 * count(score >= s) / N`

Rounded to 4 decimal places.

## 6) First-entry example

If there is one valid submission (`N = 1`), that submission gets `100.0`.

## 7) Best-tie example

If `N = 5` and two submissions tie for best score, both get:

- `percentile = 100 * 5 / 5 = 100.0`
