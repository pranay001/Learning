# Module 03 — Worker Processes: Using All Your CPU Cores

## Concept

A single `uvicorn` process is still just **one OS process with one GIL**. To actually use multiple CPU
cores for handling requests (not for one big CPU task — that's Module 06's job — but for *serving many
simultaneous requests*), you run **multiple worker processes**, each with its own event loop, behind a
process manager.

Key concepts:

| Term | Meaning |
|------|---------|
| **Worker process** | An independent OS process running its own copy of your app |
| **Process manager** | A supervisor that starts/monitors/restarts worker processes (Gunicorn) |
| **Load distribution** | The OS/process manager routes incoming connections across workers |
| **Statelessness** | Because requests can land on *any* worker, workers must not rely on in-memory state that another worker needs (that's why we'll externalize state to Redis/DB in later modules) |
| **Worker count formula** | Common rule of thumb: `(2 × CPU cores) + 1` for mixed I/O/CPU workloads |

## Hands-On Lab

### Step 1 — Install Gunicorn

```bash
uv pip install gunicorn uvicorn[standard] fastapi
```

### Step 2 — A test app that reveals which process handled each request

Create `main.py`:

```python
from fastapi import FastAPI
import os
import time

app = FastAPI()

@app.get("/whoami")
def whoami():
    return {"pid": os.getpid()}

@app.get("/work")
def work():
    # Simulate a moderately expensive synchronous task
    total = 0
    for i in range(20_000_000):
        total += i
    return {"pid": os.getpid(), "total": total}
```

### Step 3 — Run with a single worker first

```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000
```

In another terminal, fire several concurrent requests:

```bash
for i in 1 2 3 4; do curl -s http://localhost:8000/whoami & done; wait
```

Notice: all requests report the **same PID** — one process handled everything sequentially/cooperatively.

### Step 4 — Scale to multiple workers

Stop the previous command (Ctrl+C) and run:

```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

Repeat the concurrent curl test:

```bash
for i in 1 2 3 4 5 6 7 8; do curl -s http://localhost:8000/whoami & done; wait
```

Now you should see **different PIDs** — Gunicorn's OS-level connection distribution is spreading requests
across 4 independent processes, each capable of running on a separate CPU core.

### Step 5 — Measure throughput difference under real load

Install a simple load-testing tool:

```bash
uv pip install locust
```

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def hit_work_endpoint(self):
        self.client.get("/work")
```

Run Locust against your 1-worker version, note requests/sec, then repeat against the 4-worker version:

```bash
locust -f locustfile.py --headless -u 20 -r 5 -t 30s --host http://localhost:8000
```

Compare the `Requests/s` and average latency in the summary output between 1 worker and 4 workers.

**Checkpoint:** Why does 4 workers usually give roughly (but not exactly) 4x throughput for CPU-ish sync
work, but far less benefit for pure I/O-bound `async def` routes that were already handling concurrency
well within one process?

### Step 6 — Combine async concurrency + multiple workers (the real-world default)

The production pattern is: **async endpoints** (for cheap, high concurrency per process) **+ multiple
worker processes** (to use all cores) **+ a load balancer in front** (Module 09) if you need more than one
machine.

```bash
gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  -b 0.0.0.0:8000 \
  --timeout 30 \
  --graceful-timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

Notes on the flags:
- `--timeout 30`: kill a worker if a request takes longer than 30s (prevents one stuck worker from hanging forever)
- `--max-requests 1000 --max-requests-jitter 50`: restart each worker after ~1000 requests (helps with memory leaks in long-running processes; jitter avoids all workers restarting simultaneously)
- `--graceful-timeout 30`: on shutdown/restart, let in-flight requests finish for up to 30s

## Checkpoint Questions

1. If workers are independent OS processes, why can't Worker A directly read a Python variable set by Worker B?
2. Why do we need `--max-requests` in production but usually not while developing locally?
3. What's the difference between "scaling workers" (this module) and "scaling machines" (Module 09/10)?

## What's Next

Now that multiple workers can hit your app in parallel, they'll all need to talk to a shared database
safely. Module 04 covers connection pooling.
