# Module 07 — Authentication & Rate Limiting: Identifying Users, Preventing Abuse

## Concept

Once your API is reachable by many parallel users, you need to know **who** is calling (authentication),
what they're **allowed** to do (authorization), and **how much** they're allowed to call in a given time
window (rate limiting) — otherwise one aggressive or buggy client can degrade service for everyone else.

| Term | Meaning |
|------|---------|
| **API key** | A simple static secret token identifying a client/application |
| **JWT (JSON Web Token)** | A signed, self-contained token carrying user identity/claims, verifiable without a DB lookup |
| **Authentication** | Confirming *who* is calling |
| **Authorization** | Confirming *what* they're allowed to do |
| **Rate limiting** | Capping requests per identity per time window |
| **Token bucket / sliding window** | Common algorithms for implementing rate limits |
| **429 Too Many Requests** | The correct HTTP status for a rate-limited client |

## Hands-On Lab

### Step 1 — Simple API key authentication

Install: `uv pip install fastapi uvicorn[standard] python-jose[cryptography] passlib[bcrypt]`

Create `main.py`:

```python
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

# In production this lives in a database, not a hardcoded dict
VALID_API_KEYS = {"secret-key-alice": "alice", "secret-key-bob": "bob"}

def get_current_client(api_key: str = Security(api_key_header)):
    client = VALID_API_KEYS.get(api_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return client

@app.get("/protected")
def protected_route(client: str = Depends(get_current_client)):
    return {"message": f"Hello {client}, you're authenticated"}
```

Test it:

```bash
curl http://localhost:8000/protected                                    # 401, no key
curl -H "X-API-Key: secret-key-alice" http://localhost:8000/protected    # 200, works
curl -H "X-API-Key: wrong-key" http://localhost:8000/protected           # 401, invalid
```

### Step 2 — JWT-based auth (identity carried in a signed token, no DB lookup needed per-request)

Add to `main.py`:

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "CHANGE_ME_IN_PRODUCTION"  # store in an env var / secrets manager, never hardcode
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Demo user store — in production, hash+verify against a real DB
FAKE_USERS = {"alice": "password123"}

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if FAKE_USERS.get(form_data.username) != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(
        {"sub": form_data.username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/me")
def read_current_user(user: str = Depends(get_current_user)):
    return {"username": user}
```

Test it:

```bash
# Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=alice&password=password123" \
  -H "Content-Type: application/x-www-form-urlencoded" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/me
```

**Why JWT matters for parallel scaling:** with N worker processes / N machines, a JWT can be verified
locally with just the secret key — no shared session store or DB lookup needed on every request. (You
still might hit Redis/DB for authorization details, but pure identity verification is stateless.)

### Step 3 — Rate limiting per client, backed by Redis (shared across all workers/instances)

```bash
uv pip install slowapi redis
```

Create/extend `main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/2")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/limited")
@limiter.limit("5/minute")
def limited_route(request: Request):
    return {"message": "You made it within the limit"}
```

Test it — hammer the endpoint more than 5 times in a minute:

```bash
for i in $(seq 1 8); do curl -i -s http://localhost:8000/limited | head -1; done
```

You should see the first 5 return `200 OK` and the rest return `429 Too Many Requests`.

**Why Redis-backed (not in-memory) rate limiting matters:** if you have 4 Gunicorn workers (Module 03),
an in-memory counter in each worker would let a client get `5 × 4 = 20` requests/minute (5 per worker)
instead of the intended 5 total, since each worker has its own memory. Backing the limiter with Redis
gives you one shared counter across all workers and instances.

### Step 4 — Combine identity-aware rate limiting

Rate limit by authenticated user instead of just IP (fairer, and IP-based limiting breaks for users
behind shared NAT/corporate proxies):

```python
def get_client_identity(request: Request):
    # Prefer authenticated identity; fall back to IP for anonymous endpoints
    api_key = request.headers.get("X-API-Key")
    return api_key or get_remote_address(request)

limiter = Limiter(key_func=get_client_identity, storage_uri="redis://localhost:6379/2")
```

## Checkpoint Questions

1. Why is IP-based rate limiting sometimes unfair to legitimate users?
2. Why would in-memory (per-process) rate limiting fail once you have multiple Gunicorn workers or multiple machines?
3. What's the practical difference between a 401 and a 403 response? Between 401 and 429?
4. Why should the JWT secret key never be hardcoded or committed to source control in a real project?

## What's Next

Module 08 packages everything so far into a Docker image — the same artifact you'll run consistently in
dev, CI, and production.
