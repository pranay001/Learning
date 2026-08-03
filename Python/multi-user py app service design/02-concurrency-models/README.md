# Module 02 — Concurrency Models: How Python Serves Many Users at Once

## Concept

This is the single most important module for your requirement ("multiple users accessing in parallel").
There are **three different mechanisms** in Python, and they solve **different problems**. Confusing them
is the #1 mistake people make when designing concurrent services.

### The GIL (Global Interpreter Lock)

Standard CPython has a lock that ensures only **one thread executes Python bytecode at a time**, even on a
multi-core machine. This means:

- Threads do NOT give you true parallelism for CPU-bound Python code.
- Threads (and async) DO give you concurrency for I/O-bound work, because while one task is *waiting*
  (network, disk, DB), the GIL is released and another task can run.

### Three concurrency mechanisms compared

| Mechanism | Good for | Why |
|-----------|----------|-----|
| **`asyncio` / `async-await`** | I/O-bound (DB calls, HTTP calls, file I/O) — many concurrent waits | Single thread cooperatively switches between tasks whenever one is `await`-ing something. Extremely lightweight — can handle 10,000s of concurrent connections. |
| **Threading (`concurrent.futures.ThreadPoolExecutor`)** | I/O-bound work in libraries that aren't async-native | GIL is released during blocking I/O calls (e.g. `requests`, file reads), so threads can overlap waiting time. Not useful for CPU-bound work. |
| **Multiprocessing (`concurrent.futures.ProcessPoolExecutor`)** | CPU-bound work (image processing, ML inference, heavy computation) | Each process has its own Python interpreter and GIL, so they truly run in parallel across CPU cores. Higher memory overhead, and data must be pickled between processes. |

**Rule of thumb:**
- Waiting on a database/API/network? → `async` (or threads if the library is blocking).
- Crunching numbers / processing data / running an ML model? → multiprocessing (Module 03 covers running
  this via a proper worker pool / task queue rather than inline).

## Hands-On Lab

### Step 1 — Prove the GIL problem with pure Python threads

Create `gil_demo.py`:

```python
import threading
import time

def cpu_bound_work(n):
    total = 0
    for i in range(n):
        total += i
    return total

def run_sequential():
    start = time.perf_counter()
    cpu_bound_work(100_000_000)
    cpu_bound_work(100_000_000)
    print(f"Sequential: {time.perf_counter() - start:.2f}s")

def run_threaded():
    start = time.perf_counter()
    t1 = threading.Thread(target=cpu_bound_work, args=(100_000_000,))
    t2 = threading.Thread(target=cpu_bound_work, args=(100_000_000,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    print(f"Threaded:   {time.perf_counter() - start:.2f}s")

if __name__ == "__main__":
    run_sequential()
    run_threaded()
```

Run it: `python gil_demo.py`

**Expected result:** threaded is NOT meaningfully faster than sequential — often slightly slower due to
thread-switching overhead. This proves threads don't parallelize CPU work in Python.

### Step 2 — Prove multiprocessing DOES parallelize CPU work

Create `multiprocess_demo.py`:

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_bound_work(n):
    total = 0
    for i in range(n):
        total += i
    return total

if __name__ == "__main__":
    start = time.perf_counter()
    cpu_bound_work(100_000_000)
    cpu_bound_work(100_000_000)
    print(f"Sequential:      {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(cpu_bound_work, 100_000_000) for _ in range(2)]
        results = [f.result() for f in futures]
    print(f"Multiprocessing: {time.perf_counter() - start:.2f}s")
```

Run it. On a multi-core machine, you should see roughly a 2x speedup (minus process-spawn overhead).

### Step 3 — Prove async DOES help with I/O-bound work

Create `async_demo.py`:

```python
import asyncio
import time

async def fake_io_call(name, delay):
    print(f"{name}: starting I/O wait")
    await asyncio.sleep(delay)   # simulates waiting on network/DB — non-blocking
    print(f"{name}: done")
    return f"{name}-result"

async def run_sequential():
    start = time.perf_counter()
    await fake_io_call("A", 2)
    await fake_io_call("B", 2)
    print(f"Sequential await: {time.perf_counter() - start:.2f}s")

async def run_concurrent():
    start = time.perf_counter()
    await asyncio.gather(
        fake_io_call("A", 2),
        fake_io_call("B", 2),
    )
    print(f"Concurrent gather: {time.perf_counter() - start:.2f}s")

async def main():
    await run_sequential()   # ~4 seconds
    await run_concurrent()   # ~2 seconds — both waits overlap

asyncio.run(main())
```

Run it. You'll see the sequential version takes ~4s and the concurrent version ~2s, because
`asyncio.sleep` yields control back to the event loop instead of blocking it.

### Step 4 — Apply this to FastAPI: async endpoints done correctly

Create `main.py`:

```python
from fastapi import FastAPI
import asyncio
import httpx

app = FastAPI()

@app.get("/good-async")
async def good_async_endpoint():
    # Non-blocking sleep — event loop is free to handle other requests during this wait
    await asyncio.sleep(2)
    return {"pattern": "correct", "note": "used await, event loop stayed free"}

@app.get("/bad-async")
async def bad_async_endpoint():
    import time
    # WRONG: blocking call inside an async def — this DOES block the whole event loop
    time.sleep(2)
    return {"pattern": "wrong", "note": "blocked the entire event loop for 2s"}

@app.get("/fetch-external")
async def fetch_external():
    # Real-world example: calling another API without blocking other users' requests
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://httpbin.org/delay/1")
    return {"status": resp.status_code}
```

```bash
uv pip install httpx
uvicorn main:app --reload
```

**Lab exercise:** Open two browser tabs. Hit `/bad-async` in tab 1, then immediately hit `/` (root, add a
trivial root route) in tab 2. Notice tab 2 waits. Now repeat with `/good-async` instead — tab 2 responds
immediately. This is the single most common bug in real FastAPI services: calling a blocking library
(e.g. the sync `requests` library, or a non-async DB driver) inside an `async def` route.

## Checkpoint Questions

1. If your endpoint calls a slow external weather API, should you use asyncio or multiprocessing? Why?
2. If your endpoint resizes a 50MB image, should you use asyncio or multiprocessing? Why?
3. Why did `time.sleep(2)` inside an `async def` block *all* users, while `asyncio.sleep(2)` didn't?
4. Is it ever wrong to make every endpoint `async def`? (Hint: what happens if you put blocking code in one?)

## What's Next

Module 03 shows how to scale beyond one process using multiple **worker processes**, so you use all your
CPU cores for handling concurrent requests, not just one.
