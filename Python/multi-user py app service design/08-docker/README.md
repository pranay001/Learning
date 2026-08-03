# Module 08 — Docker: Packaging the App to Run Identically Everywhere

## Concept

A container packages your app + its exact dependencies + runtime into one portable image, so "works on my
machine" stops being a problem. This is the unit you'll scale horizontally in Modules 09-10.

| Term | Meaning |
|------|---------|
| **Image** | A built, immutable snapshot of your app + dependencies |
| **Container** | A running instance of an image |
| **Dockerfile** | Instructions to build an image |
| **Layer caching** | Docker reuses unchanged build steps to speed up rebuilds |
| **docker-compose** | Defines and runs multiple related containers together (app + DB + Redis + workers) |
| **Multi-stage build** | Using one stage to build/compile, and a leaner final stage to run — smaller images |

## Hands-On Lab

### Step 1 — A minimal but production-sane Dockerfile

Project layout:

```
myapp/
├── main.py
├── celery_app.py
├── tasks.py
├── database.py
├── models.py
├── requirements.txt
└── Dockerfile
```

`requirements.txt`:

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
gunicorn==23.0.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
redis==5.0.8
celery==5.4.0
slowapi==0.1.9
python-jose[cryptography]==3.3.0
httpx==0.27.2
```

`Dockerfile` (uses `uv` for dependency installation instead of `pip` — the official `uv` static binary is
copied in from Astral's distroless image, and `uv pip install` installs into an isolated venv so we can
cleanly copy that venv into the final image):

```dockerfile
# ---- Stage 1: build dependencies in an isolated layer, using uv ----
FROM python:3.12-slim AS builder

# Copy the uv binary itself from Astral's official distributed image — no pip/curl install needed
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY requirements.txt .

# Create an isolated venv with uv and install into it (much faster than pip, and produces
# a self-contained folder we can copy wholesale into the final stage below)
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt

# ---- Stage 2: lean final image ----
FROM python:3.12-slim

WORKDIR /app

# Copy only the built venv from the builder stage — no uv binary, no build tools, no bloat
COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Run as a non-root user (security best practice)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Healthcheck lets orchestrators know if the container is actually serving traffic
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "30"]
```

**Why this shape:** `uv venv` builds a normal virtual environment at `/opt/venv`, and because it's just a
regular folder of Python + installed packages, we can copy that whole folder into the slim final stage
and point `PATH` at it — same effect as the old `pip install --user` + `/root/.local` copy trick, but the
install step itself runs through `uv`'s much faster resolver instead of pip.

Add a health endpoint to `main.py` (needed by the HEALTHCHECK above and later by Kubernetes):

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### Step 2 — Build and run it standalone

```bash
docker build -t learning-api:v1 .
docker run -p 8000:8000 --name learning-api-container learning-api:v1
```

Test: `curl http://localhost:8000/health`

**Lab exercise:** Run `docker build` a second time with no code changes and note it's much faster —
that's layer caching. Then change one line in `main.py` and rebuild — notice only the layers after the
`COPY . .` step rebuild, not the dependency install step (as long as `requirements.txt` didn't change).

### Step 3 — Compose the full stack: API + Postgres + Redis + Celery worker

Create `docker-compose.yml` at the project root:

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://appuser:apppass@db:5432/appdb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  worker:
    build: .
    command: celery -A celery_app worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: postgresql+asyncpg://appuser:apppass@db:5432/appdb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

Note the important detail: inside Docker's network, services reach each other **by service name**
(`db`, `redis`), not `localhost` — update your `DATABASE_URL`/Redis host accordingly (read from env vars,
as shown, rather than hardcoding `localhost` like in earlier modules).

### Step 4 — Run the whole stack with one command

```bash
docker compose up --build
```

Verify all four containers are healthy:

```bash
docker compose ps
```

Test the API is reachable and can talk to both Postgres and Redis:

```bash
curl -X POST "http://localhost:8000/products?name=Widget&price=9.99&stock=100"
curl http://localhost:8000/products/1
```

### Step 5 — Scale the API and worker independently with Compose

```bash
docker compose up --scale api=3 --scale worker=2 -d
docker compose ps
```

Notice: you now have 3 API containers and 2 worker containers, but no load balancer yet directing traffic
across the 3 API replicas — that's exactly the gap Module 09 fills.

## Checkpoint Questions

1. Why does the multi-stage build produce a smaller final image than a single-stage build?
2. Why should the container run as a non-root user?
3. Why do services in `docker-compose.yml` refer to each other by service name instead of `localhost`?
4. What problem does `depends_on: condition: service_healthy` solve that a plain `depends_on` doesn't?

## What's Next

Module 09 puts a load balancer (NGINX) in front of your scaled API containers so traffic is actually
distributed across them.
