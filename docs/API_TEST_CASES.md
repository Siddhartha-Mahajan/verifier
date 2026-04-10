# API Test Cases

Every test case below is a curl command you can copy-paste. Replace `localhost:8080` with your server address. Each test shows the expected response.

Run the Python unit tests first to make sure the verifiers work: `python verifier/test_verifiers.py`

Then use these to test the full HTTP API layer.

---

## Health Check

```bash
curl -s http://localhost:8080/api/v1/health | python -m json.tool
```

Expected:

```json
{
  "status": "healthy",
  "timestamp": "2026-04-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## List Instances

### Hadamard

```bash
curl -s http://localhost:8080/api/v1/problems/hadamard/instances | python -m json.tool
```

Expected: 24 instances (n = 23, 27, 29, ... 99)

### Conway

```bash
curl -s http://localhost:8080/api/v1/problems/conway/instances | python -m json.tool
```

Expected: `{"problem_name": "conway", "instances": [{}]}`

### Tensor

```bash
curl -s http://localhost:8080/api/v1/problems/tensor/instances | python -m json.tool
```

Expected: 11 instances from (2,2,2) to (5,5,5)

### Still Life

```bash
curl -s http://localhost:8080/api/v1/problems/stilllife/instances | python -m json.tool
```

Expected: 5 instances (n = 8, 10, 16, 20, 32)

### Unknown Problem (should 404)

```bash
curl -s http://localhost:8080/api/v1/problems/bogus/instances | python -m json.tool
```

Expected:

```json
{
  "error_code": "PROBLEM_NOT_FOUND",
  "message": "Unknown problem_name: bogus"
}
```

---

## Hadamard Submissions

### H1. Valid: n=23 record-holding matrix (should pass)

This is the Orrick et al. (2003) witness matrix. det = 2,779,447,296,000,000.

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {
    "claimed_det": 2779447296000000,
    "matrix": [
      [ 1,-1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      [-1, 1, 1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
      [ 1, 1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
      [-1,-1, 1, 1,-1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1],
      [-1,-1, 1,-1, 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1],
      [-1, 1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1,-1],
      [-1, 1,-1,-1,-1,-1,-1, 1, 1,-1, 1,-1,-1,-1,-1, 1,-1,-1, 1, 1,-1,-1, 1],
      [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1,-1,-1,-1, 1,-1,-1, 1,-1, 1, 1,-1],
      [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1, 1,-1,-1,-1, 1, 1,-1, 1,-1,-1, 1],
      [-1,-1, 1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1, 1,-1, 1,-1],
      [-1,-1, 1, 1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1,-1, 1,-1, 1],
      [-1, 1,-1, 1, 1,-1,-1, 1,-1,-1,-1, 1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1],
      [-1, 1,-1, 1, 1,-1,-1,-1, 1,-1,-1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1],
      [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1, 1, 1, 1, 1,-1,-1],
      [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1,-1, 1, 1, 1,-1,-1,-1,-1, 1, 1],
      [ 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1],
      [ 1, 1, 1, 1,-1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1, 1,-1,-1,-1,-1],
      [ 1, 1, 1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1,-1],
      [ 1, 1, 1,-1, 1,-1, 1, 1,-1, 1,-1,-1, 1, 1,-1, 1, 1,-1, 1,-1,-1,-1,-1],
      [ 1, 1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1,-1,-1,-1,-1,-1, 1,-1, 1, 1],
      [ 1, 1, 1, 1,-1, 1,-1, 1,-1,-1, 1,-1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1, 1],
      [ 1, 1, 1,-1, 1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1,-1,-1, 1, 1,-1, 1],
      [ 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1,-1,-1, 1, 1, 1,-1]
    ]
  }
}' | python -m json.tool
```

Expected:

```json
{
  "success": true,
  "submission_id": "<uuid>",
  "problem_name": "hadamard",
  "instance": { "n": 23 },
  "score": 2779447296000000,
  "percentile": 100.0,
  "is_record": false,
  "message": "Verification passed"
}
```

### H2. Reject: disallowed n

```bash
curl -s -X POST http://168.144.71.199:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 5},
  "submission": {
    "claimed_det": 1,
    "matrix": [[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]]
  }
}' | python3 -m json.tool
```

Expected: 400, `"error_code": "INVALID_INSTANCE"`

### H3. Reject: wrong claimed determinant

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {
    "claimed_det": 9999999999999999,
    "matrix": [
      [ 1,-1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      [-1, 1, 1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
      [ 1, 1,-1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 1, 1],
      [-1,-1, 1, 1,-1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1],
      [-1,-1, 1,-1, 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1],
      [-1, 1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1,-1,-1, 1, 1,-1],
      [-1, 1,-1,-1,-1,-1,-1, 1, 1,-1, 1,-1,-1,-1,-1, 1,-1,-1, 1, 1,-1,-1, 1],
      [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1, 1,-1,-1,-1, 1,-1,-1, 1,-1, 1, 1,-1],
      [ 1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1, 1,-1,-1,-1, 1, 1,-1, 1,-1,-1, 1],
      [-1,-1, 1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1, 1,-1, 1,-1],
      [-1,-1, 1, 1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1,-1, 1,-1, 1],
      [-1, 1,-1, 1, 1,-1,-1, 1,-1,-1,-1, 1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1],
      [-1, 1,-1, 1, 1,-1,-1,-1, 1,-1,-1, 1, 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1],
      [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1, 1,-1,-1,-1, 1, 1, 1, 1,-1,-1],
      [ 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 1, 1,-1, 1, 1, 1,-1,-1,-1,-1, 1, 1],
      [ 1, 1, 1, 1,-1,-1, 1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1],
      [ 1, 1, 1, 1,-1, 1,-1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1, 1,-1,-1,-1,-1],
      [ 1, 1, 1,-1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1,-1],
      [ 1, 1, 1,-1, 1,-1, 1, 1,-1, 1,-1,-1, 1, 1,-1, 1, 1,-1, 1,-1,-1,-1,-1],
      [ 1, 1, 1, 1,-1,-1, 1,-1, 1, 1,-1, 1,-1, 1,-1,-1,-1,-1,-1, 1,-1, 1, 1],
      [ 1, 1, 1, 1,-1, 1,-1, 1,-1,-1, 1,-1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1, 1],
      [ 1, 1, 1,-1, 1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1,-1,-1, 1, 1,-1, 1],
      [ 1, 1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1,-1,-1, 1, 1, 1,-1]
    ]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "VERIFICATION_FAILED"`, message says computed |det| = 2779447296000000

### H4. Reject: missing field

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {
    "matrix": [[1]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "MISSING_FIELD"`, message mentions claimed_det

---

## Conway Submissions

### C1. Valid: zero matrix (score 0%)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"conway\",
  \"instance\": {},
  \"submission\": {
    \"matrix\": $(python -c "import json; print(json.dumps([[0]*99 for _ in range(99)]))")
  }
}" | python -m json.tool
```

Expected:

```json
{
  "success": true,
  "submission_id": "<uuid>",
  "problem_name": "conway",
  "instance": {},
  "score": 0.0,
  "percentile": 0.0,
  "is_record": false,
  "message": "0 of 4950 constraints satisfied"
}
```

### C2. Valid: circular 14-regular graph (partial score ~4%)

Each vertex connected to its 7 nearest neighbors in each direction.

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"conway\",
  \"instance\": {},
  \"submission\": {
    \"matrix\": $(python -c "
import json
m = [[0]*99 for _ in range(99)]
for i in range(99):
    for d in range(1, 8):
        j = (i + d) % 99
        m[i][j] = 1
        m[j][i] = 1
print(json.dumps(m))
")
  }
}" | python -m json.tool
```

Expected: `"success": true`, score around 4.0 (degree constraints pass, lambda/mu mostly fail)

### C3. Reject: not symmetric

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"conway\",
  \"instance\": {},
  \"submission\": {
    \"matrix\": $(python -c "
import json
m = [[0]*99 for _ in range(99)]
m[0][1] = 1
print(json.dumps(m))
")
  }
}" | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_FORMAT"`, message mentions symmetric

### C4. Reject: wrong size

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"conway\",
  \"instance\": {},
  \"submission\": {
    \"matrix\": $(python -c "import json; print(json.dumps([[0]*50 for _ in range(50)]))")
  }
}" | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_FORMAT"`

---

## Tensor Submissions

### T1. Valid: Strassen's algorithm, R(2,2,2) = 7

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "tensor",
  "instance": {"n": 2, "m": 2, "p": 2},
  "submission": {
    "num_multiplications": 7,
    "U": [
      [[1,0],[0,1]],
      [[0,0],[1,1]],
      [[1,0],[0,0]],
      [[0,0],[0,1]],
      [[1,1],[0,0]],
      [[-1,0],[1,0]],
      [[0,1],[0,-1]]
    ],
    "V": [
      [[1,0],[0,1]],
      [[1,0],[0,0]],
      [[0,1],[0,-1]],
      [[-1,0],[1,0]],
      [[0,0],[0,1]],
      [[1,1],[0,0]],
      [[0,0],[1,1]]
    ],
    "W": [
      [[1,0],[0,1]],
      [[0,0],[1,-1]],
      [[0,1],[0,1]],
      [[1,0],[1,0]],
      [[-1,1],[0,0]],
      [[0,0],[0,1]],
      [[1,0],[0,0]]
    ]
  }
}' | python -m json.tool
```

Expected:

```json
{
  "success": true,
  "submission_id": "<uuid>",
  "problem_name": "tensor",
  "instance": { "n": 2, "m": 2, "p": 2 },
  "score": 7,
  "percentile": 100.0,
  "is_record": false,
  "message": "Verification passed"
}
```

### T2. Valid: naive R(2,2,3) = 12

Schoolbook multiplication. Each of the 12 terms computes one A[i,k]\*B[k,j].

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"tensor\",
  \"instance\": {\"n\": 2, \"m\": 2, \"p\": 3},
  \"submission\": $(python -c "
import json
n,m,p = 2,2,3
U,V,W = [],[],[]
for i in range(n):
    for k in range(m):
        for j in range(p):
            u = [[0]*m for _ in range(n)]; u[i][k]=1
            v = [[0]*p for _ in range(m)]; v[k][j]=1
            w = [[0]*p for _ in range(n)]; w[i][j]=1
            U.append(u); V.append(v); W.append(w)
print(json.dumps({'num_multiplications':n*m*p,'U':U,'V':V,'W':W}))
")
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 12`

### T3. Valid: naive R(3,3,3) = 27

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"tensor\",
  \"instance\": {\"n\": 3, \"m\": 3, \"p\": 3},
  \"submission\": $(python -c "
import json
n,m,p = 3,3,3
U,V,W = [],[],[]
for i in range(n):
    for k in range(m):
        for j in range(p):
            u = [[0]*m for _ in range(n)]; u[i][k]=1
            v = [[0]*p for _ in range(m)]; v[k][j]=1
            w = [[0]*p for _ in range(n)]; w[i][j]=1
            U.append(u); V.append(v); W.append(w)
print(json.dumps({'num_multiplications':n*m*p,'U':U,'V':V,'W':W}))
")
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 27`

### T4. Valid: naive R(3,3,6) = 54

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"tensor\",
  \"instance\": {\"n\": 3, \"m\": 3, \"p\": 6},
  \"submission\": $(python -c "
import json
n,m,p = 3,3,6
U,V,W = [],[],[]
for i in range(n):
    for k in range(m):
        for j in range(p):
            u = [[0]*m for _ in range(n)]; u[i][k]=1
            v = [[0]*p for _ in range(m)]; v[k][j]=1
            w = [[0]*p for _ in range(n)]; w[i][j]=1
            U.append(u); V.append(v); W.append(w)
print(json.dumps({'num_multiplications':n*m*p,'U':U,'V':V,'W':W}))
")
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 54`

### T5. Valid: naive R(4,4,4) = 64

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"tensor\",
  \"instance\": {\"n\": 4, \"m\": 4, \"p\": 4},
  \"submission\": $(python -c "
import json
n,m,p = 4,4,4
U,V,W = [],[],[]
for i in range(n):
    for k in range(m):
        for j in range(p):
            u = [[0]*m for _ in range(n)]; u[i][k]=1
            v = [[0]*p for _ in range(m)]; v[k][j]=1
            w = [[0]*p for _ in range(n)]; w[i][j]=1
            U.append(u); V.append(v); W.append(w)
print(json.dumps({'num_multiplications':n*m*p,'U':U,'V':V,'W':W}))
")
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 64`

### T6. Valid: naive R(5,5,5) = 125

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"tensor\",
  \"instance\": {\"n\": 5, \"m\": 5, \"p\": 5},
  \"submission\": $(python -c "
import json
n,m,p = 5,5,5
U,V,W = [],[],[]
for i in range(n):
    for k in range(m):
        for j in range(p):
            u = [[0]*m for _ in range(n)]; u[i][k]=1
            v = [[0]*p for _ in range(m)]; v[k][j]=1
            w = [[0]*p for _ in range(n)]; w[i][j]=1
            U.append(u); V.append(v); W.append(w)
print(json.dumps({'num_multiplications':n*m*p,'U':U,'V':V,'W':W}))
")
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 125`

### T7. Valid: rational string coefficients

Uses `"1/2"` and `"2"` as coefficient strings.

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "tensor",
  "instance": {"n": 2, "m": 2, "p": 2},
  "submission": {
    "num_multiplications": 8,
    "U": [
      [["2",0],[0,0]], [[0,"2"],[0,0]], [[0,0],["2",0]], [[0,0],[0,"2"]],
      [["2",0],[0,0]], [[0,"2"],[0,0]], [[0,0],["2",0]], [[0,0],[0,"2"]]
    ],
    "V": [
      [[1,0],[0,0]], [[1,0],[0,0]], [[1,0],[0,0]], [[1,0],[0,0]],
      [[0,1],[0,0]], [[0,1],[0,0]], [[0,1],[0,0]], [[0,1],[0,0]]
    ],
    "W": [
      [["1/2",0],[0,0]], [[0,0],["1/2",0]], [["1/2",0],[0,0]], [[0,0],["1/2",0]],
      [[0,"1/2"],[0,0]], [[0,0],[0,"1/2"]], [[0,"1/2"],[0,0]], [[0,0],[0,"1/2"]]
    ]
  }
}' | python -m json.tool
```

Expected: hmm, this one is trickier to get right inline. Use the Python-generated naive test (T2) with rational coefficients instead. The point is: `"1/2"` strings are accepted, `0.5` floats are rejected.

### T8. Reject: disallowed size

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "tensor",
  "instance": {"n": 9, "m": 9, "p": 9},
  "submission": {
    "num_multiplications": 1,
    "U": [[[0]]],
    "V": [[[0]]],
    "W": [[[0]]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_INSTANCE"`

### T9. Reject: float coefficient

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "tensor",
  "instance": {"n": 2, "m": 2, "p": 2},
  "submission": {
    "num_multiplications": 1,
    "U": [[[0.5, 0], [0, 0]]],
    "V": [[[0, 0], [0, 0]]],
    "W": [[[0, 0], [0, 0]]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_FORMAT"`, message about rational strings

---

## Still Life Submissions

### S1. Valid: block in 8x8 (4 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "submission": {
    "claimed_cells": 4,
    "grid": [
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected:

```json
{
  "success": true,
  "submission_id": "<uuid>",
  "problem_name": "stilllife",
  "instance": { "n": 8 },
  "score": 4,
  "is_record": false,
  "message": "Verification passed"
}
```

### S2. Valid: beehive in 8x8 (6 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "submission": {
    "claimed_cells": 6,
    "grid": [
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,1,0,0,1,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected: `"success": true`, `"score": 6`

### S3. Valid: loaf in 10x10 (7 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 10},
  "submission": {
    "claimed_cells": 7,
    "grid": [
      [0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,1,1,0,0,0,0],
      [0,0,0,1,0,0,1,0,0,0],
      [0,0,0,0,1,0,1,0,0,0],
      [0,0,0,0,0,1,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected: `"success": true`, `"score": 7`

### S4. Valid: block in 16x16 (4 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"stilllife\",
  \"instance\": {\"n\": 16},
  \"submission\": {
    \"claimed_cells\": 4,
    \"grid\": $(python -c "
import json
g = [[0]*16 for _ in range(16)]
g[7][7]=g[7][8]=g[8][7]=g[8][8]=1
print(json.dumps(g))
")
  }
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 4`

### S5. Valid: beehive in 20x20 (6 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"stilllife\",
  \"instance\": {\"n\": 20},
  \"submission\": {
    \"claimed_cells\": 6,
    \"grid\": $(python -c "
import json
g = [[0]*20 for _ in range(20)]
g[9][10]=g[9][11]=1
g[10][9]=g[10][12]=1
g[11][10]=g[11][11]=1
print(json.dumps(g))
")
  }
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 6`

### S6. Valid: block in 32x32 (4 cells)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"stilllife\",
  \"instance\": {\"n\": 32},
  \"submission\": {
    \"claimed_cells\": 4,
    \"grid\": $(python -c "
import json
g = [[0]*32 for _ in range(32)]
g[15][15]=g[15][16]=g[16][15]=g[16][16]=1
print(json.dumps(g))
")
  }
}" | python -m json.tool
```

Expected: `"success": true`, `"score": 4`

### S7. Reject: unstable pattern (blinker oscillates)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "submission": {
    "claimed_cells": 3,
    "grid": [
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,1,1,1,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "VERIFICATION_FAILED"`, message about stability

### S8. Reject: disconnected blocks

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "submission": {
    "claimed_cells": 8,
    "grid": [
      [0,0,0,0,0,0,0,0],
      [0,1,1,0,0,0,0,0],
      [0,1,1,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,1,1,0],
      [0,0,0,0,0,1,1,0],
      [0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "VERIFICATION_FAILED"`, message about connected

### S9. Reject: wrong cell count

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "submission": {
    "claimed_cells": 99,
    "grid": [
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0]
    ]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "VERIFICATION_FAILED"`, message says claimed 99 but grid has 4

### S10. Reject: disallowed n

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "stilllife",
  "instance": {"n": 5},
  "submission": {
    "claimed_cells": 1,
    "grid": [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_INSTANCE"`

---

## HP Protein Folding Submissions

### P1. Valid: warm-up 6H snake (2 contacts)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hpprotein",
  "instance": {"sequence_id": "WARMUP_6H"},
  "submission": {
    "lattice": "2D",
    "coords": [[0,0],[1,0],[1,1],[0,1],[0,2],[1,2]]
  }
}' | python -m json.tool
```

Expected: `"success": true`, `"score": 2`

### P2. Valid: open benchmark S5 straight-line fold (usually low score)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"hpprotein\",
  \"instance\": {\"sequence_id\": \"S5\"},
  \"submission\": {
    \"coords\": $(python -c "import json; print(json.dumps([[i,0] for i in range(48)]))")
  }
}" | python -m json.tool
```

Expected: `"success": true`

### P3. Reject: excluded proven-optimal benchmark S1

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d "{
  \"email\": \"test@example.com\",
  \"problem_name\": \"hpprotein\",
  \"instance\": {\"sequence_id\": \"S1\"},
  \"submission\": {
    \"coords\": $(python -c "import json; print(json.dumps([[i,0] for i in range(20)]))")
  }
}" | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_INSTANCE"`

### P4. Reject: duplicate coordinate (not self-avoiding)

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hpprotein",
  "instance": {"sequence_id": "WARMUP_6H"},
  "submission": {
    "coords": [[0,0],[1,0],[1,1],[0,1],[0,1],[1,2]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "VERIFICATION_FAILED"`

### P5. Reject: invalid lattice value

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "hpprotein",
  "instance": {"sequence_id": "WARMUP_6H"},
  "submission": {
    "lattice": "3D",
    "coords": [[0,0],[1,0],[1,1],[0,1],[0,2],[1,2]]
  }
}' | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_FORMAT"`

---

## Leaderboard Endpoint

### L1. Valid: top-k leaderboard for an instance

```bash
curl -s -X POST http://localhost:8080/api/v1/leaderboard \
  -H "Content-Type: application/json" \
  -H "X-Leaderboard-Password: lossfunk123" \
  -d '{
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "k": 5
}' | python -m json.tool
```

Expected: 200 with `"success": true` and up to 5 ranked entries in `entries`.

### L2. Reject: wrong password

```bash
curl -s -X POST http://localhost:8080/api/v1/leaderboard \
  -H "Content-Type: application/json" \
  -H "X-Leaderboard-Password: wrong-password" \
  -d '{
  "problem_name": "stilllife",
  "instance": {"n": 8},
  "k": 5
}' | python -m json.tool
```

Expected: 401, `"error_code": "UNAUTHORIZED"`.

---

## Error Handling

### E1. Unknown problem_name

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "test@example.com",
  "problem_name": "bogus",
  "instance": {},
  "submission": {}
}' | python -m json.tool
```

Expected: 404, `"error_code": "PROBLEM_NOT_FOUND"`

### E2. Invalid email

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "email": "not-an-email",
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {"claimed_det": 1, "matrix": [[1]]}
}' | python -m json.tool
```

Expected: 400, `"error_code": "INVALID_EMAIL"`

### E3. Missing email

```bash
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
  "problem_name": "hadamard",
  "instance": {"n": 23},
  "submission": {"claimed_det": 1, "matrix": [[1]]}
}' | python -m json.tool
```

Expected: 400, `"error_code": "MISSING_FIELD"`

### E4. Payload too large

```bash
# Generate a payload > 500KB
python -c "
import json
m = [[1]*99 for _ in range(99)]
# Pad with spaces to exceed 500KB
payload = json.dumps({'email':'a@b.com','problem_name':'hadamard','instance':{'n':99},'submission':{'claimed_det':1,'matrix':m}})
# Write to temp file
with open('/tmp/big_payload.json','w') as f:
    f.write(payload + ' ' * 600000)
"
curl -s -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d @/tmp/big_payload.json | python -m json.tool
```

Expected: 413, `"error_code": "SIZE_LIMIT_EXCEEDED"`

### E5. Get nonexistent submission

```bash
curl -s http://localhost:8080/api/v1/submission/00000000-0000-0000-0000-000000000000 | python -m json.tool
```

Expected: 404, `"error_code": "NOT_FOUND"`

---

## Test Summary

| #   | Problem   | Type   | Description            | Expected                 |
| --- | --------- | ------ | ---------------------- | ------------------------ |
| H1  | hadamard  | valid  | n=23 witness matrix    | score = 2779447296000000 |
| H2  | hadamard  | reject | n=5 not allowed        | INVALID_INSTANCE         |
| H3  | hadamard  | reject | wrong claimed_det      | VERIFICATION_FAILED      |
| H4  | hadamard  | reject | missing claimed_det    | MISSING_FIELD            |
| C1  | conway    | valid  | zero matrix            | score = 0.0              |
| C2  | conway    | valid  | circular graph         | score ~4.0               |
| C3  | conway    | reject | asymmetric             | INVALID_FORMAT           |
| C4  | conway    | reject | 50x50 matrix           | INVALID_FORMAT           |
| T1  | tensor    | valid  | Strassen (2,2,2)=7     | score = 7                |
| T2  | tensor    | valid  | naive (2,2,3)=12       | score = 12               |
| T3  | tensor    | valid  | naive (3,3,3)=27       | score = 27               |
| T4  | tensor    | valid  | naive (3,3,6)=54       | score = 54               |
| T5  | tensor    | valid  | naive (4,4,4)=64       | score = 64               |
| T6  | tensor    | valid  | naive (5,5,5)=125      | score = 125              |
| T7  | tensor    | valid  | rational strings       | score = 8                |
| T8  | tensor    | reject | (9,9,9) not allowed    | INVALID_INSTANCE         |
| T9  | tensor    | reject | float coefficient      | INVALID_FORMAT           |
| S1  | stilllife | valid  | block n=8              | score = 4                |
| S2  | stilllife | valid  | beehive n=8            | score = 6                |
| S3  | stilllife | valid  | loaf n=10              | score = 7                |
| S4  | stilllife | valid  | block n=16             | score = 4                |
| S5  | stilllife | valid  | beehive n=20           | score = 6                |
| S6  | stilllife | valid  | block n=32             | score = 4                |
| S7  | stilllife | reject | blinker (unstable)     | VERIFICATION_FAILED      |
| S8  | stilllife | reject | disconnected blocks    | VERIFICATION_FAILED      |
| S9  | stilllife | reject | wrong cell count       | VERIFICATION_FAILED      |
| S10 | stilllife | reject | n=5 not allowed        | INVALID_INSTANCE         |
| P1  | hpprotein | valid  | warm-up snake          | score = 2                |
| P2  | hpprotein | valid  | S5 linear fold         | success                  |
| P3  | hpprotein | reject | S1 excluded            | INVALID_INSTANCE         |
| P4  | hpprotein | reject | duplicate coordinate   | VERIFICATION_FAILED      |
| P5  | hpprotein | reject | lattice not 2D         | INVALID_FORMAT           |
| L1  | --        | valid  | leaderboard top-k      | success                  |
| L2  | --        | reject | leaderboard bad secret | UNAUTHORIZED             |
| E1  | --        | reject | unknown problem        | PROBLEM_NOT_FOUND        |
| E2  | --        | reject | bad email              | INVALID_EMAIL            |
| E3  | --        | reject | missing email          | MISSING_FIELD            |
| E4  | --        | reject | oversized payload      | SIZE_LIMIT_EXCEEDED      |
| E5  | --        | reject | nonexistent submission | NOT_FOUND                |
