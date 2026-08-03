# Module 12 — Capstone: A Complete Parallel, Multi-User API Service

## Goal

Combine every concept from Modules 01-11 into one working service: a **Product Catalog & Order API**
where many users can browse products (cached, DB-backed), place orders (safely, under concurrent writes),
trigger background report generation (Celery), all behind auth + rate limiting, load-balanced across
replicas, containerized, and observable.

## Architecture

```
        many parallel users
               │
               ▼
        ┌────────────┐
        │   NGINX    │  (Module 09: load balancing, edge rate limiting)
        └─────┬──────┘
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
┌──────┐  ┌──────┐   ┌──────┐
│ API  │  │ API  │   │ API  │   (Modules 01-02-03: FastAPI async, Gunicorn workers)
│ (x3) │  │      │   │      │   (Module 07: JWT auth + Redis-backed rate limiting)
└──┬───┘  └──┬───┘   └──┬───┘   (Module 11: structured logs + /metrics)
   │         │          │
   └────┬────┴────┬─────┘
        ▼         ▼
   ┌─────────┐ ┌─────────┐
   │ Postgres│ │  Redis  │  (Module 04: pooled async access)
   │ (pooled)│ │ (cache, │  (Module 05: cache-aside + stampede lock)
   └─────────┘ │ broker, │  (Module 06: Celery broker/result backend)
               │ limiter)│  (Module 07: rate-limit storage)
               └────┬────┘
                     ▼
              ┌─────────────┐
              │Celery workers│  (Module 06: async report generation)
              │   (x2)       │
              └─────────────┘
```

## Directory contents

```
12-capstone-project/
├── app/
│   ├── main.py              # FastAPI app: routes, auth, rate limiting, caching, logging
│   ├── database.py          # async engine + pooled sessions
│   ├── models.py            # SQLAlchemy models (Product, Order)
│   ├── celery_app.py        # Celery config
│   ├── tasks.py             # background tasks
│   └── requirements.txt
├── worker/
│   └── Dockerfile           # (reuses app/ code, different CMD)
├── nginx/
│   └── nginx.conf
├── k8s/
│   ├── config.yaml
│   ├── api-deployment.yaml
│   └── worker-deployment.yaml
├── Dockerfile
└── docker-compose.yml
```

## Build order (do this yourself, using Modules 01-11 as reference — don't just copy)

1. Copy `database.py` and `models.py` patterns from Module 04, add an `Order` model with a `version`
   column for optimistic locking (Module 04 Step 6).
2. Write `main.py` combining:
   - Async endpoints for browsing products (Module 02) with cache-aside + stampede protection (Module 05)
   - A `POST /orders` endpoint using optimistic locking against product stock (Module 04 Step 6)
   - JWT auth on order placement, API-key or JWT-based rate limiting (Module 07)
   - The structured logging middleware and `/metrics` endpoint (Module 11)
3. Write `celery_app.py` + `tasks.py`: a `generate_order_report` task (Module 06)
4. Write the multi-stage `Dockerfile` (Module 08) and `docker-compose.yml` wiring api + worker + db +
   redis + nginx together (Modules 08-09)
5. Run it all locally with `docker compose up --scale api=3 --scale worker=2 -d`
6. Translate the working `docker-compose.yml` into Kubernetes manifests (Module 10) — Deployments,
   Services, ConfigMap, readiness/liveness probes, HPA
7. Load test the whole thing with Locust and watch Grafana dashboards react (Module 11)

## Capstone acceptance checklist

Work through this list and check off each item by actually demonstrating it (screenshot, terminal output,
or a short note of what you observed) — this is your evidence of mastery, not just code that exists:

- [ ] `GET /products/{id}` responds from cache on the second call (verify via a `_source` field or timing)
- [ ] 20 concurrent requests for an uncached product don't cause a cache stampede (Module 05 Step 5 test)
- [ ] Two simultaneous `POST /orders` for the last unit of stock: exactly one succeeds, one gets `409`
- [ ] `POST /orders` requires a valid JWT; missing/invalid token returns `401`
- [ ] Hitting any endpoint >N times/minute as one client returns `429`, and the limit is shared correctly
      across all 3 API replicas (prove it's not `N × 3`)
- [ ] `docker compose up --scale api=3` + NGINX distributes `/whoami`-style requests across replicas
- [ ] Killing one API container mid-load doesn't interrupt the client-visible request stream
- [ ] `POST /reports` returns instantly; polling `GET /reports/{task_id}` shows state transition to `SUCCESS`
- [ ] Kubernetes: deleting a pod causes a replacement to appear automatically
- [ ] Kubernetes: HPA scales replicas up under CPU load and back down after
- [ ] Every request's log line includes a `request_id`, and `/metrics` shows request counts/latency

## Stretch goals (optional, for going further)

- Add OpenTelemetry distributed tracing across API → Celery worker → DB call
- Add a `/products` full-text search using Postgres `tsvector` or an external search index, and cache
  the results
- Swap the Celery broker from Redis to RabbitMQ and compare delivery guarantees
- Add a CI pipeline (GitHub Actions) that builds the Docker image and runs a smoke test on every push
- Add blue/green or canary deployment to the Kubernetes rollout instead of the default rolling update

## Final reflection questions

1. Walk through what happens, component by component, when 500 users simultaneously call `GET /products`
   for the same popular item, at the moment your cache has just expired.
2. Walk through what happens when 500 users simultaneously try to buy the last 10 units of a product.
3. If your service is slow under load, what's your order of investigation, and which module's tooling
   do you reach for at each step? (Hint: metrics/logs first to locate the bottleneck, then the relevant
   concurrency/caching/pooling concept to fix it.)
4. Which of these components would you scale up first if load doubled: API replicas, Celery workers, or
   the database? What would tell you which one is actually the bottleneck?
