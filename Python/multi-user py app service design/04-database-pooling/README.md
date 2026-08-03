# Module 04 — Database Access Under Parallel Load: Connection Pooling

## Concept

If every incoming request opens a brand-new database connection, you'll quickly exhaust the database's
connection limit once you have multiple workers × multiple concurrent requests each. A **connection pool**
maintains a set of already-open connections that requests borrow and return, instead of paying the cost
of a fresh TCP + auth handshake every time.

| Term | Meaning |
|------|---------|
| **Connection pool** | A cache of open DB connections reused across requests |
| **Pool size** | Max connections kept open per process (careful: with N workers, total = N × pool_size) |
| **Overflow** | Extra connections allowed temporarily beyond pool size, under burst load |
| **Async driver** | A DB driver that doesn't block the event loop while waiting on the database (e.g. `asyncpg` for Postgres) |
| **Optimistic locking** | Preventing lost updates by checking a version/timestamp column before committing a write |
| **N+1 problem** | A classic bug where a loop triggers one query per item instead of one batched query — devastating under parallel load |

## Hands-On Lab

### Step 1 — Run Postgres locally with Docker

```bash
docker run --name learning-postgres \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=appdb \
  -p 5432:5432 \
  -d postgres:16
```

Verify it's running: `docker ps`

### Step 2 — Install dependencies

```bash
uv pip install fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg
```

### Step 3 — Define models and an async engine with explicit pooling

Create `database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://appuser:apppass@localhost:5432/appdb"

# pool_size: connections kept open per process
# max_overflow: extra connections allowed temporarily under burst load
# pool_timeout: how long a request waits for a free connection before erroring
# pool_recycle: refresh connections periodically (avoids stale/dead connections)
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    """FastAPI dependency: yields a session, always returns it to the pool afterward."""
    async with AsyncSessionLocal() as session:
        yield session
```

Create `models.py`:

```python
from sqlalchemy import Column, Integer, String, Float
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=0)  # for optimistic locking, Step 6
```

### Step 4 — Wire it into FastAPI

Create `main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, get_db
from models import Product

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/products")
async def create_product(name: str, price: float, stock: int, db: AsyncSession = Depends(get_db)):
    product = Product(name=name, price=price, stock=stock)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "name": product.name}

@app.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": product.id, "name": product.name, "price": product.price, "stock": product.stock}

@app.get("/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return [{"id": p.id, "name": p.name, "stock": p.stock} for p in products]
```

Run it: `uvicorn main:app --reload`

Create a product:
```bash
curl -X POST "http://localhost:8000/products?name=Widget&price=9.99&stock=100"
```

### Step 5 — Prove pooling matters: load test and watch connection count

In one terminal, watch active Postgres connections live:

```bash
watch -n 1 "docker exec learning-postgres psql -U appuser -d appdb -c \"SELECT count(*) FROM pg_stat_activity WHERE datname='appdb';\""
```

In another terminal, hammer the list endpoint with Locust (reuse the `locustfile.py` pattern from
Module 03, pointed at `/products`) with 50 concurrent users. Watch the connection count in the first
terminal — it should stay bounded near your `pool_size + max_overflow`, never exploding to match the
50 concurrent users. This is the pool doing its job: requests queue briefly for a connection instead of
each opening a fresh one.

**Experiment:** temporarily set `pool_size=2, max_overflow=0` and rerun the load test. You should see
requests start timing out (`TimeoutError: QueuePool limit... connection timed out`) once concurrent
demand exceeds capacity — this demonstrates why sizing the pool matters and why it must account for
`(number of workers) × (pool_size)` against your database's max connection limit.

### Step 6 — Handling concurrent writes safely: optimistic locking

This simulates two users trying to decrement stock on the same product simultaneously (a classic race
condition under parallel load).

Add to `main.py`:

```python
from sqlalchemy import update

@app.post("/products/{product_id}/purchase")
async def purchase_product(product_id: int, quantity: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product or product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Optimistic lock: only update if version hasn't changed since we read it
    stmt = (
        update(Product)
        .where(Product.id == product_id, Product.version == product.version)
        .values(stock=product.stock - quantity, version=product.version + 1)
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        # Someone else updated it between our read and write — caller should retry
        raise HTTPException(status_code=409, detail="Conflict, please retry")

    return {"status": "purchased", "quantity": quantity}
```

**Lab exercise:** Write a small script using `httpx` (or just two curl commands fired near-simultaneously
with `&`) that sends two purchase requests for the same product at once, each buying half the remaining
stock. Confirm you either get both succeeding cleanly, or one getting a `409 Conflict` — never a
negative stock count.

## Checkpoint Questions

1. If you have 4 Gunicorn workers each with `pool_size=10`, and Postgres's `max_connections=100`, do the numbers work out safely? What would you need to change if not?
2. Why does the pool queue requests instead of just opening unlimited new connections?
3. Why is `expire_on_commit=False` set on the sessionmaker here, and what problem could arise if many concurrent requests share a session incorrectly?
4. Why is optimistic locking (version column) often preferred over a hard row-level `SELECT ... FOR UPDATE` lock for high-concurrency reads?

## What's Next

Not every request needs to hit the database. Module 05 introduces caching with Redis to cut load and
latency dramatically for repeated reads.
