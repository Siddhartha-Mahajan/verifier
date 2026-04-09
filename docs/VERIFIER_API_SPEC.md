# CAISc 2026 Verifiable Problems -- Verification & API Spec

## Summary

This system verifies submissions to the CAISc 2026 Verifiable Problems Track. A participant submits a JSON payload containing a candidate solution to one of five math/CS/biology problems. The system validates the input, runs problem-specific verification, computes a score, stores the result in PostgreSQL, and returns the score with an all-time percentile ranking. New records are flagged for manual review before appearing on the public leaderboard.

The service is independent of the conference website. Users submit directly to the API.

---

## MVP Deliverables

1. **Five problem verifiers** (Python modules, no external services):
   - `hadamard.py` -- Hadamard Maximal Determinant
   - `conway.py` -- Conway's 99-Graph
   - `tensor.py` -- Matrix Multiplication Tensor Rank
   - `stilllife.py` -- Connected Still Life
   - `hpprotein.py` -- HP Protein Folding (2D lattice)

2. **API server** (FastAPI, 5 endpoints):
   - `POST /api/v1/submit` -- submit and verify a solution
   - `GET /api/v1/submission/{id}` -- retrieve a past result
   - `GET /api/v1/problems/{id}/instances` -- list allowed instances
   - `POST /api/v1/leaderboard` -- protected top-k leaderboard for one problem instance
   - `GET /api/v1/health` -- health check

3. **PostgreSQL storage** -- every submission stored forever, indexed for percentile queries

4. **Rate limiting** -- per-IP, sliding window

5. **Configuration** -- allowed instances and current records in a JSON config file, environment variables for secrets

**Not in MVP:** email verification, webhooks, RNA inverse folding, admin dashboard.

---

## Problem Definitions

### Hadamard Maximal Determinant (`hadamard`)

| Field        | Value                                                                        |
| ------------ | ---------------------------------------------------------------------------- |
| Instance     | `{"n": 23}` where n is from the allowed list                                 |
| Submission   | `{"claimed_det": <int>, "matrix": [[1,-1,...], ...]}`                        |
| Verification | Matrix is n x n, entries are +1 or -1, exact determinant matches claimed_det |
| Score        | abs(determinant), higher is better                                           |
| Timeout      | 60 seconds                                                                   |
| Max payload  | 500 KB                                                                       |

**Allowed n:** 23, 27, 29, 31, 33, 34, 35, 39, 45, 47, 53, 63, 67, 69, 73, 75, 77, 79, 83, 87, 91, 93, 95, 99

**Verification steps:**

1. Check n is in allowed list
2. Check matrix is square n x n
3. Check every entry is exactly +1 or -1 (integers, not floats)
4. Compute exact integer determinant using sympy (required dependency)
5. Check abs(computed) == claimed_det
6. Compare against current record for this n

---

### Conway's 99-Graph (`conway`)

| Field        | Value                                                                            |
| ------------ | -------------------------------------------------------------------------------- |
| Instance     | `{}` (fixed problem, 99 vertices)                                                |
| Submission   | `{"matrix": [[0,1,...], ...]}`                                                   |
| Verification | 99 x 99 symmetric binary matrix, zero diagonal, degree-14, lambda/mu constraints |
| Score        | percentage of constraints satisfied (0-100), higher is better                    |
| Timeout      | 10 seconds                                                                       |
| Max payload  | 100 KB                                                                           |

**Scoring model:** Unlike other problems, Conway accepts partial solutions. Any syntactically valid 99 x 99 binary symmetric matrix with zero diagonal gets a score. The score is the percentage of the 4950 constraints satisfied (99 degree constraints + 4851 pair constraints). A score of 100.0 means the graph exists and you found it.

**Verification steps:**

1. Check matrix is 99 x 99
2. Check symmetric with zero diagonal
3. Check all entries are 0 or 1
4. Count degree constraints satisfied (each row should sum to 14)
5. Compute A-squared; count lambda constraints (A-squared[i,j] = 1 for edges) and mu constraints (A-squared[i,j] = 2 for non-edges)
6. Score = satisfied / 4950 \* 100

**Validity:** A submission is valid (stored with score, included in percentile) as long as it passes steps 1-3 (correct shape, symmetric, binary, zero diagonal). Steps 4-6 determine the score. This means partial solutions are accepted and ranked.

---

### Matrix Multiplication Tensor Rank (`tensor`)

| Field        | Value                                                                         |
| ------------ | ----------------------------------------------------------------------------- |
| Instance     | `{"n": 3, "m": 3, "p": 6}` where (n,m,p) is from the allowed list             |
| Submission   | `{"num_multiplications": <int>, "U": [...], "V": [...], "W": [...]}`          |
| Verification | Dimensions match, algorithm produces correct product on 100 random test pairs |
| Score        | num_multiplications, **lower is better**                                      |
| Timeout      | 30 seconds                                                                    |
| Max payload  | 200 KB                                                                        |

**Allowed sizes:** (2,2,2), (2,2,3), (2,3,3), (2,3,4), (2,4,5), (3,3,3), (3,3,4), (3,3,6), (4,4,4), (4,4,5), (5,5,5)

**Coefficient format:** All entries in U, V, W must be integers or exact rationals written as strings (e.g., `"1/2"`, `"-3/4"`). No floats. The verifier parses everything into Python `fractions.Fraction` for exact arithmetic.

**Submission structure:**

- `U`: list of R matrices, each n x m (coefficients applied to entries of A)
- `V`: list of R matrices, each m x p (coefficients applied to entries of B)
- `W`: list of R matrices, each n x p (reconstruction weights for output C)
- `num_multiplications`: R, the length of U/V/W (must match)

**How the algorithm is verified:** For each of 100 random integer matrix pairs A (n x m) and B (m x p) with entries in [-10, 10]:

1. Compute expected C = A \* B using standard multiplication
2. Run the submitted algorithm: for each t in 1..R, compute scalar `s_t = sum(U[t] * A) * sum(V[t] * B)`, then accumulate `C_submitted += s_t * W[t]` (element-wise)
3. Check C_submitted == C exactly

The random seed is fixed per submission (seeded from submission_id) for reproducibility.

**Verification steps:**

1. Check (n,m,p) is in allowed list
2. Check U, V, W all have length == num_multiplications
3. Check each U[t] is n x m, V[t] is m x p, W[t] is n x p
4. Parse all coefficients as Fraction (reject anything that isn't int or valid rational string)
5. Run on 100 random test pairs, check exact equality

---

### Connected Still Life (`stilllife`)

| Field        | Value                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------- |
| Instance     | `{"n": 20}` where n is from the allowed list                                                 |
| Submission   | `{"claimed_cells": <int>, "grid": [[0,1,...], ...]}`                                         |
| Verification | Grid is n x n binary, stable under GoL rules, all live cells 8-connected, cell count matches |
| Score        | claimed_cells, higher is better                                                              |
| Timeout      | 10 seconds                                                                                   |
| Max payload  | 50 KB                                                                                        |

**Allowed n:** 8, 10, 16, 20, 32

**Verification steps:**

1. Check n is in allowed list
2. Check grid is n x n with entries 0 or 1
3. Count live cells, verify count == claimed_cells
4. For each live cell: check it has exactly 2 or 3 live neighbors (survival rule)
5. For each dead cell adjacent to any live cell: check it does NOT have exactly 3 live neighbors (no-birth rule)
6. BFS from any live cell; verify all live cells are reached (8-connectivity)

---

### HP Protein Folding (`hpprotein`)

| Field        | Value                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| Instance     | `{"sequence_id": "S5"}` where sequence_id is one of `WARMUP_6H, S5, S6, S7, S8, S9, S10`                     |
| Submission   | `{"lattice": "2D", "coords": [[x0,y0], [x1,y1], ...]}`                                                       |
| Verification | Self-avoiding walk, chain-adjacent residues are lattice-adjacent, coordinates length matches sequence length |
| Score        | number of non-sequential H-H lattice contacts (higher is better)                                             |
| Timeout      | 10 seconds                                                                                                   |
| Max payload  | 100 KB                                                                                                       |

**Note on instances:** Proven-optimal benchmark cases are excluded from active API instances. The API accepts warm-up plus open targets.

**Verification steps:**

1. Check sequence_id is in the allowed open-instance list
2. Check lattice is `2D`
3. Check coords length equals sequence length
4. Check every coordinate is an integer pair
5. Check all coordinates are unique (self-avoidance)
6. Check each consecutive pair has Manhattan distance 1
7. Count H-H contacts for pairs `(i, j)` where `|i-j| > 1`, both residues are `H`, and coordinates are lattice-adjacent

**Additional metric:** compactness (`radius of gyration`) is computed for diagnostics/tie-analysis, while score remains contact count.

---

## Database

**PostgreSQL 15+**, single table `submissions`:

| Column          | Type         | Notes                                                |
| --------------- | ------------ | ---------------------------------------------------- |
| submission_id   | UUID         | Primary key, generated server-side                   |
| created_at      | TIMESTAMPTZ  | UTC, default now()                                   |
| email           | VARCHAR(255) | As entered, unverified in MVP                        |
| ip_address      | VARCHAR(45)  | From X-Forwarded-For or remote addr                  |
| problem_name    | VARCHAR(32)  | hadamard, conway, tensor, stilllife, hpprotein       |
| instance        | JSONB        | Problem parameters                                   |
| submission      | JSONB        | Raw payload (the matrix/grid/tensors)                |
| is_valid        | BOOLEAN      | Passed structural validation                         |
| score           | NUMERIC      | NULL only if is_valid = false                        |
| score_direction | VARCHAR(4)   | "high" or "low" (denormalized for query convenience) |
| error_message   | TEXT         | NULL if valid                                        |
| percentile      | NUMERIC      | Computed at query time, cached here                  |
| is_record       | BOOLEAN      | Beats current best for this problem+instance         |

**Indexes:**

- `(problem_name, instance, is_valid, score DESC)` for percentile queries
- `(ip_address, created_at)` for rate limiting
- `(created_at)` for auditing

**Retention:** Forever. Submissions are immutable after creation.

---

## Percentile Calculation

For problems where higher is better (hadamard, conway, stilllife, hpprotein):

```
percentile = 100 * count(valid submissions with score < this_score) / count(all valid submissions for this problem+instance)
```

For problems where lower is better (tensor):

```
percentile = 100 * count(valid submissions with score > this_score) / count(all valid submissions for this problem+instance)
```

Recalculated on each GET request (not cached in MVP).

---

## Record Detection

When a valid submission beats the current best-known score for its problem+instance:

1. Set `is_record = true`
2. Hold for manual review (do not update public leaderboard automatically)
3. After admin review, mark `verified_record = true` and update the config file's current records

For Conway, any score above the previous highest partial score is a record. A score of 100.0 is a major event (problem solved).

---

## Rate Limiting

- 10 submissions per IP per problem per hour (sliding window)
- 100 submissions per IP per day (all problems combined)
- Returns HTTP 429 with `Retry-After` header

---

## Timeouts

Each verifier has a maximum execution time. If verification exceeds the timeout, the submission is rejected with error code `TIMEOUT`.

| Problem   | Timeout    |
| --------- | ---------- |
| hadamard  | 60 seconds |
| conway    | 10 seconds |
| tensor    | 30 seconds |
| stilllife | 10 seconds |
| hpprotein | 10 seconds |

---

## Configuration

**Environment variables:**

| Variable             | Description                        |
| -------------------- | ---------------------------------- |
| URL_DATABASE         | PostgreSQL connection string       |
| PORT                 | API server port (default 8080)     |
| RATE_LIMIT_PER_HOUR  | Per IP per problem (default 10)    |
| RATE_LIMIT_PER_DAY   | Per IP total (default 100)         |
| LEADERBOARD_PASSWORD | Password for `/api/v1/leaderboard` |

**Config file** (`config.json`): Stores allowed instances and current records per problem. Loaded at startup. Updated manually when records are verified.

---

## Technology Stack

- Python 3.11+ with FastAPI
- PostgreSQL 15+
- Required Python packages: sympy, numpy, fractions (stdlib)
- Synchronous verification (no task queue in MVP)
- Structured JSON logging

---

## Post-MVP

- Email verification (confirm email before accepting)
- Record notification emails
- Webhooks for record events
- RNA Inverse Folding
- API keys for trusted users with higher rate limits

---

## API Endpoints

Detailed request/response formats, error codes, and examples are in [API_ENDPOINTS.md](API_ENDPOINTS.md) (same directory).
