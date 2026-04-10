# API Test Guide (FastAPI `/docs`)

Base URL: `http://localhost:8080`
API prefix: `/api/v1`

Open Swagger UI: `http://localhost:8080/docs`

---

## 1) Endpoints with no request body

Use **Try it out** in `/docs`:

- `GET /api/v1/health`
- `GET /api/v1/problems/{problem_name}/instances`
  - Test with: `hadamard`, `conway`, `tensor`, `stilllife`, `hpprotein`, and `unknown` (error case)
- `GET /api/v1/submission/{submission_id}`
  - First get a real `submission_id` from a successful `POST /api/v1/submit`

Protected endpoint:

- `POST /api/v1/leaderboard`
  - Requires header `X-Leaderboard-Password`
  - Body shape:

```json
{
  "problem_name": "stilllife",
  "instance": { "n": 8 },
  "k": 5
}
```

---

## 2) JSON bodies for `POST /api/v1/submit`

Paste one payload at a time in `/docs`.

Notes for new schema behavior:

- Request body is now auto-generated from the `SubmitRequest` model in Swagger UI.
- Missing required body fields or invalid body shape now return HTTP `422` (FastAPI validation).

### A. Valid payload (Still Life, should pass)

```json
{
  "email": "tester@example.com",
  "problem_name": "stilllife",
  "instance": {
    "n": 8
  },
  "submission": {
    "claimed_cells": 4,
    "grid": [
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 1, 1, 0, 0, 0, 0],
      [0, 0, 1, 1, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0]
    ]
  }
}
```

### B. Valid payload (Tensor 2x2x2 with 8 multiplications, should pass)

```json
{
  "email": "tester@example.com",
  "problem_name": "tensor",
  "instance": {
    "n": 2,
    "m": 2,
    "p": 2
  },
  "submission": {
    "num_multiplications": 8,
    "U": [
      [
        [1, 0],
        [0, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [1, 0],
        [0, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 0],
        [0, 1]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 0],
        [0, 1]
      ]
    ],
    "V": [
      [
        [1, 0],
        [0, 0]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [0, 0],
        [0, 1]
      ],
      [
        [1, 0],
        [0, 0]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [0, 0],
        [0, 1]
      ]
    ],
    "W": [
      [
        [1, 0],
        [0, 0]
      ],
      [
        [1, 0],
        [0, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [0, 1],
        [0, 0]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 0],
        [1, 0]
      ],
      [
        [0, 0],
        [0, 1]
      ],
      [
        [0, 0],
        [0, 1]
      ]
    ]
  }
}
```

### C. Error test: invalid email (should return `INVALID_EMAIL`)

```json
{
  "email": "invalid-email",
  "problem_name": "stilllife",
  "instance": { "n": 8 },
  "submission": {
    "claimed_cells": 4,
    "grid": [
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 1, 1, 0, 0, 0, 0],
      [0, 0, 1, 1, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0]
    ]
  }
}
```

### D. Error test: unknown problem (should return `PROBLEM_NOT_FOUND`)

```json
{
  "email": "tester@example.com",
  "problem_name": "unknown_problem",
  "instance": {},
  "submission": {}
}
```

### E. Validation test: missing required field `submission` (should return HTTP `422`)

```json
{
  "email": "tester@example.com",
  "problem_name": "conway",
  "instance": {}
}
```

### F. Validation test: invalid `submission_id` in `GET /api/v1/submission/{submission_id}`

- Example request: `/api/v1/submission/not-a-uuid`
- Expected response: HTTP `422` (path parameter validation error)

### G. Valid payload (HP Protein warm-up, should pass)

```json
{
  "email": "tester@example.com",
  "problem_name": "hpprotein",
  "instance": { "sequence_id": "WARMUP_6H" },
  "submission": {
    "lattice": "2D",
    "coords": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 2], [1, 2]]
  }
}
```

---

## 3) Suggested full test flow in `/docs`

1. `GET /api/v1/health`
2. `GET /api/v1/problems/{problem_name}/instances` for each known problem + one unknown
3. `POST /api/v1/submit` with payload **A** (copy returned `submission_id`)
4. `GET /api/v1/submission/{submission_id}` with copied ID
5. `POST /api/v1/submit` with payload **B**
6. `POST /api/v1/submit` with payload **C** and **D** (error-path checks)
7. `POST /api/v1/submit` with payload **E** (validation-path check)
8. `POST /api/v1/submit` with payload **G** (HP warm-up)
9. `GET /api/v1/submission/not-a-uuid` (path-validation check)
10. `POST /api/v1/leaderboard` with valid password header and `{"problem_name":"stilllife","instance":{"n":8},"k":5}`
11. `POST /api/v1/leaderboard` with wrong password (expect `401 UNAUTHORIZED`)

This covers all API routes and both success/error behavior.
