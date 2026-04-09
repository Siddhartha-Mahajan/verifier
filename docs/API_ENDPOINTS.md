# CAISc 2026 Verifiable Problems -- API Endpoints

All endpoints are under `/api/v1/`. Content-Type is `application/json` for all requests and responses.

---

## POST /api/v1/submit

Submit a solution for verification.

### Request

| Field        | Type   | Required | Description                                                                          |
| ------------ | ------ | -------- | ------------------------------------------------------------------------------------ |
| email        | string | Yes      | Submitter's email (format: contains @ and a dot after it)                            |
| problem_name | string | Yes      | One of: hadamard, conway, tensor, stilllife, hpprotein                               |
| instance     | object | Depends  | Problem parameters (required for hadamard, tensor, stilllife, hpprotein; empty `{}` for conway) |
| submission   | object | Yes      | Problem-specific solution payload                                                    |

### Submission Payloads by Problem

**Hadamard:**

```json
{
  "email": "alice@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {
    "claimed_det": 2779447296000000,
    "matrix": [[1, -1, 1, ...], [-1, 1, 1, ...], ...]
  }
}
```

**Conway:**

```json
{
  "email": "bob@example.com",
  "problem_name": "conway",
  "instance": {},
  "submission": {
    "matrix": [[0, 1, 0, ...], [1, 0, 1, ...], ...]
  }
}
```

**Tensor:**

```json
{
  "email": "carol@example.com",
  "problem_name": "tensor",
  "instance": {"n": 2, "m": 2, "p": 2},
  "submission": {
    "num_multiplications": 7,
    "U": [[[1, 0], [0, 0]], ...],
    "V": [[[0, 0], [0, 1]], ...],
    "W": [[[1, 0], [0, 0]], ...]
  }
}
```

Coefficients in U, V, W must be integers or exact rational strings like `"1/2"`. No floats.

**Still Life:**

```json
{
  "email": "dave@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 20},
  "submission": {
    "claimed_cells": 149,
    "grid": [[0, 1, 1, 0, ...], [1, 0, 0, 1, ...], ...]
  }
}
```

**HP Protein Folding:**

```json
{
  "email": "erin@example.com",
  "problem_name": "hpprotein",
  "instance": {"sequence_id": "S5"},
  "submission": {
    "lattice": "2D",
    "coords": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 2], ...]
  }
}
```

Rules checked: self-avoiding walk, consecutive lattice adjacency, and H-H contact counting.

### Success Response (200)

```json
{
  "success": true,
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "problem_name": "hadamard",
  "instance": { "n": 23 },
  "score": 2779447296000000,
  "percentile": 87.5,
  "is_record": false,
  "message": "Verification passed"
}
```

### Failure Response (400)

```json
{
  "success": false,
  "error_code": "VERIFICATION_FAILED",
  "message": "Claimed determinant 1000 does not match computed |det| = 999",
  "field": "submission.claimed_det",
  "details": {
    "claimed": 1000,
    "computed": 999
  }
}
```

For Conway partial failures (valid structure but imperfect score), the response is still 200 with the score:

```json
{
  "success": true,
  "submission_id": "...",
  "problem_name": "conway",
  "instance": {},
  "score": 98.73,
  "percentile": 95.2,
  "is_record": true,
  "message": "Verification passed. 4887 of 4950 constraints satisfied."
}
```

---

## GET /api/v1/submission/{submission_id}

Retrieve a past submission result. Percentile is recalculated within the same `problem_name + instance` bucket.

### Response (200)

```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-15T10:30:00Z",
  "problem_name": "hadamard",
  "instance": { "n": 23 },
  "is_valid": true,
  "score": 2779447296000000,
  "percentile": 87.5,
  "is_record": false
}
```

### Response (404)

```json
{
  "error_code": "NOT_FOUND",
  "message": "Submission not found"
}
```

---

## GET /api/v1/problems/{problem_name}/instances

List allowed instance parameters for a problem.

### Response (200)

```json
{
  "problem_name": "hadamard",
  "instances": [{ "n": 23 }, { "n": 27 }, { "n": 29 }]
}
```

For conway: `{"problem_name": "conway", "instances": [{}]}`

For tensor: `{"problem_name": "tensor", "instances": [{"n":2,"m":2,"p":2}, {"n":2,"m":2,"p":3}, ...]}`

For hpprotein: `{"problem_name": "hpprotein", "instances": [{"sequence_id":"WARMUP_6H"}, {"sequence_id":"S5"}, ..., {"sequence_id":"S10"}]}`

### Response (404)

```json
{
  "error_code": "PROBLEM_NOT_FOUND",
  "message": "Unknown problem_name: foo"
}
```

---

## POST /api/v1/leaderboard

Return top-k submissions for a specific `problem_name + instance` bucket.

### Headers

| Header | Required | Description |
| ------ | -------- | ----------- |
| X-Leaderboard-Password | Yes | Password for protected leaderboard access |

### Request

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| problem_name | string | Yes | One of: hadamard, conway, tensor, stilllife, hpprotein |
| instance | object | Yes | Instance object for the selected problem |
| k | integer | No | Number of results to return (default 10, min 1, max 200) |

```json
{
  "problem_name": "hpprotein",
  "instance": { "sequence_id": "S5" },
  "k": 5
}
```

### Response (200)

```json
{
  "success": true,
  "problem_name": "hpprotein",
  "instance": { "sequence_id": "S5" },
  "k": 5,
  "returned": 2,
  "entries": [
    {
      "submission_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-04-15T10:30:00Z",
      "email": "alice@example.com",
      "ip_address": "203.0.113.42",
      "problem_name": "hpprotein",
      "instance": { "sequence_id": "S5" },
      "submission": { "lattice": "2D", "coords": [[0, 0], [1, 0], [1, 1]] },
      "is_valid": true,
      "score": 23,
      "score_direction": "high",
      "error_message": null,
      "percentile": 95.2381,
      "is_record": false
    }
  ]
}
```

### Response (401)

```json
{
  "success": false,
  "error_code": "UNAUTHORIZED",
  "message": "Invalid leaderboard password"
}
```

---

## GET /api/v1/health

### Response (200)

```json
{
  "status": "healthy",
  "timestamp": "2026-04-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Error Codes

| Code                | HTTP Status | When                                                                       |
| ------------------- | ----------- | -------------------------------------------------------------------------- |
| MISSING_FIELD       | 400         | Required field absent                                                      |
| INVALID_EMAIL       | 400         | Email format invalid                                                       |
| INVALID_FORMAT      | 400         | Submission structure wrong (bad dimensions, wrong entry types)             |
| INVALID_INSTANCE    | 400         | Instance parameters not in allowed list                                    |
| INVALID_K           | 400         | Leaderboard `k` must be within allowed bounds                              |
| VERIFICATION_FAILED | 400         | Structure valid but verification check failed (e.g., determinant mismatch) |
| TIMEOUT             | 408         | Verification exceeded time limit                                           |
| SIZE_LIMIT_EXCEEDED | 413         | Payload too large                                                          |
| RATE_LIMITED        | 429         | Too many submissions (includes Retry-After header)                         |
| UNAUTHORIZED        | 401         | Missing or incorrect leaderboard password                                   |
| PROBLEM_NOT_FOUND   | 404         | Unknown problem_name                                                       |
| NOT_FOUND           | 404         | Unknown submission_id                                                      |

---

## Rate Limiting

When rate limited, the response includes:

```
HTTP 429 Too Many Requests
Retry-After: 3600

{
  "success": false,
  "error_code": "RATE_LIMITED",
  "message": "Rate limit exceeded: 10 submissions per hour per problem",
  "retry_after_seconds": 3600
}
```
