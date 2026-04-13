# CAISc 2026 — Verifier API

Automated verification and scoring service for the **CAISc 2026 Verifiable Problems Track**. Participants submit candidate solutions to five long-standing open problems in mathematics, computer science, and computational biology. The API validates each solution against the exact mathematical constraints, computes a score, ranks it against all prior submissions, and returns a percentile.

**Stack:** Python 3.12 · FastAPI · PostgreSQL 18 · Docker

---

## Problems

| ID | Problem | Domain | Scoring | Instances |
|----|---------|--------|---------|-----------|
| `hadamard` | Hadamard Maximal Determinant | Linear Algebra | \|det(M)\| — higher is better | 24 values of n (23–99) |
| `conway` | Conway's 99-Graph | Graph Theory | % constraints satisfied — higher is better | Single fixed instance |
| `tensor` | Matrix Multiplication Tensor Rank | Algebraic Complexity | # scalar multiplications — lower is better | 11 size triples |
| `stilllife` | Connected Still Life | Cellular Automata | Live cell count — higher is better | n ∈ {8, 10, 16, 20, 32} |
| `hpprotein` | HP Protein Folding (2D) | Computational Biology | H-H contacts — higher is better | 7 sequences |

For full problem definitions, constraints, and submission formats see [docs/VERIFIABLE_PROBLEMS_GUIDE.md](docs/VERIFIABLE_PROBLEMS_GUIDE.md).

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.12+ for local development

### Run with Docker

```bash
# Clone and start
git clone git@github.com:Siddhartha-Mahajan/verifier.git
cd verifier

# Create .env for the API service
cat > .env <<EOF
URL_DATABASE=postgresql+asyncpg://postgres:postgres@postgres:5432/verifier
SERVICE_PORT=8080
SERVICE_HOST=0.0.0.0
SERVICE_WORKERS=8
LEADERBOARD_PASSWORD=changeme
EOF

# Start PostgreSQL + API
docker compose up -d --build

# Verify
curl http://localhost:8080/api/v1/health
```

The API will be available at `http://localhost:8080`. Swagger docs are at `/docs`.

### Run Locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export URL_DATABASE="postgresql+asyncpg://postgres:postgres@localhost:5430/verifier"
export LEADERBOARD_PASSWORD="changeme"

# Start PostgreSQL (via Docker or local install)
docker compose up -d postgres

# Initialize database and start server
python main.py
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/problems/{problem_name}/instances` | List allowed instances for a problem |
| `POST` | `/api/v1/submit` | Submit a solution for verification |
| `GET` | `/api/v1/submission/{submission_id}` | Retrieve a past submission result |
| `POST` | `/api/v1/leaderboard` | Top-k leaderboard (requires `X-Leaderboard-Password` header) |

### Submit a Solution

```bash
curl -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "problem_name": "stilllife",
    "instance": {"n": 8},
    "submission": {
      "claimed_cells": 4,
      "grid": [
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,1,1,0,0,0,0],
        [0,0,1,1,0,0,0,0],
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
  "submission_id": "d3f1a2b4-...",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "score": 4,
  "percentile": 100.0,
  "is_record": false,
  "message": "Verification passed"
}
```

For complete endpoint documentation with all problem payloads, see [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md).

### Query the Leaderboard

```bash
curl -X POST http://localhost:8080/api/v1/leaderboard \
  -H "Content-Type: application/json" \
  -H "X-Leaderboard-Password: changeme" \
  -d '{"problem_name": "stilllife", "instance": {"n": 20}, "k": 10}'
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `URL_DATABASE` | PostgreSQL connection string (`postgresql+asyncpg://...`) | — (required) |
| `SERVICE_PORT` | API server port | `8080` |
| `SERVICE_HOST` | Bind address | `0.0.0.0` |
| `SERVICE_WORKERS` | Uvicorn workers | `8` |
| `SERVICE_REFRESH` | Auto-reload on code changes | `false` |
| `ENABLE_API_DOCS` | Enable Swagger UI at `/docs` | `true` |
| `LEADERBOARD_PASSWORD` | Password for leaderboard endpoint | `lossfunk123` |
| `RATE_LIMIT_PER_SECOND` | Per-IP per-problem rate limit | `1` |
| `RATE_LIMIT_PER_MINUTE` | Per-IP per-problem rate limit | `5` |
| `RATE_LIMIT_PER_HOUR` | Per-IP per-problem rate limit | `10` |
| `RATE_LIMIT_PER_DAY` | Per-IP total rate limit | `100` |

PostgreSQL credentials are in `db.env` (used by the `postgres` Docker service).

---

## Verifiers

Each problem has a standalone verification module in `helper/`:

```python
from verifier import (
    verify_hadamard,
    verify_conway,
    verify_tensor,
    verify_stilllife,
    verify_hpprotein,
)

result = verify_stilllife(
    instance={"n": 20},
    submission={"claimed_cells": 148, "grid": [[0, 1, ...], ...]},
    current_record=148,
)
```

Every `verify_*` function returns:

```python
{
    "is_valid": bool,
    "score": int | float | None,
    "error_code": str | None,
    "error_message": str | None,
    "is_record": bool,
}
```

### Dependencies

| Package | Used by |
|---------|---------|
| `sympy` | Hadamard (exact integer determinant) |
| `numpy` | Conway (matrix operations) |
| stdlib (`fractions`, `collections`) | Tensor, Still Life, HP Protein |

---

## Testing

```bash
# Unit tests for verifier modules
python test_verifiers.py

# HP Protein-specific tests
python test_hpprotein.py

# Full API integration tests (requires running server)
python run_api_test_cases.py
```

See [docs/API_TEST_CASES.md](docs/API_TEST_CASES.md) for curl-based API test cases covering all problems and error paths.

---

## Project Structure

```
├── main.py                    # FastAPI application entry point
├── config.py                  # Environment variable loading
├── database.py                # SQLAlchemy async engine and session
├── models.py                  # Submission ORM model
├── schema.py                  # Pydantic request/response schemas
├── create_db.py               # Database table initialization
├── __init__.py                # Exports verify_* functions
├── requirements.txt           # Python dependencies
├── requirements-test.txt      # Test dependencies
├── Dockerfile                 # Container image (Python 3.12-slim)
├── docker-compose.yml         # PostgreSQL + API service stack
├── db.env                     # PostgreSQL credentials
├── .env                       # API environment variables (not committed)
│
├── helper/                    # Problem verification modules
│   ├── hadamard.py            # ±1 matrix, exact det via SymPy
│   ├── conway.py              # srg(99,14,1,2) constraint checker
│   ├── tensor.py              # Bilinear algorithm, exact rational arithmetic
│   ├── stilllife.py           # GoL stability + 8-connectivity
│   └── hpprotein.py           # HP lattice folding, H-H contacts
│
├── routers/
│   └── api_v1.py              # All /api/v1/* route handlers
│
├── hosting/
│   └── docker-compose.yml     # Production hosting config
│
├── test_verifiers.py          # Verifier unit tests
├── test_hpprotein.py          # HP Protein verifier tests
├── run_api_test_cases.py      # Automated API integration tests
│
└── docs/                      # Documentation
    ├── VERIFIER_API_SPEC.md   # Full system spec (problems, DB, config)
    ├── API_ENDPOINTS.md       # HTTP endpoint reference
    ├── API_TEST.md            # Swagger UI test guide
    ├── API_TEST_CASES.md      # Curl-based API test cases
    ├── VERIFIABLE_PROBLEMS_GUIDE.md  # Problem definitions and examples
    └── PERCENTILE_CALCULATION.md     # Scoring and percentile logic
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/VERIFIER_API_SPEC.md](docs/VERIFIER_API_SPEC.md) | Full system spec — problem definitions, database schema, rate limits, configuration |
| [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md) | HTTP endpoint reference with request/response formats |
| [docs/VERIFIABLE_PROBLEMS_GUIDE.md](docs/VERIFIABLE_PROBLEMS_GUIDE.md) | Detailed problem descriptions, constraints, allowed instances, and submission examples |
| [docs/API_TEST.md](docs/API_TEST.md) | Guide for testing via Swagger UI |
| [docs/API_TEST_CASES.md](docs/API_TEST_CASES.md) | Copy-paste curl commands for every endpoint and error path |
| [docs/PERCENTILE_CALCULATION.md](docs/PERCENTILE_CALCULATION.md) | Percentile formula, tie-breaking, and edge cases |

---

## License

Internal project — [Lossfunk](https://lossfunk.com) × CAISc 2026.
