# Module 05 — Caching with Redis: Cutting Repeated Work Under Parallel Load

## Concept

Many parallel users often ask for the *same* data (a product listing, a popular article, a leaderboard).
Recomputing/refetching it every time wastes DB load and CPU. **Redis** is an in-memory key-value store
that's fast (sub-millisecond) and shared across all your worker processes/instances — solving the
statelessness problem from Module 03 (workers can't share in-memory Python variables, but they can all
read/write the same Redis instance).

| Term | Meaning |
|------|---------|
| **Cache hit / miss** | Whether requested data was found in cache (hit) or had to be computed/fetched (miss) |
| **TTL (Time To Live)** | How long a cached value stays valid before auto-expiring |
| **Cache invalidation** | Explicitly removing/updating a cached value when underlying data changes |
| **Cache stampede** | Many concurrent requests all miss the cache at once and hammer the DB simultaneously |
| **Write-through / cache-aside** | Common patterns for keeping cache and DB in sync |

## Hands-On Lab

### Step 1 — Run Redis locally

```bash
docker run --name learning-redis -p 6379:6379 -d redis:7
```

Verify: `docker exec -it learning-redis redis-cli ping` → should return `PONG`

### Step 2 — Install the async Redis client

```bash
uv pip install redis
```

### Step 3 — Cache-aside pattern in FastAPI

Create `main.py` (building on Module 04's `Product` model — reuse `database.py`/`models.py`, or adapt to
your own app):

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis
import json
import time

from database import get_db
from models import Product

app = FastAPI()
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

CACHE_TTL_SECONDS = 30

@app.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"product:{product_id}"

    # 1. Try cache first
    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_source"] = "cache"
        return data

    # 2. Cache miss — go to the database
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")

    data = {"id": product.id, "name": product.name, "price": product.price, "stock": product.stock}

    # 3. Populate cache for next time
    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL_SECONDS)

    data["_source"] = "database"
    return data

@app.put("/products/{product_id}/invalidate")
async def invalidate_product_cache(product_id: int):
    # Call this whenever the product is updated elsewhere, so stale data isn't served
    await redis_client.delete(f"product:{product_id}")
    return {"status": "invalidated"}
```

### Step 4 — Measure the speed difference

```bash
# First call — cache miss, hits DB
time curl -s http://localhost:8000/products/1 > /dev/null

# Second call within 30s — cache hit
time curl -s http://localhost:8000/products/1 > /dev/null
```

Compare the `real` time between the two — the cached call should be noticeably faster, especially once
your "database" simulates realistic latency.

### Step 5 — Simulate and fix a cache stampede

First, reproduce the problem. Add an artificial DB delay to `get_product`'s miss path (simulate a slow
query):

```python
import asyncio
# inside the cache-miss branch, before the DB query:
await asyncio.sleep(1)
```

Clear the cache (`redis-cli FLUSHALL` or wait for TTL to expire), then fire 20 concurrent requests for
the same product:

```bash
for i in $(seq 1 20); do curl -s http://localhost:8000/products/1 & done; wait
```

Without protection, all 20 requests miss the cache simultaneously and all 20 hit the "slow" database path
— defeating the purpose of caching. Fix this with a **distributed lock** so only one request repopulates
the cache while others wait briefly and then read the fresh value:

```python
@app.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"product:{product_id}"
    lock_key = f"lock:{cache_key}"

    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_source"] = "cache"
        return data

    # Try to acquire a short-lived lock; only the winner queries the DB
    got_lock = await redis_client.set(lock_key, "1", nx=True, ex=5)
    if not got_lock:
        # Someone else is already repopulating the cache — wait briefly and retry from cache
        for _ in range(10):
            await asyncio.sleep(0.2)
            cached = await redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                data["_source"] = "cache (waited)"
                return data
        # fall through to querying ourselves if the wait timed out

    try:
        await asyncio.sleep(1)  # simulated slow query
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Not found")
        data = {"id": product.id, "name": product.name, "price": product.price, "stock": product.stock}
        await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL_SECONDS)
        data["_source"] = "database"
        return data
    finally:
        if got_lock:
            await redis_client.delete(lock_key)
```

Rerun the 20-concurrent-request test and observe (via added logging or a counter) that the DB path only
executes once or a handful of times, not 20.

## Checkpoint Questions

1. Why must invalidation happen explicitly on writes, instead of relying only on TTL, for data that changes often?
2. What could go wrong if two workers both think they hold the "lock" at the same time? (Hint: why does `nx=True` matter?)
3. When is caching a bad idea (what kind of data should you probably NOT cache)?

## What's Next

Some work is too slow or CPU-heavy to do inline in a request at all — even with caching. Module 06 covers
offloading that work to background workers with Celery.
