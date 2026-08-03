# Module 06 — Background Work with Celery: Not Blocking the API for Slow Tasks

## Concept

Some work is too slow (sending emails, generating reports, processing images/video, calling slow external
APIs) or too CPU-heavy (Module 02's problem) to run inline during a request — it would tie up a worker
process and hurt every other user's response time. The fix: the API **enqueues** a task and immediately
returns; a separate pool of **worker processes** picks up tasks from the queue and executes them,
possibly on entirely different machines.

| Term | Meaning |
|------|---------|
| **Task queue / message broker** | Where pending tasks wait (Redis or RabbitMQ) |
| **Celery worker** | A separate process that pulls tasks off the queue and executes them |
| **Task ID** | A handle returned immediately so the client can poll for the result later |
| **Result backend** | Where task results are stored so they can be retrieved after completion (often Redis) |
| **Idempotency** | Designing tasks so re-running them (e.g. after a retry) doesn't cause duplicate side effects |
| **Retry / backoff** | Automatically re-attempting a failed task, with increasing delay |

## Hands-On Lab

### Step 1 — Install Celery (Redis, from Module 05, doubles as the broker)

```bash
uv pip install celery redis fastapi uvicorn[standard]
```

Make sure Redis is still running (`docker ps` should show `learning-redis`; if not, rerun the command
from Module 05 Step 1).

### Step 2 — Define the Celery app and a task

Create `celery_app.py`:

```python
from celery import Celery

celery_app = Celery(
    "learning_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
)
```

Create `tasks.py`:

```python
import time
from celery_app import celery_app

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def generate_report(self, report_type: str, user_id: int):
    """Simulates a slow report-generation job."""
    try:
        time.sleep(10)  # simulate heavy work: querying, aggregating, rendering a PDF, etc.
        if report_type == "broken":
            raise ValueError("Simulated failure for retry demo")
        return {"report_type": report_type, "user_id": user_id, "status": "complete", "pages": 42}
    except ValueError as exc:
        raise self.retry(exc=exc)

@celery_app.task
def send_notification_email(user_id: int, message: str):
    time.sleep(2)  # simulate SMTP call
    print(f"[EMAIL SENT] to user {user_id}: {message}")
    return {"user_id": user_id, "delivered": True}
```

### Step 3 — Start a Celery worker (a separate process from your API!)

```bash
celery -A celery_app worker --loglevel=info --concurrency=4
```

Leave this running in its own terminal. `--concurrency=4` means it can process 4 tasks in parallel
(internally using either processes or threads depending on the "pool" — default is prefork/processes,
which is correct for CPU-heavy tasks per Module 02's lesson).

### Step 4 — Wire task submission into FastAPI

Create `main.py`:

```python
from fastapi import FastAPI
from tasks import generate_report, send_notification_email
from celery.result import AsyncResult
from celery_app import celery_app

app = FastAPI()

@app.post("/reports")
def request_report(report_type: str, user_id: int):
    # .delay() enqueues the task and returns IMMEDIATELY — no blocking
    task = generate_report.delay(report_type, user_id)
    return {"task_id": task.id, "status": "queued"}

@app.get("/reports/{task_id}")
def get_report_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    response = {"task_id": task_id, "state": result.state}
    if result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.result)
    return response

@app.post("/notify")
def notify_user(user_id: int, message: str):
    send_notification_email.delay(user_id, message)
    return {"status": "notification queued"}
```

Run the API: `uvicorn main:app --reload`

### Step 5 — Prove the API doesn't block

```bash
time curl -X POST "http://localhost:8000/reports?report_type=sales&user_id=1"
```

Notice the response returns almost instantly (just the `task_id`) even though the actual report takes
10 seconds. Now poll for the result:

```bash
# copy the task_id from the previous response
curl http://localhost:8000/reports/<task_id>
# run again after ~10s
curl http://localhost:8000/reports/<task_id>
```

Watch it transition from `PENDING`/`STARTED` to `SUCCESS`.

### Step 6 — Load test: many users queueing tasks simultaneously

```bash
for i in $(seq 1 15); do
  curl -s -X POST "http://localhost:8000/reports?report_type=sales&user_id=$i" &
done
wait
```

All 15 requests return near-instantly. Watch your Celery worker terminal — it processes up to 4 at a
time (your `--concurrency` setting) while the rest queue up. This is the key insight: **the API's
responsiveness is decoupled from the task's actual execution time.**

### Step 7 — See retry behavior

```bash
curl -X POST "http://localhost:8000/reports?report_type=broken&user_id=99"
```

Watch the Celery worker log — you'll see it fail and automatically retry (per
`max_retries=3, default_retry_delay=5`), demonstrating built-in resilience for transient failures.

### Step 8 — Scale workers independently from the API

This is the real payoff: you can scale API instances and worker instances **independently** based on
where the bottleneck actually is.

```bash
# Terminal A: run more worker concurrency (simulating another machine's capacity)
celery -A celery_app worker --loglevel=info --concurrency=8 --hostname=worker2@%h
```

Now you have two worker processes (from Step 3 and this one) both pulling from the same queue — Celery
distributes tasks between them automatically.

## Checkpoint Questions

1. Why shouldn't `generate_report` just run directly inside the `/reports` FastAPI endpoint?
2. What would happen to API response times for ALL users if 50 people requested reports at once and there was no task queue?
3. Why is `result_backend` (Redis DB 1) kept separate from the broker (Redis DB 0) here?
4. Why does retry logic matter more in a distributed system than in a single-process script?

## What's Next

Now that users can trigger both instant and background work, Module 07 covers identifying *who* is
calling your API and protecting it from abuse.
