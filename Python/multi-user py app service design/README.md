# Building a Parallel, Multi-User Python API Service — Hands-On Learning Path

This is a project-based curriculum. Every module has: **concept explanation → hands-on lab → checkpoint questions**.
By the end, you will have built (and understand deeply) a production-shaped service where many users can call
your API in parallel, safely and efficiently.

## How to use this material

1. Work through modules **in order** — each builds on the previous one's code.
2. Actually type/run every command. Don't just read — the labs are where the learning happens.
3. Each module folder is self-contained with its own code, but Module 12 (Capstone) stitches everything
   into one real deployable service.
4. Budget roughly: Modules 1-3 (~3-4 hrs), Modules 4-7 (~4-5 hrs), Modules 8-11 (~4-5 hrs), Capstone (~3-4 hrs).

## Prerequisites

- Python 3.11+ installed (`python3 --version`)
- [uv](https://docs.astral.sh/uv/) installed — this is the tool we use for **all** package/venv management
  throughout this material instead of raw `pip` (`curl -LsSf https://astral.sh/uv/install.sh | sh`, or
  `pipx install uv` / `brew install uv`). Verify with `uv --version`.
- Docker Desktop installed and running (`docker --version`)
- Basic command-line comfort (cd, mkdir, running scripts)
- A code editor (VS Code recommended)
- Basic Python knowledge (functions, classes, decorators) — you do NOT need prior async/API experience

## A note on tooling: why `uv` instead of plain `pip`

Every module in this material uses **`uv`** for creating virtual environments and installing packages,
instead of `python -m venv` + `pip install`. Reasons this matters for the kind of service you're building:

- **Speed**: `uv` resolves and installs packages dramatically faster than pip (written in Rust), which
  matters a lot when you're rebuilding Docker images repeatedly across Modules 08-10.
- **Reproducibility**: `uv` produces a lockfile (`uv.lock`) capturing exact resolved versions, so "works on
  my machine" problems (the exact thing Module 08 is about eliminating) don't creep back in through
  dependency drift.
- **One tool for venvs + installs**: `uv venv` and `uv pip install` replace `python -m venv` +
  `pip install`, so there's one consistent command pattern across every module.

Anywhere you see `pip install X` in older Python tutorials elsewhere, the equivalent here is
`uv pip install X` (inside a `uv venv`-created environment), or `uv add X` if you've initialized the
folder as a `uv` project with `uv init`. Both approaches are used in this material — module labs use the
lighter-weight `uv venv` + `uv pip install` flow, while the Capstone's Dockerfiles show the project-style
`uv sync` flow.

## Curriculum Map

| # | Module | Core Question It Answers |
|---|--------|---------------------------|
| 01 | FastAPI Basics | How do I expose Python logic as an HTTP API? |
| 02 | Concurrency Models | Why/how can one process serve many requests at once? |
| 03 | Worker Processes | How do I use multiple CPU cores, not just one process? |
| 04 | Database Pooling | How do many parallel requests share a database safely? |
| 05 | Caching with Redis | How do I avoid redoing the same expensive work per request? |
| 06 | Celery Background Tasks | How do I handle slow/CPU-heavy work without blocking the API? |
| 07 | Auth & Rate Limiting | How do I identify users and stop abuse? |
| 08 | Docker | How do I package the app so it runs identically everywhere? |
| 09 | Load Balancing (NGINX) | How do I run multiple copies and spread traffic across them? |
| 10 | Kubernetes | How do I auto-scale and self-heal in production? |
| 11 | Observability | How do I know what's happening across thousands of parallel requests? |
| 12 | Capstone Project | Put it all together into one working, scalable service |

## Architecture you'll end up with

```
                     ┌─────────────┐
   Many Users  ───▶  │ NGINX / LB  │
   (parallel)        └──────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐   ┌──────────┐
        │ FastAPI  │  │ FastAPI  │   │ FastAPI  │   (N replicas, stateless)
        │ instance │  │ instance │   │ instance │
        └────┬─────┘  └────┬─────┘   └────┬─────┘
             │             │              │
      ┌──────┴─────────────┴──────────────┴──────┐
      ▼                    ▼                     ▼
 ┌─────────┐         ┌───────────┐         ┌────────────┐
 │  Redis  │         │ Postgres  │         │   Celery    │
 │ (cache) │         │ (pooled)  │         │  workers    │
 └─────────┘         └───────────┘         └────────────┘
```

Start with `01-fastapi-basics/README.md`.
