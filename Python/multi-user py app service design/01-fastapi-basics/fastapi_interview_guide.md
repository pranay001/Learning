# FastAPI Interview Preparation Guide

A comprehensive question-and-answer reference covering FastAPI from fundamentals to advanced production topics. Each question is labeled **Beginner**, **Intermediate**, or **Advanced**, and every answer includes a detailed explanation with code examples where relevant.

---

## Table of Contents

1. [Beginner Questions](#beginner-questions) (Q1–Q15)
2. [Intermediate Questions](#intermediate-questions) (Q16–Q30)
3. [Advanced Questions](#advanced-questions) (Q31–Q45)

---

## Beginner Questions

### Q1. What is FastAPI, and why has it become popular? — **Beginner**

**Answer:**
FastAPI is a modern, high-performance Python web framework for building APIs, built on top of **Starlette** (for the web/ASGI layer) and **Pydantic** (for data validation and serialization).

**Detailed explanation:**
Its popularity comes from a combination of factors:
- **Speed**: Because it's built on Starlette and uses ASGI (Asynchronous Server Gateway Interface), it's one of the fastest Python frameworks available, comparable to NodeJS and Go in benchmarks.
- **Type hints as the source of truth**: FastAPI uses standard Python type hints to perform data validation, serialization, and documentation generation. You don't write separate schemas — your function signature *is* the schema.
- **Automatic interactive documentation**: FastAPI auto-generates OpenAPI (Swagger) and ReDoc documentation from your code, with zero extra configuration.
- **Editor support**: Because everything is typed, IDEs can autocomplete request bodies, query params, and more.
- **Built-in data validation**: Pydantic models catch invalid data automatically and return clear 422 errors, without you writing manual validation logic.
- **Async-first**: Native support for `async def` path operations makes it well-suited for I/O-bound workloads (DB calls, external API calls).

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

---

### Q2. How does FastAPI compare to Flask and Django? — **Beginner**

**Answer:**
Flask is a minimalist WSGI micro-framework, Django is a full-featured "batteries-included" WSGI framework, and FastAPI is an ASGI framework focused specifically on building APIs with automatic validation and docs.

**Detailed explanation:**

| Aspect | Flask | Django | FastAPI |
|---|---|---|---|
| Protocol | WSGI (sync) | WSGI (sync, ASGI partial support) | ASGI (async-native) |
| Data validation | Manual / extensions (Marshmallow) | Django Forms/DRF Serializers | Built-in via Pydantic |
| Docs generation | Manual / extensions | Manual / DRF extensions | Automatic (OpenAPI/Swagger) |
| Performance | Moderate | Moderate | High (async + Starlette) |
| Use case | General web apps, small APIs | Full web apps with ORM, admin, auth | High-performance APIs, microservices |
| Learning curve | Low | Higher (many built-in conventions) | Low–Medium |

FastAPI isn't a full replacement for Django in scenarios needing an admin panel, built-in ORM, or templating out of the box — it's laser-focused on API development. Many teams pick FastAPI when performance and automatic validation/docs matter more than a monolithic batteries-included structure.

---

### Q3. What is the difference between WSGI and ASGI, and why does it matter for FastAPI? — **Beginner**

**Answer:**
WSGI (Web Server Gateway Interface) is a synchronous specification for how web servers communicate with Python web applications; ASGI (Asynchronous Server Gateway Interface) is its successor that supports asynchronous code, WebSockets, and long-lived connections.

**Detailed explanation:**
- WSGI handles one request at a time per worker thread/process — it blocks while waiting on I/O (like a database call), which limits throughput under I/O-heavy workloads unless you scale via more workers/threads.
- ASGI allows a single worker to handle many concurrent requests using an event loop (via Python's `asyncio`), because it can pause execution during I/O waits (using `await`) and serve other requests in the meantime.
- FastAPI is built on ASGI (via Starlette), served typically by **Uvicorn**, an ASGI server. This lets FastAPI support standard synchronous handlers, `async def` handlers, WebSockets, and background tasks — all within the same framework, whereas WSGI frameworks like classic Flask cannot natively handle WebSockets or concurrent async I/O.

---

### Q4. How do you define a basic route (path operation) in FastAPI? — **Beginner**

**Answer:**
You use decorators corresponding to HTTP methods (`@app.get`, `@app.post`, `@app.put`, `@app.delete`, `@app.patch`) on an instance of `FastAPI`.

**Detailed explanation:**
Each decorator takes a path string, and the decorated function ("path operation function") handles requests to that path and method. The return value is automatically serialized to JSON.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(name: str):
    return {"name": name}
```

FastAPI matches incoming requests to path operations in the order they are declared, so more specific paths (e.g., `/users/me`) should be declared before more generic dynamic ones (e.g., `/users/{user_id}`) to avoid the dynamic route greedily matching first.

---

### Q5. How do path parameters work, and how does FastAPI perform type conversion/validation on them? — **Beginner**

**Answer:**
Path parameters are declared as part of the URL path in curly braces, and their type annotation in the function signature tells FastAPI how to convert and validate the value.

**Detailed explanation:**
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```
Here, `item_id: int` means FastAPI will:
1. Extract `item_id` from the URL as a string.
2. Attempt to convert it to `int`.
3. If conversion fails (e.g., `/items/abc`), automatically return a `422 Unprocessable Entity` response with a descriptive error — no manual `try/except` needed.

You can further constrain path parameters using `Path()`:
```python
from fastapi import Path

@app.get("/items/{item_id}")
async def read_item(item_id: int = Path(..., gt=0, le=1000)):
    return {"item_id": item_id}
```
This enforces `item_id` must be greater than 0 and less than or equal to 1000.

---

### Q6. How do query parameters work, and how do you make them optional with defaults? — **Beginner**

**Answer:**
Any function parameter that is **not** part of the path and is a simple type (str, int, float, bool, etc.) is automatically interpreted as a query parameter.

**Detailed explanation:**
```python
@app.get("/items/")
async def list_items(skip: int = 0, limit: int = 10, q: str | None = None):
    return {"skip": skip, "limit": limit, "q": q}
```
- `skip` and `limit` have default values, making them optional query parameters (`?skip=5&limit=20`).
- `q: str | None = None` marks `q` as optional and nullable.
- If a parameter has no default, it becomes **required**, and omitting it in the request returns a 422 error.

You can add validation constraints using `Query()`:
```python
from fastapi import Query

@app.get("/items/")
async def list_items(q: str | None = Query(default=None, max_length=50, min_length=3)):
    return {"q": q}
```

---

### Q7. How do you accept and validate a JSON request body? — **Beginner**

**Answer:**
You define a Pydantic model representing the expected body shape, then declare a function parameter typed as that model — FastAPI will parse, validate, and inject it automatically.

**Detailed explanation:**
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```
When a request arrives, FastAPI:
1. Reads the raw JSON body.
2. Validates it against the `Item` schema (checking types, required fields).
3. If invalid, returns a 422 response detailing exactly which field failed and why.
4. If valid, provides `item` as a fully-typed Python object inside the function, with IDE autocomplete support.

This eliminates a large class of bugs from manually parsing `request.json()` and validating fields by hand.

---

### Q8. What is Pydantic's `BaseModel`, and why is it central to FastAPI? — **Beginner**

**Answer:**
`BaseModel` is Pydantic's base class for defining data schemas using Python type hints; FastAPI uses it as the single source of truth for request/response validation, serialization, and OpenAPI schema generation.

**Detailed explanation:**
```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int | None = None
```
Key behaviors:
- **Validation**: Pydantic coerces and validates input (e.g., a numeric string `"5"` is converted to `int` if the field type is `int`, unless strict mode is used).
- **Serialization**: `.model_dump()` (Pydantic v2) or `.dict()` (v1) converts the model back into a plain dict; `.model_dump_json()` converts to a JSON string.
- **Nested models**: Fields can be other `BaseModel` types, and Pydantic validates recursively.
- **Reuse across the API**: The same model class can double as the OpenAPI schema definition, saving you from maintaining a separate JSON Schema file by hand.

---

### Q9. What does `response_model` do, and why declare it explicitly? — **Beginner**

**Answer:**
`response_model` tells FastAPI the shape of the data your endpoint should return, allowing it to filter, validate, and document the output — independent of what your function's internal logic actually returns.

**Detailed explanation:**
```python
class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    # Even if we return the full user object (including password),
    # FastAPI filters the response down to UserOut's fields.
    return user
```
This is critical for **security** (never accidentally leaking a hashed password or internal field) and for keeping your OpenAPI docs accurate. FastAPI validates the return value against `response_model` and strips out any fields not declared on it.

---

### Q10. How do you set a custom HTTP status code for a response? — **Beginner**

**Answer:**
Use the `status_code` parameter on the path operation decorator for a fixed code, or manipulate the `Response` object directly for a dynamic one.

**Detailed explanation:**
```python
from fastapi import status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item
```
For dynamic status codes (decided at runtime):
```python
from fastapi import Response

@app.get("/items/{item_id}")
async def get_item(item_id: int, response: Response):
    if item_id == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "not found"}
    return {"item_id": item_id}
```
Using the `fastapi.status` module (constants like `HTTP_201_CREATED`) instead of raw integers improves readability and reduces typos.

---

### Q11. How does FastAPI generate interactive API documentation automatically? — **Beginner**

**Answer:**
FastAPI introspects your path operations, Pydantic models, and type hints to build an OpenAPI schema in JSON, then serves interactive UIs (Swagger UI at `/docs`, ReDoc at `/redoc`) that render that schema.

**Detailed explanation:**
- The OpenAPI schema itself is available at `/openapi.json` by default.
- Every piece of metadata you add — `response_model`, `status_code`, `tags`, `summary`, `description`, docstrings, Pydantic field descriptions — feeds directly into this schema and shows up in the docs UI.
- You don't write documentation separately; the same code that handles requests also produces the docs, which prevents docs and implementation from drifting out of sync.
- You can customize or disable the docs:
```python
app = FastAPI(docs_url="/documentation", redoc_url=None)  # rename Swagger, disable ReDoc
```

---

### Q12. How do you return proper error responses using `HTTPException`? — **Beginner**

**Answer:**
`HTTPException` is a special exception class that, when raised, FastAPI catches and converts into an HTTP error response with the specified status code and detail message.

**Detailed explanation:**
```python
from fastapi import HTTPException

items = {"foo": "The Foo item"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}
```
When raised, this immediately halts execution of the function and returns:
```json
{"detail": "Item not found"}
```
with a 404 status. You can also pass custom headers:
```python
raise HTTPException(status_code=400, detail="Bad request", headers={"X-Error": "custom"})
```
This is the idiomatic way to signal client errors (4xx) without manually constructing `Response` objects.

---

### Q13. What HTTP method decorators does FastAPI provide, and how do they map to CRUD operations? — **Beginner**

**Answer:**
FastAPI provides decorators for all standard HTTP verbs: `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`, plus `@app.options`, `@app.head`, and `@app.trace`.

**Detailed explanation:**
Conventional REST mapping:
- **GET** → Read/retrieve a resource (should be safe and idempotent, no body typically).
- **POST** → Create a new resource (not idempotent — calling twice creates two resources).
- **PUT** → Replace/update a resource fully (idempotent — same call twice yields the same result).
- **PATCH** → Partially update a resource (may or may not be idempotent).
- **DELETE** → Remove a resource (idempotent — deleting twice is the same as once).

```python
@app.get("/items/{id}")     # Read
@app.post("/items/")        # Create
@app.put("/items/{id}")     # Full update
@app.patch("/items/{id}")   # Partial update
@app.delete("/items/{id}")  # Delete
```
Following these conventions matters for interview discussions because it shows understanding of REST semantics, not just FastAPI syntax.

---

### Q14. What is Uvicorn, and why is it needed to run a FastAPI app? — **Beginner**

**Answer:**
Uvicorn is a lightning-fast ASGI server implementation, built on `uvloop` and `httptools`, responsible for actually accepting HTTP connections and passing them to your FastAPI application.

**Detailed explanation:**
FastAPI itself is just a framework — it defines *how* to handle a request once received, but it doesn't listen on a network socket. Uvicorn (or alternatives like Hypercorn, Daphne) is the ASGI server that:
1. Binds to a host/port.
2. Accepts raw TCP/HTTP connections.
3. Translates them into the ASGI protocol (a standard Python callable interface).
4. Passes them to your `app` object.

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- `main:app` means "import `app` from `main.py`".
- `--reload` enables auto-restart on code changes (development only, not for production).
- In production, Uvicorn is often run with multiple worker processes via Gunicorn as a process manager (`gunicorn -k uvicorn.workers.UvicornWorker`).

---

### Q15. Why does FastAPI rely so heavily on Python type hints, and how does that benefit development? — **Beginner**

**Answer:**
Type hints in FastAPI aren't just documentation — they are actively read at runtime (via Pydantic) to perform validation, conversion, serialization, and dependency injection, and they drive automatic OpenAPI schema generation.

**Detailed explanation:**
Normally in Python, type hints are optional and ignored at runtime. FastAPI changes this by using libraries (`Pydantic`, `typing`) to introspect annotations and act on them:
```python
async def read_item(item_id: int, q: str | None = None, item: Item | None = None):
    ...
```
From this single signature, FastAPI infers:
- `item_id` is a required path/query param, must be an integer.
- `q` is an optional query param, string or null.
- `item` is a request body (since it's a Pydantic model), optional.

Benefits:
- **Less code**: No manual parsing/validation logic.
- **Fewer bugs**: Type mismatches are caught before your business logic runs.
- **Better editor support**: Autocomplete, inline errors, and refactoring safety in IDEs like PyCharm/VSCode.
- **Self-documenting**: The function signature communicates the API contract clearly to other developers.

---

## Intermediate Questions

### Q16. What is Dependency Injection in FastAPI, and how does `Depends()` work? — **Intermediate**

**Answer:**
Dependency Injection (DI) in FastAPI lets you declare reusable pieces of logic (dependencies) that FastAPI automatically calls and injects into your path operation functions, using the `Depends()` marker.

**Detailed explanation:**
```python
from fastapi import Depends

def common_params(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def list_items(commons: dict = Depends(common_params)):
    return commons

@app.get("/users/")
async def list_users(commons: dict = Depends(common_params)):
    return commons
```
How it works internally:
1. FastAPI sees `Depends(common_params)` as a marker, not a default value.
2. Before calling `list_items`, it calls `common_params(...)`, resolving its own parameters (which can themselves be query params, path params, or other dependencies) from the incoming request.
3. The return value of `common_params` is injected as `commons`.

Benefits: eliminates duplicated logic across endpoints (pagination, auth checks, DB session creation), and dependencies can be class-based, generator-based (with `yield`), or simple functions. FastAPI also caches a dependency's result **per request** by default, so if two different dependencies both need the same sub-dependency, it's only computed once.

---

### Q17. How do nested/chained dependencies work, and why are they useful? — **Intermediate**

**Answer:**
Dependencies can themselves declare their own dependencies via `Depends()`, forming a tree that FastAPI resolves recursively before executing the path operation.

**Detailed explanation:**
```python
def get_query_token(token: str):
    if token != "secret":
        raise HTTPException(status_code=400, detail="Invalid token")
    return token

def verify_and_get_user(token: str = Depends(get_query_token), db=Depends(get_db)):
    user = db.query_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/profile/")
async def get_profile(user=Depends(verify_and_get_user)):
    return {"user": user}
```
Here, `get_profile` depends on `verify_and_get_user`, which itself depends on `get_query_token` and `get_db`. FastAPI resolves this whole chain automatically. This pattern is heavily used for:
- Authentication/authorization layering (verify token → fetch user → check permissions).
- Shared resource acquisition (DB sessions, external clients).

Because dependencies are cached per request, if multiple parts of the chain need `get_db`, it's only invoked once per incoming request unless you explicitly disable caching with `Depends(get_db, use_cache=False)`.

---

### Q18. How do you write custom validators on Pydantic fields, and when would you use them? — **Intermediate**

**Answer:**
Pydantic allows custom validation logic beyond basic type checks using the `@field_validator` decorator (Pydantic v2) or `@validator` (Pydantic v1), useful for cross-field checks, format enforcement, and normalization.

**Detailed explanation:**
```python
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("username must be alphanumeric")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v
```
Use cases:
- Enforcing business rules (password strength, username format).
- Cross-field validation (password confirmation, date ranges where `end_date > start_date`).
- Normalizing input (trimming whitespace, lowercasing emails) before it reaches your business logic.

If a validator raises `ValueError`, FastAPI automatically converts this into a 422 response with a clear error message pointing to the offending field — no extra exception handling code required.

---

### Q19. What are Background Tasks, and how do they differ from a task queue like Celery? — **Intermediate**

**Answer:**
`BackgroundTasks` lets you schedule a function to run **after** the response has been sent to the client, within the same process — useful for lightweight fire-and-forget work, but not a substitute for a distributed task queue for heavy or critical work.

**Detailed explanation:**
```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message + "\n")

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"notification sent to {email}")
    return {"message": "Notification sent"}
```
Key characteristics:
- Runs in-process, after the response is returned — the client doesn't wait for it.
- If the process crashes before the task completes, the task is lost (no persistence/retry).
- Not distributed — doesn't scale across multiple worker processes/machines by itself.

Use `BackgroundTasks` for: sending a quick log entry, firing a webhook, cleanup after a request. Use **Celery** (or RQ, Dramatiq, arq) when you need: retries on failure, task persistence (e.g., backed by Redis/RabbitMQ), scheduling, distributed workers across machines, or long-running/heavy computation that shouldn't share resources with the API process.

---

### Q20. How do you create and use custom Middleware in FastAPI? — **Intermediate**

**Answer:**
Middleware wraps every request/response cycle, letting you run code before the request reaches your path operation and after the response is generated — commonly used for logging, timing, authentication headers, or modifying responses globally.

**Detailed explanation:**
```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```
- `call_next` passes control to the next middleware or the actual path operation, and returns the resulting `Response`.
- Middleware runs for **every** request, unlike dependencies which are attached per-route.
- Order matters: middleware added later wraps *around* middleware added earlier (they nest like layers of an onion).

Common built-in middleware includes `CORSMiddleware`, `GZipMiddleware`, and `TrustedHostMiddleware`, all added via `app.add_middleware(...)`.

---

### Q21. How do you configure CORS in FastAPI, and why is it necessary? — **Intermediate**

**Answer:**
CORS (Cross-Origin Resource Sharing) restrictions are enforced by browsers to prevent a web page from one origin making requests to an API on a different origin unless explicitly allowed; FastAPI provides `CORSMiddleware` to configure this.

**Detailed explanation:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myfrontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
- `allow_origins`: which frontend origins can call this API (never use `["*"]` in production if `allow_credentials=True`, since that combination is disallowed by browsers for security reasons).
- `allow_credentials`: whether cookies/auth headers are allowed in cross-origin requests.
- `allow_methods` / `allow_headers`: restrict which HTTP methods/headers are permitted.

Without this, a browser-based frontend hosted on a different domain than your API would have its requests blocked by the browser (even though tools like Postman/curl bypass CORS entirely, since CORS is a browser-enforced policy, not a server-side security feature per se).

---

### Q22. When should a path operation be `async def` vs a regular `def`? — **Intermediate**

**Answer:**
Use `async def` when your function performs `await`-able I/O (async DB drivers, async HTTP clients); use regular `def` when your code is synchronous/blocking, and FastAPI will automatically run it in a separate thread pool so it doesn't block the event loop.

**Detailed explanation:**
```python
@app.get("/async-example")
async def async_example():
    result = await some_async_db_call()  # non-blocking
    return result

@app.get("/sync-example")
def sync_example():
    result = some_blocking_call()  # e.g., requests.get(), blocking DB driver
    return result
```
The critical mistake is writing an `async def` function that contains **blocking** synchronous code (like `time.sleep()` or a synchronous `requests.get()` call) — this blocks the entire event loop, stalling *all* concurrent requests being handled by that worker, not just the current one.

Rule of thumb:
- If everything inside is `await`-compatible (async ORM like `SQLAlchemy` async engine, `httpx.AsyncClient`, `asyncpg`) → use `async def`.
- If you must call blocking/synchronous libraries → use plain `def` (FastAPI runs these in Starlette's threadpool automatically) or explicitly offload blocking calls with `run_in_executor`.

---

### Q23. How do you manage application configuration/settings using Pydantic? — **Intermediate**

**Answer:**
FastAPI applications commonly use `pydantic-settings`' `BaseSettings` class to load configuration from environment variables (and `.env` files), validated and typed just like request bodies.

**Detailed explanation:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    database_url: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```
Usage as a dependency (useful for testing/overriding):
```python
from functools import lru_cache

@lru_cache
def get_settings():
    return Settings()

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name}
```
Benefits: type-checked config (e.g., `debug: bool` rejects a garbage string), a single source of truth for environment-dependent values, and easy mocking in tests by overriding the `get_settings` dependency via `app.dependency_overrides`.

---

### Q24. How do you write automated tests for a FastAPI application? — **Intermediate**

**Answer:**
FastAPI applications are typically tested using `TestClient` (built on `httpx`), combined with `pytest`, allowing you to make requests against your app in-process without running an actual server.

**Detailed explanation:**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_item():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}

def test_create_item():
    response = client.post("/items/", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
```
Best practices:
- Use `app.dependency_overrides[get_db] = get_test_db` to swap real dependencies (like a production DB session) with test doubles (an in-memory SQLite DB, or a mock).
- For fully async test clients (needed when testing lifespan events or truly async fixtures), `httpx.AsyncClient` with `ASGITransport` is used alongside `pytest-asyncio`.
- Fixtures (via `pytest.fixture`) are commonly used to set up/tear down test databases per test or per session.

---

### Q25. What path operation configuration options exist (tags, summary, deprecated, etc.), and why use them? — **Intermediate**

**Answer:**
Beyond the path and method, FastAPI decorators accept metadata parameters — `tags`, `summary`, `description`, `response_description`, `deprecated`, `operation_id` — that enrich the generated OpenAPI documentation without affecting runtime behavior.

**Detailed explanation:**
```python
@app.get(
    "/items/{item_id}",
    tags=["items"],
    summary="Get a single item",
    description="Retrieve a specific item by its unique identifier.",
    response_description="The requested item",
    deprecated=False,
)
async def get_item(item_id: int):
    """This docstring also appears in the docs if description isn't set."""
    return {"item_id": item_id}
```
- `tags`: groups endpoints together in the Swagger UI sidebar (e.g., all "users" endpoints under one collapsible section).
- `deprecated=True`: visually marks an endpoint as deprecated in the docs, signaling to API consumers it will be removed, without actually disabling it.
- These have zero effect on request handling — they exist purely to make auto-generated documentation clearer for API consumers and are heavily valued in real-world, multi-team API development.

---

### Q26. How do you handle file uploads in FastAPI? — **Intermediate**

**Answer:**
FastAPI provides `UploadFile` (paired with `File(...)`) to accept uploaded files efficiently, streaming them to a temporary spooled file rather than loading the entire file into memory upfront.

**Detailed explanation:**
```python
from fastapi import File, UploadFile

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "content_type": file.content_type, "size": len(contents)}
```
- `UploadFile` exposes `.filename`, `.content_type`, and async methods `.read()`, `.write()`, `.seek()`, `.close()`.
- Compared to using plain `bytes` (`file: bytes = File(...)`), `UploadFile` is more memory-efficient for large files because it's backed by `SpooledTemporaryFile`, spilling to disk only if the file exceeds a size threshold.
- Multiple files: `files: list[UploadFile] = File(...)`.
- To accept both files and form fields together, combine with `Form(...)` parameters in the same function signature (note: you cannot mix `File`/`Form` params with a JSON body Pydantic model in the same request, since the request becomes `multipart/form-data`).

---

### Q27. How do you handle traditional form data (not JSON) in FastAPI? — **Intermediate**

**Answer:**
Use the `Form()` marker on parameters to declare that data arrives as `application/x-www-form-urlencoded` or `multipart/form-data`, common for classic HTML form submissions or OAuth2 password flows.

**Detailed explanation:**
```python
from fastapi import Form

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```
- This requires installing `python-multipart` as a dependency.
- Unlike a Pydantic model body (which expects JSON), `Form()` parameters expect the request content-type to be form-encoded, matching what an HTML `<form>` element sends by default.
- This is the mechanism used in FastAPI's OAuth2 password-flow examples, since the OAuth2 spec mandates form-encoded credentials rather than JSON.

---

### Q28. How do you create custom exception handlers for specific exception types? — **Intermediate**

**Answer:**
Use `@app.exception_handler(SomeExceptionClass)` to register a function that intercepts a given exception type raised anywhere in your app and converts it into a custom, consistent response.

**Detailed explanation:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} not found"},
    )

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in db:
        raise ItemNotFoundError(item_id)
    return db[item_id]
```
This is preferable to sprinkling `try/except` + `HTTPException` throughout your codebase — you define custom domain exceptions once (e.g., in a `exceptions.py`), raise them naturally from business logic anywhere, and centralize the HTTP-response mapping in one place. You can also override FastAPI's default handlers for `RequestValidationError` and `HTTPException` this way to customize error response shape globally.

---

### Q29. What are the different Response classes in FastAPI, and when do you use each? — **Intermediate**

**Answer:**
FastAPI provides several `Response` subclasses beyond the default JSON — `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, and `FileResponse` — each suited to a different content type or delivery pattern.

**Detailed explanation:**
```python
from fastapi.responses import (
    JSONResponse, HTMLResponse, PlainTextResponse,
    RedirectResponse, StreamingResponse, FileResponse
)

@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>Hello</h1>"

@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="/docs")

@app.get("/download")
async def download():
    return FileResponse("report.pdf", media_type="application/pdf", filename="report.pdf")

@app.get("/stream")
async def stream():
    def generate():
        for i in range(1000):
            yield f"chunk {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")
```
- **`StreamingResponse`** is important for large files or generated content (like exporting a huge CSV) where you don't want to hold the entire payload in memory before sending it.
- **`FileResponse`** efficiently streams a file from disk, setting appropriate headers automatically.
- Setting `response_class` on the decorator changes the default rendering (and updates OpenAPI docs accordingly) without needing to construct the response object manually in every function.

---

### Q30. What is `APIRouter`, and how does it help organize larger applications? — **Intermediate**

**Answer:**
`APIRouter` lets you define path operations in separate modules/files and then combine them into the main `FastAPI` app via `include_router()`, mirroring how large applications are broken into logical sub-modules (users, items, orders, etc.).

**Detailed explanation:**
```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    return [...]

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {...}
```
```python
# main.py
from fastapi import FastAPI
from routers import users, items

app = FastAPI()
app.include_router(users.router)
app.include_router(items.router, prefix="/api/v1")
```
Benefits:
- Keeps large codebases maintainable by feature/domain rather than one giant `main.py`.
- `prefix` and `tags` set on the router apply to all routes within it, reducing repetition.
- Routers can have their own dependencies applied to *all* their routes: `APIRouter(dependencies=[Depends(verify_token)])`, useful for e.g. requiring auth on an entire section of the API.
- Supports arbitrary nesting — routers can include other routers.

---

## Advanced Questions

### Q31. How do dependencies with `yield` work, and why are they used for resource management (e.g., DB sessions)? — **Advanced**

**Answer:**
A dependency using `yield` instead of `return` lets you run setup code before the `yield` and teardown/cleanup code after it, with FastAPI guaranteeing the cleanup runs after the response has been sent — even if an exception occurred.

**Detailed explanation:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```
Execution flow:
1. FastAPI calls `get_db()`, runs code up to `yield`, and injects `db` into the path operation.
2. The path operation executes, using the session.
3. After the response is generated (or if an unhandled exception propagates), FastAPI resumes `get_db()` after the `yield`, running the `finally: db.close()` block.

This pattern is the standard way to manage anything requiring cleanup: database sessions, file handles, network connections, or locks. You can also catch exceptions inside the dependency itself using `try/except/finally` around the `yield`, allowing dependencies to participate in error handling (e.g., rolling back a transaction on failure) — this is sometimes called the "dependency with exception handling" pattern, though as of recent FastAPI versions there are nuances around how exceptions propagate through yield-dependencies that are worth testing carefully in your version.

---

### Q32. How do you implement OAuth2 Password Flow with JWT tokens in FastAPI? — **Advanced**

**Answer:**
FastAPI provides `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm` as building blocks; you combine them with a JWT library (like `python-jose` or `PyJWT`) to issue and validate signed tokens representing authenticated sessions.

**Detailed explanation:**
```python
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me")
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user
```
Key points:
- `OAuth2PasswordBearer(tokenUrl="token")` doesn't perform auth itself — it just tells FastAPI/Swagger UI where the token comes from and extracts the `Authorization: Bearer <token>` header.
- The actual verification (decoding the JWT, checking signature/expiry) is your custom logic inside `get_current_user`, used as a dependency on any protected route.
- Passwords should always be hashed (e.g., via `passlib`'s bcrypt) — never store or compare plaintext passwords.
- JWTs are stateless (no server-side session storage needed), but that means revoking a token before its expiry requires additional infrastructure (a blocklist/short expiry + refresh tokens).

---

### Q33. How do you implement role-based access control or OAuth2 scopes in FastAPI? — **Advanced**

**Answer:**
FastAPI's `Security` (an extension of `Depends`) supports OAuth2 "scopes" — granular permission strings embedded in the token — allowing you to require specific scopes per endpoint via `SecurityScopes`.

**Detailed explanation:**
```python
from fastapi import Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"items:read": "Read items", "items:write": "Write items"},
)

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
            )
    return get_user(payload.get("sub"))

@app.get("/items/")
async def list_items(user=Security(get_current_user, scopes=["items:read"])):
    return [...]

@app.post("/items/")
async def create_item(user=Security(get_current_user, scopes=["items:write"])):
    return {...}
```
For simpler role systems (not full OAuth2 scopes), many teams implement a lighter pattern: store a `role` field on the user, and write a dependency factory like `require_role("admin")` that raises 403 if `current_user.role != "admin"`. This is often preferred over full OAuth2 scopes when you don't need the complexity of the OAuth2 spec, and is a common interview topic when discussing pragmatic authorization design.

---

### Q34. How do you integrate SQLAlchemy (sync or async) with FastAPI properly? — **Advanced**

**Answer:**
You create a SQLAlchemy `Engine`/`AsyncEngine` and `SessionLocal` factory once at startup, then expose a per-request session via a `yield`-based dependency, ensuring each request gets an isolated session that's properly closed afterward.

**Detailed explanation:**

**Synchronous version:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine("postgresql://user:pass@localhost/db")
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

**Async version (using `asyncpg` driver):**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/items/")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```
Important considerations:
- Never share a single global session across requests — each request must get its own session to avoid data leaking or race conditions between concurrent requests.
- Mixing sync SQLAlchemy calls inside `async def` path operations blocks the event loop; either use the async SQLAlchemy engine end-to-end, or keep DB-using endpoints as regular `def` functions so FastAPI runs them in the threadpool.
- Connection pooling is handled by the `Engine` itself (configurable via `pool_size`, `max_overflow`), not by FastAPI.

---

### Q35. How do you implement WebSockets in FastAPI? — **Advanced**

**Answer:**
FastAPI supports WebSockets natively via the `@app.websocket()` decorator and a `WebSocket` object, enabling full-duplex, persistent connections for real-time features like chat or live notifications.

**Detailed explanation:**
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        print(f"Client #{client_id} disconnected")
```
Key points:
- `await websocket.accept()` completes the WebSocket handshake.
- The connection stays open for the lifetime of the `while True` loop; messages are sent/received with `send_text`/`send_json`/`send_bytes` and their `receive_*` counterparts.
- `WebSocketDisconnect` is raised when the client closes the connection — always handle it to clean up any shared state (e.g., removing the client from an active-connections registry).
- For broadcasting to multiple clients (like a chat room), you typically maintain a `ConnectionManager` class holding a list/dict of active `WebSocket` objects, iterating over them to `send_text` to all connected clients.
- Because WebSockets are stateful and long-lived, they interact differently with horizontal scaling than regular HTTP — you often need a pub/sub layer (like Redis Pub/Sub) to broadcast messages across multiple server instances/workers.

---

### Q36. How does `lifespan` differ from the older `@app.on_event("startup"/"shutdown")` approach? — **Advanced**

**Answer:**
`lifespan` is the modern, recommended way (using an async context manager) to run startup and shutdown logic, replacing the deprecated `@app.on_event()` decorators, and it more naturally supports resources that need to be held open for the app's whole lifetime.

**Detailed explanation:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    ml_models["model"] = load_model()
    yield
    # Shutdown logic
    ml_models.clear()

app = FastAPI(lifespan=lifespan)
```
Advantages over `@app.on_event`:
- A single function handles both startup and shutdown, keeping related setup/teardown logic visually together (versus two separate decorated functions).
- Because it's a proper async context manager, resources (like a shared `httpx.AsyncClient` or a connection pool) can be created before `yield` and reliably cleaned up after, even accounting for exceptions.
- `@app.on_event` is deprecated as of recent FastAPI versions and may be removed in the future, so `lifespan` is the interview-correct, forward-compatible answer.

This is commonly used for: loading ML models once at startup (rather than per-request), establishing a shared DB connection pool, or setting up caches/clients that should persist for the app's lifetime.

---

### Q37. When should you offload work to Celery instead of FastAPI's `BackgroundTasks`? — **Advanced**

**Answer:**
Use Celery (or similar distributed task queues like RQ, Dramatiq, or arq) when tasks are long-running, need to survive a server restart, require retries/scheduling, or need to be distributed across multiple machines — none of which `BackgroundTasks` provides.

**Detailed explanation:**
Comparison:

| Requirement | BackgroundTasks | Celery |
|---|---|---|
| Runs after response sent | Yes | Yes (via message broker) |
| Survives process crash | No | Yes (task persisted in broker) |
| Retry on failure | Manual only | Built-in retry policies |
| Distributed across machines | No (same process) | Yes (multiple workers) |
| Scheduling (run at 3am) | No | Yes (Celery Beat) |
| Task monitoring/dashboard | No | Yes (Flower, etc.) |
| Suitable for heavy CPU work | Risky (shares process resources) | Yes (isolated worker processes) |

A typical FastAPI + Celery setup: the API enqueues a task message onto a broker (Redis/RabbitMQ), returns an immediate response (e.g., `202 Accepted` with a task ID), and separate Celery worker processes pick up and execute the task independently. The client can poll a `/tasks/{task_id}` endpoint (or receive a webhook/websocket update) to check completion status. This decoupling is essential for things like video processing, sending bulk emails, generating large reports, or any workload that shouldn't risk destabilizing the API's own request-handling capacity.

---

### Q38. How do you implement API versioning in FastAPI? — **Advanced**

**Answer:**
There's no single built-in versioning mechanism in FastAPI — the common approaches are URL path versioning (`/v1/`, `/v2/`), header-based versioning, or separate `APIRouter`/sub-application instances per version, with URL path versioning being the most widely adopted in practice.

**Detailed explanation:**

**1. Path-based versioning (most common):**
```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/items/")
async def list_items_v1():
    return {"version": 1, "items": [...]}

@v2_router.get("/items/")
async def list_items_v2():
    return {"version": 2, "items": [...], "meta": {...}}

app.include_router(v1_router)
app.include_router(v2_router)
```

**2. Separate sub-applications mounted at different prefixes:**
```python
app_v1 = FastAPI()
app_v2 = FastAPI()

app = FastAPI()
app.mount("/v1", app_v1)
app.mount("/v2", app_v2)
```
This fully isolates each version's docs, middleware, and dependency graph — useful when versions diverge significantly.

**3. Header-based versioning** (e.g., `Accept: application/vnd.myapi.v2+json`): implemented via a custom dependency that inspects request headers and dispatches accordingly — less discoverable via URL but avoids proliferating URL paths.

Trade-offs: path-based versioning is the most explicit and cache-friendly (different URLs are trivially cacheable independently), but can lead to significant code duplication across versions if not carefully abstracted with shared internal service layers.

---

### Q39. How would you implement rate limiting for a FastAPI application? — **Advanced**

**Answer:**
Rate limiting in FastAPI is typically implemented either via third-party middleware/dependency libraries like `slowapi` (a FastAPI adaptation of Flask-Limiter) backed by Redis, or via a reverse proxy/gateway layer (Nginx, API Gateway, Traefik) in front of the app.

**Detailed explanation:**
Application-level example using `slowapi`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/items/")
@limiter.limit("5/minute")
async def list_items(request: Request):
    return [...]
```
Design considerations:
- **Key function**: how you identify "who" is being rate limited — IP address, API key, or authenticated user ID. IP-based limiting is weaker behind shared NATs/proxies; API-key or user-based limiting is more precise.
- **Storage backend**: in-memory counters only work for a single-process deployment; multi-worker/multi-instance deployments need a shared store like Redis so limits are enforced globally, not per-process.
- **Algorithm choice**: fixed window (simple, but bursts at window boundaries), sliding window, or token bucket (smoother, industry-standard for APIs).
- **Where to enforce it**: application-level (fine-grained, per-endpoint control, but consumes app resources for rejected requests) vs. gateway/proxy-level (rejects requests before they even reach your app, better for protecting against high-volume abuse/DDoS-style traffic).

In interviews, it's valuable to mention that for serious production systems, rate limiting is often layered: coarse limits at the gateway/CDN level, finer per-user/per-endpoint limits at the application level.

---

### Q40. How would you add caching to a FastAPI application, and what are the trade-offs? — **Advanced**

**Answer:**
Caching in FastAPI is commonly implemented at the response level (using libraries like `fastapi-cache2` backed by Redis or in-memory stores) or manually within business logic, trading off data freshness for reduced latency and database load.

**Detailed explanation:**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/items/{item_id}")
@cache(expire=60)  # cache for 60 seconds
async def get_item(item_id: int):
    return await slow_db_lookup(item_id)
```
Key trade-offs and considerations:
- **Cache invalidation**: the classic hard problem — when the underlying data changes (an item is updated), the cache must be invalidated or it will serve stale data. Strategies include TTL expiry (simple but allows staleness within the window), explicit invalidation on writes (more complex but more accurate), or cache versioning.
- **What to cache**: read-heavy, rarely-changing, or expensive-to-compute endpoints (aggregations, external API calls) benefit most; highly personalized or frequently-changing data benefits less.
- **Where to cache**: in-process memory (fastest, but not shared across multiple worker processes/instances, and lost on restart) vs. Redis/Memcached (shared across all instances, survives restarts, slight network overhead).
- **HTTP caching headers**: an alternative/complementary approach — setting `Cache-Control`, `ETag`, and `Last-Modified` headers lets browsers and CDNs cache responses without any server-side cache infrastructure at all, appropriate for public, cacheable GET endpoints.

---

### Q41. What are the major differences between Pydantic v1 and v2, and why does it matter for FastAPI developers? — **Advanced**

**Answer:**
Pydantic v2 (a near-complete rewrite with a Rust core called `pydantic-core`) brought major performance improvements and several breaking API changes — method renames, stricter validation defaults, and a new configuration style — that FastAPI developers must account for depending on which version their project uses.

**Detailed explanation:**
Key differences:

| Aspect | Pydantic v1 | Pydantic v2 |
|---|---|---|
| Core implementation | Pure Python | Rust core (`pydantic-core`) — much faster |
| Serialization | `.dict()`, `.json()` | `.model_dump()`, `.model_dump_json()` |
| Validation | `.parse_obj()` | `.model_validate()` |
| Field validators | `@validator` | `@field_validator` (different signature) |
| Config | inner `class Config:` | `model_config = ConfigDict(...)` |
| Settings management | Built into `pydantic` (`BaseSettings`) | Moved to separate `pydantic-settings` package |
| Strictness | More lenient coercion by default | Stricter by default (e.g., won't silently coerce `"123"` to `int` in some contexts unless configured) |

Practical implications:
- FastAPI versions 0.100+ support Pydantic v2 as default; older FastAPI projects may still be pinned to Pydantic v1, so recognizing which API you're working with (`.dict()` vs `.model_dump()`) is a common real-world debugging scenario.
- Performance-sensitive applications benefit significantly from v2's Rust core — validation and serialization can be several times faster.
- Some third-party libraries lag behind in migrating to v2, which historically caused dependency conflicts — a relevant discussion point for "how do you handle library compatibility issues" style interview questions.

---

### Q42. How do you customize the generated OpenAPI schema beyond what decorators expose? — **Advanced**

**Answer:**
You can override `app.openapi()` entirely with a custom function that programmatically modifies the generated schema dictionary — useful for adding custom metadata, security schemes, or examples not directly expressible through standard FastAPI parameters.

**Detailed explanation:**
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My Custom API",
        version="2.5.0",
        description="A custom description with extra markdown support.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```
Common use cases:
- Adding custom `x-` vendor extension fields consumed by API gateways or documentation portals.
- Injecting global security schemes (e.g., API key headers) that apply across all endpoints without repeating `Security()` dependencies everywhere.
- Modifying example values or descriptions dynamically (e.g., pulling live example data from a database at startup).
- Excluding internal/admin-only routes from the public-facing schema selectively, beyond the simple `include_in_schema=False` flag available per-route.

The `app.openapi_schema` caching pattern shown above (checking `if app.openapi_schema` first) avoids regenerating the schema on every request to `/openapi.json`, since schema generation can be a nontrivial amount of work for large APIs.

---

### Q43. How does FastAPI handle concurrency internally, and how does the GIL affect this? — **Advanced**

**Answer:**
FastAPI (via Starlette/asyncio) achieves high concurrency for I/O-bound work through a single-threaded event loop that switches between tasks during `await` points; CPU-bound work still contends with Python's Global Interpreter Lock (GIL) and does not get true parallelism within a single process regardless of `async`/`await` usage.

**Detailed explanation:**
- The event loop can juggle thousands of concurrent connections because most of a typical request's time is spent *waiting* (for a database, an external API, disk I/O) — during these waits, `await` yields control back to the loop, letting it work on other requests.
- This is fundamentally different from true multi-threaded parallelism: there's still only one thread executing Python bytecode at a time (the GIL), so `async def` does **not** help CPU-bound work (heavy computation, image processing, data crunching) — it can actually make things worse if such blocking work occupies the event loop, since it stalls every other in-flight request until it finishes.
- For CPU-bound work, the standard solutions are: run it in a separate process pool (`concurrent.futures.ProcessPoolExecutor`, invoked via `loop.run_in_executor`), offload it to a background worker (Celery), or use a compiled/optimized library (NumPy, which releases the GIL internally for many operations).
- For blocking I/O libraries that don't have async equivalents, regular `def` path operations are automatically run in Starlette's threadpool, allowing the main event loop to remain responsive even though that particular call is blocking within its own thread.
- Horizontal scaling (multiple Uvicorn/Gunicorn worker **processes**) is how you get true parallelism across CPU cores, since each worker process has its own Python interpreter and thus its own GIL.

This distinction — I/O-bound concurrency (where async shines) vs. CPU-bound parallelism (where it doesn't help) — is one of the most commonly probed advanced FastAPI/async interview topics.

---

### Q44. How do you deploy a FastAPI application to production reliably? — **Advanced**

**Answer:**
Production deployment typically involves running Uvicorn workers managed by a process supervisor like Gunicorn (or using Uvicorn's own built-in multi-worker mode), behind a reverse proxy (Nginx or a cloud load balancer), often containerized with Docker, with proper handling of logging, health checks, and graceful shutdown.

**Detailed explanation:**
A common production stack:
```
Client → Load Balancer / Nginx → Gunicorn (process manager) → N × Uvicorn worker processes → FastAPI app
```
Example Gunicorn command:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
Key production considerations:
- **Number of workers**: a common heuristic is `(2 × CPU cores) + 1`, though this should be tuned based on whether the workload is I/O-bound or CPU-bound.
- **Reverse proxy**: Nginx (or a cloud LB) handles TLS termination, static file serving, request buffering, and can add another layer of protection (rate limiting, IP filtering) in front of the app servers.
- **Health checks**: expose a lightweight `/health` endpoint that checks critical dependencies (DB connectivity) so orchestrators (Kubernetes, ECS) can detect and restart unhealthy instances.
- **Graceful shutdown**: ensure in-flight requests complete before a worker is killed during a deployment/restart (Uvicorn/Gunicorn support graceful timeout configuration).
- **Containerization**: a typical `Dockerfile` installs dependencies, copies the app, and runs Uvicorn/Gunicorn as the container's entrypoint; container orchestration (Kubernetes, ECS, Docker Swarm) then handles scaling, restarts, and rolling deployments.
- **Logging & observability**: structured logging (JSON logs), request tracing (e.g., OpenTelemetry), and metrics (Prometheus) are commonly integrated via middleware for production visibility.
- **Environment-specific config**: never hardcode secrets; use environment variables or a secrets manager (Vault, AWS Secrets Manager), loaded via the `Settings`/`BaseSettings` pattern discussed earlier.

---

### Q45. How do you mount a sub-application or serve static files alongside your API in FastAPI? — **Advanced**

**Answer:**
FastAPI supports `app.mount()` to attach an entirely separate ASGI application (including another FastAPI instance, or Starlette's `StaticFiles`) at a given path prefix, useful for serving static assets or completely isolating a sub-system's routing/docs/middleware.

**Detailed explanation:**
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```
This serves any file placed in the local `static/` directory at URLs like `/static/logo.png`, handled directly by Starlette's efficient static file serving (including proper `Content-Type`, range requests for video/audio, and caching headers) without writing a custom path operation.

Mounting a full sub-application:
```python
sub_app = FastAPI(title="Sub API")

@sub_app.get("/")
async def sub_root():
    return {"message": "Hello from sub-app"}

app.mount("/subapi", sub_app)
```
Important nuances:
- A mounted sub-application gets its **own** independent OpenAPI docs (`/subapi/docs`), middleware stack, and exception handlers — it doesn't inherit the parent app's dependencies or middleware automatically.
- This is different from `include_router()`, which merges routes into the *same* app (sharing the same docs, middleware, and dependency graph) — `mount()` is for genuine isolation (e.g., embedding a legacy service, or serving a completely separate internal admin API under the same domain).
- Path matching for mounted routes is checked as a prefix match, so ensure mount paths don't unintentionally shadow other routes declared on the main app.

---

## Quick-Reference Summary Table

| # | Question | Level |
|---|---|---|
| 1 | What is FastAPI and why popular | Beginner |
| 2 | FastAPI vs Flask vs Django | Beginner |
| 3 | WSGI vs ASGI | Beginner |
| 4 | Basic path operations | Beginner |
| 5 | Path parameters & type conversion | Beginner |
| 6 | Query parameters | Beginner |
| 7 | Request body validation | Beginner |
| 8 | Pydantic BaseModel | Beginner |
| 9 | response_model | Beginner |
| 10 | Custom status codes | Beginner |
| 11 | Automatic docs generation | Beginner |
| 12 | HTTPException | Beginner |
| 13 | HTTP method decorators & REST | Beginner |
| 14 | Uvicorn | Beginner |
| 15 | Type hints role | Beginner |
| 16 | Dependency Injection basics | Intermediate |
| 17 | Nested dependencies | Intermediate |
| 18 | Custom Pydantic validators | Intermediate |
| 19 | Background Tasks | Intermediate |
| 20 | Custom middleware | Intermediate |
| 21 | CORS configuration | Intermediate |
| 22 | async def vs def | Intermediate |
| 23 | Settings management | Intermediate |
| 24 | Testing with TestClient | Intermediate |
| 25 | Path operation metadata | Intermediate |
| 26 | File uploads | Intermediate |
| 27 | Form data | Intermediate |
| 28 | Custom exception handlers | Intermediate |
| 29 | Response classes | Intermediate |
| 30 | APIRouter | Intermediate |
| 31 | yield dependencies | Advanced |
| 32 | OAuth2 + JWT | Advanced |
| 33 | Scopes / RBAC | Advanced |
| 34 | SQLAlchemy integration | Advanced |
| 35 | WebSockets | Advanced |
| 36 | lifespan vs on_event | Advanced |
| 37 | Celery vs BackgroundTasks | Advanced |
| 38 | API versioning | Advanced |
| 39 | Rate limiting | Advanced |
| 40 | Caching | Advanced |
| 41 | Pydantic v1 vs v2 | Advanced |
| 42 | Custom OpenAPI schema | Advanced |
| 43 | Concurrency & GIL | Advanced |
| 44 | Production deployment | Advanced |
| 45 | Mounting sub-apps / static files | Advanced |

---

*Good luck with your interview preparation! Focus extra time on the Advanced section if you're interviewing for a senior/backend-architecture role, since concurrency, auth, and deployment topics tend to come up most in system-design-style discussions.*
