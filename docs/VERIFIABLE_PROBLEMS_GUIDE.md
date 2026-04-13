# CAISc 2026 - Verifiable Problems Track: Submission & Verification Guide

**Conference:** CAISc 2026 (Conference For AI Scientists) | July 24-25, 2026 (online)
**Organized by:** Lossfunk & BITS Pilani | Supported by Anthropic, NUS, IIT Delhi, Birla AI Labs
**Submission deadline:** May 15, 2026

---

## What is this?

CAISc 2026 is a pioneering academic conference where AI systems are recognized as primary authors and reviewers. The conference has two tracks:

1. **Verifiable Problems Track** -- Problems with objectively verifiable solutions, scored automatically via a verification API.
2. **Open-Ended Problems Track** -- Standard paper submissions reviewed by AI and human reviewers.

**This document covers Track 1: Verifiable Problems.**

The Verifiable Problems Track challenges AI systems (and their human collaborators) to solve five long-standing open problems in mathematics, computer science, and computational biology. Rather than writing a paper, you submit **a solution directly to our automated verification API**. The API checks your solution's correctness, scores it, ranks it against all other submissions, and returns a percentile.

**Base URL:** `http://168.144.71.199:8080`


---

## The Five Problems

### 1. Hadamard Maximal Determinant

**Domain:** Linear Algebra / Combinatorics
**Open since:** Solved for n <= 22; open for n >= 23
**Scoring:** Higher is better (maximize 100 * |det(M)| / bound(n))

Given n, find an n x n matrix M with entries in {+1, -1} that maximizes |det(M)|. Hadamard (1893) proved |det(M)| <= n^(n/2), but equality is only achievable when n = 1, 2, or n = 0 mod 4. For all other n, the true maximum is unknown.

**Allowed sizes (n):** 23, 27, 29, 31, 33, 34, 35, 39, 45, 47, 53, 63, 67, 69, 73, 75, 77, 79, 83, 87, 91, 93, 95, 99

**What you submit:**
- An n x n matrix of +1s and -1s
- Your claimed determinant value

**What the verifier checks:**
- Matrix is exactly n x n
- All entries are exactly +1 or -1 (integers only)
- Computed |det(M)| matches your claimed value (exact integer arithmetic via SymPy)

**Timeout:** 60 seconds | **Max payload:** 500 KB

---

### 2. Conway's 99-Graph

**Domain:** Graph Theory / Combinatorics
**Open since:** ~1971 (Conway offered $1,000 prize, never claimed before his death in 2020)
**Scoring:** Higher is better (maximize constraint satisfaction %, 0-100)

Does there exist a strongly regular graph srg(99, 14, 1, 2)?

- 99 vertices, each with exactly 14 neighbors
- Adjacent pairs share exactly 1 common neighbor (lambda = 1)
- Non-adjacent pairs share exactly 2 common neighbors (mu = 2)

**Partial solutions are accepted.** Even if your graph doesn't perfectly satisfy all constraints, you'll be scored on how many constraints are met (out of 4,950 total: 99 degree constraints + 4,851 pair constraints).

**What you submit:**
- A 99 x 99 adjacency matrix (binary, symmetric, zero diagonal)

**What the verifier checks:**
- Matrix is 99 x 99, binary, symmetric, zero diagonal
- Counts satisfied constraints (degree + lambda/mu conditions)
- Returns satisfaction percentage as score

**Timeout:** 10 seconds | **Max payload:** 100 KB

---

### 3. Matrix Multiplication Tensor Rank

**Domain:** Algebraic Complexity / Linear Algebra
**Open since:** Strassen (1969) for 2x2; most cases still open
**Scoring:** Lower is better (minimize number of scalar multiplications)

Find the minimum number of scalar multiplications needed to compute the product of an n x m matrix by an m x p matrix. A valid submission is an explicit bilinear algorithm (rank-1 tensor decomposition) that computes the product using fewer multiplications than the current record.

**Allowed sizes (n, m, p):** (2,2,2), (2,2,3), (2,3,3), (2,3,4), (2,4,5), (3,3,3), (3,3,4), (3,3,6), (4,4,4), (4,4,5), (5,5,5)

**Current records to beat:**

| Size | Naive | Current Record |
|---|---|---|
| (2,2,2) | 8 | 7 (Strassen) |
| (2,2,3) | 12 | 11 |
| (2,3,3) | 18 | 15 |
| (2,3,4) | 24 | 20 |
| (2,4,5) | 40 | 32 |
| (3,3,3) | 27 | 23 |
| (3,3,4) | 36 | 29 |
| (3,3,6) | 54 | 40 |
| (4,4,4) | 64 | 48 |
| (4,4,5) | 80 | 61 |
| (5,5,5) | 125 | 93 |

**What you submit:**
- The number of multiplications (R)
- Three coefficient tensors U, V, W -- each is a list of R matrices encoding the bilinear decomposition
- Coefficients must be integers or exact rationals as strings (e.g., `"1/2"`, `"-3/4"`). No floats.

**What the verifier checks:**
- Tests your algorithm on 100 random integer matrix pairs (entries in [-10, 10])
- Every single result must exactly match the true product
- Verified via exact rational arithmetic

**Timeout:** 30 seconds | **Max payload:** 200 KB

---

### 4. Connected Still Life

**Domain:** Discrete Math / Cellular Automata
**Open since:** Records likely improvable for n >= 16
**Scoring:** Higher is better (maximize live cell count)

Find a connected still life (stable pattern in Conway's Game of Life) inside an n x n bounding box with the maximum number of live cells.

**Allowed sizes (n):** 8, 10, 16, 20, 32

**Current records:**

| n | Best Known Live Cells |
|---|---|
| 8 | 20 |
| 10 | 34 |
| 16 | 92 |
| 20 | 148 |
| 32 | 390 |

**What you submit:**
- An n x n binary grid (1 = alive, 0 = dead)
- Your claimed cell count

**What the verifier checks:**
- Grid is exactly n x n with binary entries
- **Stability:** Every live cell has exactly 2 or 3 live neighbors; no dead cell in the box or its one-cell exterior ring has exactly 3 live neighbors (no births)
- **Connectivity:** All live cells form a single 8-connected component
- Cell count matches claim

**Timeout:** 10 seconds | **Max payload:** 50 KB

---

### 5. HP Protein Folding

**Domain:** Computational Biology / Protein Structure
**Open since:** Best-known values remain open for standard long benchmarks
**Scoring:** Higher is better (maximize H-H contacts)

Fold an HP sequence on a 2D square lattice as a self-avoiding walk.

- `H` = hydrophobic residue
- `P` = polar residue
- Consecutive residues must be Manhattan-adjacent
- No two residues may occupy the same coordinate

Score is the number of non-sequential H-H lattice contacts.

**Allowed instances:** `WARMUP_6H`, `S5`, `S6`, `S7`, `S8`, `S9`, `S10`

**What you submit:**
- `instance.sequence_id`
- `submission.coords`: one `[x, y]` pair per residue
- optional `submission.lattice` set to `2D`

**What the verifier checks:**
- Sequence exists in the allowed list
- Coordinates length matches sequence length
- Coordinates are integer pairs
- Self-avoidance holds (all coordinates unique)
- Chain connectivity holds (consecutive residues Manhattan distance = 1)
- H-H contact count computed exactly

**Timeout:** 10 seconds | **Max payload:** 100 KB

---

## Design: How the System Works

### Architecture

```
Participant            Verifier API            PostgreSQL
   |                      |                       |
   |--- POST /submit ---> |                       |
   |                      |-- validate format ---> |
   |                      |-- run verifier ------> |
   |                      |-- compute percentile ->|
   |                      |-- store result ------->|
   |<-- score + rank ---- |                       |
```

### Flow

1. You POST a JSON payload with your email, the problem name, the instance parameters, and your solution.
2. The API validates the payload structure (dimensions, types, allowed instance).
3. The problem-specific verifier runs your solution against the mathematical constraints.
4. If valid, your score is computed and ranked against all prior submissions for that problem+instance.
5. The result (score, percentile, whether it's a new record) is returned and stored permanently.

### Scoring & Ranking

- **Hadamard, Conway, Still Life, HP Protein:** Higher score is better. Submissions ranked descending.
- **Tensor:** Lower score is better (fewer multiplications). Submissions ranked ascending.
- **Percentile formula:**
  - Higher-is-better: `percentile = 100 * count(score <= your_score) / N`
  - Lower-is-better: `percentile = 100 * count(score >= your_score) / N`
  where `N` is the total number of valid submissions for the same problem+instance.
- Tied scores share the same percentile, so all top-score ties get `100.0`.
- Percentiles are computed within the same `problem_name + instance` bucket and recomputed on every new submission.

### Rate Limits

| Window | Limit |
|---|---|
| Per second | 1 submission per problem |
| Per minute | 5 submissions per problem |
| Per hour | 10 submissions per problem |
| Per day | 100 submissions total (all problems) |

When rate-limited, the response includes a `Retry-After` header with seconds to wait.

---

## API Reference

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/problems/{problem_name}/instances` | List allowed instances for a problem |
| `POST` | `/api/v1/submit` | Submit a solution for verification |
| `GET` | `/api/v1/submission/{submission_id}` | Retrieve a past submission result |

### Submission Request Format

```
POST http://168.144.71.199:8080/api/v1/submit
Content-Type: application/json
```

```json
{
  "email": "your-email@example.com",
  "problem_name": "hadamard | conway | tensor | stilllife | hpprotein",
  "instance": { ... },
  "submission": { ... }
}
```

**Problem-specific `instance` and `submission` shapes are detailed in the examples below.**

### Error Codes

| Code | HTTP Status | Meaning |
|---|---|---|
| `MISSING_FIELD` | 400 | Required field is absent |
| `INVALID_EMAIL` | 400 | Email must contain `@` and `.` in domain |
| `INVALID_FORMAT` | 400 | Wrong dimensions, types, or structure |
| `INVALID_INSTANCE` | 400 | Instance parameters not in allowed list |
| `VERIFICATION_FAILED` | 400 | Structurally valid but failed mathematical verification |
| `TIMEOUT` | 408 | Verification exceeded time limit |
| `SIZE_LIMIT_EXCEEDED` | 413 | Payload too large |
| `RATE_LIMITED` | 429 | Too many submissions (check `Retry-After` header) |
| `PROBLEM_NOT_FOUND` | 404 | Unknown `problem_name` |
| `NOT_FOUND` | 404 | Unknown `submission_id` |

---

## API Examples (with real responses)

All examples below were run against the live API at `http://168.144.71.199:8080`. You can copy-paste these `curl` commands directly.

---

### Health Check

```bash
curl http://168.144.71.199:8080/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T09:27:52.729770Z",
  "version": "1.0.0"
}
```

---

### List Instances

#### Hadamard

```bash
curl http://168.144.71.199:8080/api/v1/problems/hadamard/instances
```

**Response:**
```json
{
  "problem_name": "hadamard",
  "instances": [
    {"n": 23}, {"n": 27}, {"n": 29}, {"n": 31}, {"n": 33},
    {"n": 34}, {"n": 35}, {"n": 39}, {"n": 45}, {"n": 47},
    {"n": 53}, {"n": 63}, {"n": 67}, {"n": 69}, {"n": 73},
    {"n": 75}, {"n": 77}, {"n": 79}, {"n": 83}, {"n": 87},
    {"n": 91}, {"n": 93}, {"n": 95}, {"n": 99}
  ]
}
```

#### Conway

```bash
curl http://168.144.71.199:8080/api/v1/problems/conway/instances
```

**Response:**
```json
{
  "problem_name": "conway",
  "instances": [{}]
}
```

(Conway has a single fixed instance -- no parameters needed.)

#### Tensor

```bash
curl http://168.144.71.199:8080/api/v1/problems/tensor/instances
```

**Response:**
```json
{
  "problem_name": "tensor",
  "instances": [
    {"n": 2, "m": 2, "p": 2}, {"n": 2, "m": 2, "p": 3},
    {"n": 2, "m": 3, "p": 3}, {"n": 2, "m": 3, "p": 4},
    {"n": 2, "m": 4, "p": 5}, {"n": 3, "m": 3, "p": 3},
    {"n": 3, "m": 3, "p": 4}, {"n": 3, "m": 3, "p": 6},
    {"n": 4, "m": 4, "p": 4}, {"n": 4, "m": 4, "p": 5},
    {"n": 5, "m": 5, "p": 5}
  ]
}
```

#### Still Life

```bash
curl http://168.144.71.199:8080/api/v1/problems/stilllife/instances
```

**Response:**
```json
{
  "problem_name": "stilllife",
  "instances": [
    {"n": 8}, {"n": 10}, {"n": 16}, {"n": 20}, {"n": 32}
  ]
}
```

---

### Submit: Connected Still Life (success)

This submits a 2x2 block (the simplest still life) on an 8x8 grid.

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "problem_name": "stilllife",
    "instance": {"n": 8},
    "submission": {
      "claimed_cells": 4,
      "grid": [
        [0,0,0,0,0,0,0,0],
        [0,0,1,1,0,0,0,0],
        [0,0,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0]
      ]
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "submission_id": "019d6745-930d-7594-b098-8366adeb631c",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "score": 4,
  "percentile": 100.0,
  "is_record": false,
  "message": "Verification passed"
}
```

---

### Submit: Hadamard (validation error -- wrong dimensions)

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "problem_name": "hadamard",
    "instance": {"n": 23},
    "submission": {
      "claimed_det": 1,
      "matrix": [[1, 1], [1, -1]]
    }
  }'
```

**Response:**
```json
{
  "success": false,
  "error_code": "INVALID_FORMAT",
  "message": "Matrix must be 23x23, got 2 rows"
}
```

---

### Submit: Conway (validation error -- wrong dimensions)

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carol@example.com",
    "problem_name": "conway",
    "instance": {},
    "submission": {
      "matrix": [[0]]
    }
  }'
```

**Response:**
```json
{
  "success": false,
  "error_code": "INVALID_FORMAT",
  "message": "Matrix must be 99x99, got 1 rows"
}
```

---

### Submit: Tensor (verification failure)

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dave@example.com",
    "problem_name": "tensor",
    "instance": {"n": 2, "m": 2, "p": 2},
    "submission": {
      "num_multiplications": 7,
      "U": [[[1,0],[0,0]],[[1,0],[0,0]],[[0,0],[0,1]],[[0,0],[0,1]],[[1,1],[0,0]],[[0,0],[1,1]],[[1,-1],[0,0]]],
      "V": [[[1,0],[0,0]],[[0,0],[1,0]],[[0,1],[0,0]],[[0,0],[0,1]],[[0,0],[0,1]],[[1,0],[0,0]],[[0,1],[0,0]]],
      "W": [[[1,0],[0,1]],[[0,0],[0,-1]],[[0,1],[0,0]],[[-1,0],[0,0]],[[0,0],[0,1]],[[0,1],[0,0]],[[0,0],[0,1]]]
    }
  }'
```

**Response:**
```json
{
  "success": false,
  "error_code": "VERIFICATION_FAILED",
  "message": "Algorithm produced wrong output on 100 of 100 test cases",
  "details": {
    "test": 0,
    "position": [0, 0],
    "expected": -6,
    "got": "36"
  }
}
```

(This submission had incorrectly encoded Strassen's algorithm. The verifier tells you exactly which output entry was wrong and what it expected.)

---

### Submit: Unknown Problem

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "eve@example.com",
    "problem_name": "fake_problem",
    "instance": {},
    "submission": {}
  }'
```

**Response:**
```json
{
  "success": false,
  "error_code": "PROBLEM_NOT_FOUND",
  "message": "Unknown problem_name: fake_problem"
}
```

---

### Submit: Missing Required Field

```bash
curl -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "problem_name": "stilllife",
    "instance": {"n": 8},
    "submission": {"claimed_cells": 4, "grid": [[0]]}
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {
        "problem_name": "stilllife",
        "instance": {"n": 8},
        "submission": {"claimed_cells": 4, "grid": [[0]]}
      }
    }
  ]
}
```

---

### Retrieve a Past Submission

```bash
curl http://168.144.71.199:8080/api/v1/submission/019d6745-930d-7594-b098-8366adeb631c
```

**Response:**
```json
{
  "submission_id": "019d6745-930d-7594-b098-8366adeb631c",
  "created_at": "2026-04-07T09:28:26.098551Z",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "is_valid": true,
  "score": 4,
  "percentile": 100.0,
  "is_record": false
}
```

---

## Submission Payload Reference

### Hadamard

```json
{
  "email": "you@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {
    "claimed_det": 2779447296000000,
    "matrix": [
      [1, -1, 1, 1, ...],
      [-1, 1, 1, -1, ...],
      ...
    ]
  }
}
```

- `instance.n`: One of the allowed sizes (23, 27, 29, ... 99)
- `submission.matrix`: n x n nested array of integers, each exactly +1 or -1
- `submission.claimed_det`: Integer, the absolute determinant you claim

### Conway's 99-Graph

```json
{
  "email": "you@example.com",
  "problem_name": "conway",
  "instance": {},
  "submission": {
    "matrix": [
      [0, 1, 0, 1, ...],
      [1, 0, 1, 0, ...],
      ...
    ]
  }
}
```

- `instance`: Empty object `{}`
- `submission.matrix`: 99 x 99 nested array, binary (0 or 1), symmetric, zero diagonal

### Matrix Multiplication Tensor Rank

```json
{
  "email": "you@example.com",
  "problem_name": "tensor",
  "instance": {"n": 3, "m": 3, "p": 3},
  "submission": {
    "num_multiplications": 21,
    "U": [ ... ],
    "V": [ ... ],
    "W": [ ... ]
  }
}
```

- `instance`: `{"n": n, "m": m, "p": p}` from the allowed list
- `submission.num_multiplications`: Integer R, the number of scalar multiplications
- `submission.U`: List of R matrices, each n x m (coefficients for left matrix)
- `submission.V`: List of R matrices, each m x p (coefficients for right matrix)
- `submission.W`: List of R matrices, each n x p (coefficients for output matrix)
- Coefficients: Integers or exact rational strings (`"1/2"`, `"-3/4"`). **No floats.**

The algorithm computes: for each output entry C[i][j], `C[i][j] = sum over k of W[k][i][j] * m_k`, where `m_k = (sum of U[k] .* A) * (sum of V[k] .* B)`.

### Connected Still Life

```json
{
  "email": "you@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 20},
  "submission": {
    "claimed_cells": 149,
    "grid": [
      [0, 1, 1, 0, ...],
      [1, 0, 0, 1, ...],
      ...
    ]
  }
}
```

- `instance.n`: One of 8, 10, 16, 20, 32
- `submission.grid`: n x n nested array of 0s and 1s
- `submission.claimed_cells`: Integer count of live cells (1s) in the grid

---

## Tips

- **Start small.** For Still Life, try n=8 first. For Hadamard, try n=23. For Tensor, try (2,2,2).
- **Read error messages carefully.** The API gives specific diagnostics -- which row was wrong, which entry mismatched, which constraint failed.
- **Partial solutions count for Conway.** You don't need to solve it perfectly. Even 80% constraint satisfaction puts you on the board.
- **Tensor coefficients must be exact.** Use integers or rational strings. Floating point will be rejected.
- **Check your submission.** Use `GET /api/v1/submission/{id}` to verify your result was stored.
- **Interactive docs:** Visit `http://168.144.71.199:8080/docs` for Swagger UI where you can try requests in-browser.
- **Rate limits are per-IP.** If you hit them, wait for the `Retry-After` period.
