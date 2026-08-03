# Module 01 — FastAPI Basics: Exposing Python as an API

## Concept

An API service takes incoming HTTP requests, runs your Python logic, and returns a response — usually JSON.
**FastAPI** is the framework we'll use because:

- It's built on **ASGI** (Asynchronous Server Gateway Interface), which is what lets a single process
  handle many requests concurrently (you'll see why in Module 02).
- It uses **Pydantic** models for automatic request validation — bad input gets rejected before your
  code ever runs.
- It auto-generates interactive API docs (Swagger UI) for free.

Key vocabulary:

| Term | Meaning |
|------|---------|
| **Endpoint / route** | A URL + HTTP method combination your app responds to (e.g. `GET /users/42`) |
| **Path parameter** | Part of the URL itself, e.g. the `42` in `/users/42` |
| **Query parameter** | Part after `?`, e.g. `/users?active=true` |
| **Request body** | JSON payload sent with POST/PUT requests |
| **Pydantic model (schema)** | A Python class describing the *shape* of valid data |
| **Status code** | Numeric HTTP result: 200 OK, 404 Not Found, 422 Validation Error, 500 Server Error |
| **ASGI server** | The program that actually listens on a socket and hands requests to FastAPI (we use `uvicorn`) |

## Hands-On Lab

### Step 1 — Set up your environment

```bash
mkdir -p ~/learning-lab/01-fastapi-basics && cd ~/learning-lab/01-fastapi-basics
uv venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
uv pip install fastapi uvicorn[standard] pydantic
```

`uv venv` creates a `.venv` folder (same idea as `python -m venv`, just faster), and `uv pip install`
resolves and installs packages into it — noticeably quicker than plain `pip`, which you'll appreciate
once you're rebuilding environments/images repeatedly in later modules.

### Step 2 — Your first endpoint

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Learning API")

@app.get("/")
def read_root():
    return {"message": "API is alive"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # user_id is automatically validated as an int — try /users/abc and see what happens
    return {"user_id": user_id, "name": f"User{user_id}"}
```

Run it:

```bash
uvicorn main:app --reload
```

Visit:
- `http://127.0.0.1:8000/` → see the JSON response
- `http://127.0.0.1:8000/docs` → interactive Swagger UI (try calling `/users/42` from the browser)
- `http://127.0.0.1:8000/users/abc` → see FastAPI reject bad input automatically (422 error)

**Checkpoint:** Why did `/users/abc` fail without you writing any validation code yourself?
*(Answer: the `user_id: int` type hint is used by FastAPI+Pydantic to validate automatically.)*

### Step 3 — Query parameters and request bodies

Add to `main.py`:

```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/search")
def search_items(q: str, limit: int = 10):
    # q is required (no default); limit is optional with default 10
    return {"query": q, "limit": limit, "results": [f"result-{i}" for i in range(limit)]}

@app.post("/items")
def create_item(item: Item):
    # FastAPI parses + validates the JSON body into an `Item` instance automatically
    return {"received": item.dict(), "status": "created"}
```

Test the POST endpoint with curl:

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": 9.99}'
```

Try sending invalid data (e.g. `"price": "not-a-number"`) and observe the structured error response.

### Step 4 — Simulating "real work" and measuring blocking behavior

This step sets up the problem that Module 02 solves. Add:

```python
import time

@app.get("/slow-sync")
def slow_sync_endpoint():
    time.sleep(3)  # simulates a blocking call: e.g. a slow DB query done the wrong way
    return {"done": True}
```

Open **two browser tabs** and hit `http://127.0.0.1:8000/slow-sync` in both at nearly the same time.
Notice: with a single `uvicorn` worker and a *sync* `def` endpoint using `time.sleep`, FastAPI runs it in
a thread pool, so it won't fully freeze other requests — but there's a limited thread pool size. Now
change `time.sleep` to a CPU-bound loop:

```python
@app.get("/slow-cpu")
def slow_cpu_endpoint():
    total = 0
    for i in range(200_000_000):
        total += i
    return {"total": total}
```

Hit `/slow-cpu` in one tab, and `/` (the root endpoint) in another tab immediately after. **Notice the
root endpoint now waits** — pure CPU work in a single process blocks everything else, regardless of
sync/async. This is the exact problem Modules 02 and 03 solve.

## Checkpoint Questions

1. What's the difference between a path parameter and a query parameter?
2. Why does FastAPI return a 422 status code instead of a 500 when you send bad data?
3. Why did the CPU-bound loop block the root endpoint, but `time.sleep` (somewhat) didn't?

## What's Next

Module 02 explains *why* this happens (the GIL, async I/O vs CPU-bound work) and how to design around it.
