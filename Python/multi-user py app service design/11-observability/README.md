# Module 11 — Observability: Understanding Behavior Across Many Parallel Requests

## Concept

With multiple workers, multiple containers, and multiple machines all handling concurrent requests, you
can no longer just "read the terminal output" to understand what's happening. You need structured,
correlatable, aggregatable signals.

| Term | Meaning |
|------|---------|
| **Structured logging** | Logs as machine-parsable JSON (fields), not free-text sentences |
| **Correlation ID / Request ID** | A unique ID attached to a request, threaded through every log line and downstream call, so you can reconstruct one request's full journey across services |
| **Metrics** | Numeric time-series data (request count, latency, error rate, queue depth) |
| **Tracing** | Following a single request's timeline across multiple services/functions, showing where time was spent |
| **The four golden signals** | Latency, traffic, errors, saturation — the standard starting point for what to monitor |

## Hands-On Lab

### Step 1 — Structured logging with request correlation IDs

```bash
uv pip install python-json-logger
```

Create/extend `main.py`:

```python
import logging
import time
import uuid
from fastapi import FastAPI, Request
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("api")
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(duration_ms)s"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI()

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "duration_ms": duration_ms,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
        },
    )
    return response
```

Run it and issue a few requests, then look at the log output — each line is a JSON object you could feed
directly into a log aggregation system (ELK stack, Loki, Datadog, CloudWatch Logs Insights, etc.) and
query by `request_id`, filter by `status_code >= 500`, or aggregate `duration_ms` percentiles.

**Lab exercise:** Add the same `request_id` propagation to a downstream call (e.g. when calling Celery in
Module 06 or another service) by passing it along as a header/kwarg, so one user's request can be traced
end-to-end even across process boundaries.

### Step 2 — Metrics with Prometheus

```bash
uv pip install prometheus-fastapi-instrumentator
```

Add to `main.py`:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)  # exposes /metrics automatically
```

Run the app, hit a few endpoints, then check:

```bash
curl http://localhost:8000/metrics
```

You'll see auto-generated metrics like `http_requests_total`, `http_request_duration_seconds` — broken
down by path, method, and status code.

### Step 3 — Run Prometheus + Grafana to visualize it

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "learning-api"
    static_configs:
      - targets: ["host.docker.internal:8000"]   # adjust if running via docker-compose service names
```

```bash
docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d --name grafana -p 3000:3000 grafana/grafana
```

- Visit `http://localhost:9090` (Prometheus) — try the query `rate(http_requests_total[1m])`
- Visit `http://localhost:3000` (Grafana, default login admin/admin) — add Prometheus as a data source
  (`http://host.docker.internal:9090`) and build a dashboard panel showing request rate and p95 latency.

### Step 4 — Generate load and watch the dashboard react

Reuse Locust from Module 03 to hammer the API for a few minutes while watching your Grafana panel —
you should see request rate and latency shift in near real-time, giving you a live picture of how your
service behaves under concurrent load (tying directly back to Modules 02-03's concepts).

### Step 5 — Alerting on the golden signals (conceptual + minimal example)

Add an alerting rule concept to `prometheus.yml` (rules file referenced separately in real setups):

```yaml
# alert_rules.yml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Error rate above 5% for 2+ minutes"
```

This is the pattern used in production: define a threshold on one of the golden signals, and get paged
before users notice widespread problems, not after.

## Checkpoint Questions

1. Why is a `request_id` essential once you have multiple workers/containers handling concurrent requests, but less important in a single-user script?
2. Why prefer structured (JSON) logs over free-text logs at scale?
3. What are the "four golden signals" and why start there instead of logging everything imaginable?
4. If p95 latency spikes but average latency looks fine, what does that suggest, and why does average alone hide it?

## What's Next

Module 12 (Capstone) combines every module — FastAPI, async, workers, DB pooling, Redis caching, Celery,
auth/rate limiting, Docker, NGINX, and observability — into one coherent, runnable project.
