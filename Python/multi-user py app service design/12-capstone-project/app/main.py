import os
import json
import time
import uuid
import logging
import socket
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Request, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from jose import jwt, JWTError
from pythonjsonlogger import jsonlogger
import redis.asyncio as redis
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import asyncio

from database import get_db, init_models
from models import Product, Order
from celery_app import celery_app
from tasks import generate_order_report
from celery.result import AsyncResult

# ---------------------------------------------------------------------------
# Module 11: structured logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("api")
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(duration_ms)s"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Module 05/06/07: Redis (cache + Celery broker + rate-limit storage)
# ---------------------------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
CACHE_TTL_SECONDS = 30

# ---------------------------------------------------------------------------
# Module 07: auth
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
FAKE_USERS = {"alice": "password123", "bob": "hunter2"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# ---------------------------------------------------------------------------
# Module 07: rate limiting (Redis-backed, shared across all workers/replicas)
# ---------------------------------------------------------------------------
def get_client_identity(request: Request):
    api_key = request.headers.get("X-API-Key")
    return api_key or (request.client.host if request.client else "unknown")

limiter = Limiter(key_func=get_client_identity, storage_uri=REDIS_URL)

app = FastAPI(title="Capstone: Product Catalog & Order API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Module 11: Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)


# ---------------------------------------------------------------------------
# Module 11: request-id + timing middleware
# ---------------------------------------------------------------------------
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


@app.on_event("startup")
async def startup():
    await init_models()


@app.get("/health")
def health_check():
    return {"status": "ok", "hostname": socket.gethostname()}


@app.get("/whoami")
def whoami():
    return {"hostname": socket.gethostname(), "pid": os.getpid()}


# ---------------------------------------------------------------------------
# Module 07: auth endpoints
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if FAKE_USERS.get(form_data.username) != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(
        {"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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


# ---------------------------------------------------------------------------
# Module 04 + 05: products — pooled DB access with cache-aside + stampede lock
# ---------------------------------------------------------------------------
@app.post("/products")
async def create_product(name: str, price: float, stock: int, db: AsyncSession = Depends(get_db)):
    product = Product(name=name, price=price, stock=stock)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "name": product.name}


@app.get("/products")
@limiter.limit("30/minute")
async def list_products(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return [{"id": p.id, "name": p.name, "stock": p.stock, "price": p.price} for p in products]


@app.get("/products/{product_id}")
@limiter.limit("30/minute")
async def get_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"product:{product_id}"
    lock_key = f"lock:{cache_key}"

    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_source"] = "cache"
        return data

    got_lock = await redis_client.set(lock_key, "1", nx=True, ex=5)
    if not got_lock:
        for _ in range(10):
            await asyncio.sleep(0.2)
            cached = await redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                data["_source"] = "cache (waited)"
                return data

    try:
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


# ---------------------------------------------------------------------------
# Module 04: orders — optimistic locking to prevent overselling under
# concurrent purchases; requires auth (Module 07)
# ---------------------------------------------------------------------------
@app.post("/orders")
@limiter.limit("10/minute")
async def place_order(
    request: Request,
    product_id: int,
    quantity: int,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product or product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    stmt = (
        update(Product)
        .where(Product.id == product_id, Product.version == product.version)
        .values(stock=product.stock - quantity, version=product.version + 1)
    )
    result = await db.execute(stmt)

    if result.rowcount == 0:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Conflict, please retry")

    order = Order(product_id=product_id, username=username, quantity=quantity)
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Invalidate the cached product since stock changed (Module 05)
    await redis_client.delete(f"product:{product_id}")

    return {"order_id": order.id, "status": "placed", "quantity": quantity}


# ---------------------------------------------------------------------------
# Module 06: background report generation, decoupled from the API's response time
# ---------------------------------------------------------------------------
@app.post("/reports")
def request_report(username: str = Depends(get_current_user)):
    task = generate_order_report.delay(username)
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
