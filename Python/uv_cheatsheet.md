# ⚡ UV for Python – Complete Step-by-Step Guide (Beginner → Advanced)

**UV** is an extremely fast Python package and project manager, written in Rust by [Astral](https://astral.sh/) (the makers of Ruff). It replaces `pip`, `pip-tools`, `virtualenv`, `pyenv`, `poetry`, and `pipx` — all with a single tool that is **10–100× faster**.

This guide takes you from zero knowledge to advanced usage. Read it top-to-bottom and you'll be able to manage real Python projects with UV.

---

## 📑 Table of Contents

1. [Why UV?](#-1-why-uv)
2. [Installing UV](#-2-installing-uv)
3. [Core Mental Model](#-3-core-mental-model)
4. [Managing Python Versions](#-4-managing-python-versions)
5. [Your First Project](#-5-your-first-project)
6. [Adding & Removing Dependencies](#-6-adding--removing-dependencies)
7. [Running Code](#-7-running-code)
8. [The Lockfile & Reproducibility](#-8-the-lockfile--reproducibility)
9. [Understanding pyproject.toml](#-9-understanding-pyprojecttoml)
10. [Dependency Groups (dev, test, etc.)](#-10-dependency-groups)
11. [Version Constraints Explained](#-11-version-constraints-explained)
12. [Working With Virtual Environments](#-12-working-with-virtual-environments)
13. [Using UV as a pip Replacement](#-13-using-uv-as-a-pip-replacement)
14. [Tools: Replacing pipx](#-14-tools-replacing-pipx)
15. [Single-File Scripts With Inline Dependencies](#-15-single-file-scripts-with-inline-dependencies)
16. [Building & Publishing Packages](#-16-building--publishing-packages)
17. [Workspaces (Monorepos)](#-17-workspaces-monorepos)
18. [UV in Docker / CI](#-18-uv-in-docker--ci)
19. [Migrating From pip / Poetry / Pipenv](#-19-migrating-from-other-tools)
20. [Command Cheat Sheet](#-20-command-cheat-sheet)
21. [Troubleshooting](#-21-troubleshooting)
22. [Key Files & Folders](#-22-key-files--folders)

---

## 🚀 1. Why UV?

Traditionally a Python project needed a stack of separate tools:

| Job                          | Old tool(s)            | UV replaces it |
| ---------------------------- | ---------------------- | -------------- |
| Install packages             | `pip`                  | ✅              |
| Create virtual environments  | `venv`, `virtualenv`   | ✅              |
| Install multiple Python versions | `pyenv`            | ✅              |
| Lock dependencies            | `pip-tools`            | ✅              |
| Project & dependency manager | `poetry`, `pipenv`     | ✅              |
| Install CLI tools globally   | `pipx`                 | ✅              |

**Key advantages:**

- **Speed** — written in Rust, with a global cache and parallel downloads. Installs that took minutes take seconds.
- **One tool** — no more juggling pyenv + venv + pip + pip-tools.
- **Reproducible** — a `uv.lock` file pins every package (direct and transitive) with hashes.
- **Standards-based** — uses the standard `pyproject.toml`, so it interoperates with the wider Python ecosystem.

---

## 📦 2. Installing UV

UV is a **standalone binary** — it does *not* need Python to be installed first (it can install Python for you).

### 🪟 Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 🍎 macOS / 🐧 Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Alternative install methods

```bash
# Using pipx
pipx install uv

# Using pip
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using winget (Windows)
winget install --id=astral-sh.uv
```

### 🔍 Verify the installation

```bash
uv --version
```

> 💡 After installing, restart your terminal so the updated `PATH` takes effect.

### 🔄 Keeping UV updated

If you installed via the standalone installer:

```bash
uv self update
```

---

## 🧠 3. Core Mental Model

Before commands, understand the two ways people use UV. This is the single most important section for a beginner.

### A) Project workflow (recommended)

You let UV manage everything through a `pyproject.toml` and `uv.lock`. You almost never activate a venv manually — instead you prefix commands with `uv run`.

```
my_project/
├── pyproject.toml   ← what you depend on (you + UV edit this)
├── uv.lock          ← exact resolved versions (UV manages, you commit)
├── .venv/           ← the virtual environment (UV manages, you DON'T commit)
└── main.py          ← your code
```

The golden rule: **`uv add` to install, `uv run` to execute.** UV automatically keeps `.venv` and `uv.lock` in sync every time you run a command.

### B) pip-compatible workflow

If you just want a faster `pip`, UV offers `uv pip ...` and `uv venv` that mirror the classic commands. Covered in [section 13](#-13-using-uv-as-a-pip-replacement).

> 👉 New users should learn the **project workflow** (A). The rest of this guide focuses there.

---

## 🐍 4. Managing Python Versions

UV can download and manage Python interpreters for you — no `pyenv` needed.

```bash
# List Python versions available to install
uv python list

# Install specific versions
uv python install 3.12
uv python install 3.11 3.12 3.13   # multiple at once

# Show installed versions
uv python list --only-installed

# Pin a Python version for the current project
uv python pin 3.12
```

`uv python pin 3.12` writes a `.python-version` file. Any UV command in that folder will then use Python 3.12, installing it automatically if missing.

> 💡 You don't *have* to pre-install Python. When you create a project or run a script, UV downloads the required interpreter on demand.

---

## 📁 5. Your First Project

### Create a new project

```bash
uv init my_project
cd my_project
```

This scaffolds:

```
my_project/
├── .git/             # initialized git repo
├── .gitignore        # pre-filled (ignores .venv, etc.)
├── .python-version   # pinned Python version
├── README.md
├── main.py           # a hello-world entry point
└── pyproject.toml    # project metadata + dependencies
```

### Useful `init` variants

```bash
uv init                       # initialize in the CURRENT directory
uv init --app my_app          # application layout (default)
uv init --lib my_lib          # library layout with src/ (for packages you'll publish)
uv init --package my_pkg      # packaged app with a build system
uv init --python 3.11 proj    # choose the Python version up front
```

**App vs. Lib layout:**
- `--app` → flat layout, for scripts/services you run but don't publish.
- `--lib` → `src/my_lib/` layout with a build backend, for packages you'll publish to PyPI.

### Run it

```bash
uv run main.py
```

The first `uv run` creates the `.venv`, installs Python if needed, and resolves dependencies — all automatically.

---

## 📚 6. Adding & Removing Dependencies

This is the day-to-day core of UV.

### Add a dependency

```bash
uv add requests
```

This does several things at once:
1. Adds `requests` to `pyproject.toml`.
2. Resolves the full dependency tree.
3. Updates `uv.lock`.
4. Installs it into `.venv`.

### Add a specific version

```bash
uv add "django>=5.0,<6.0"
uv add "numpy==1.26.4"
uv add "fastapi~=0.110"
```

### Add multiple packages

```bash
uv add requests rich pydantic
```

### Add a development dependency

```bash
uv add --dev pytest ruff mypy
```

Dev dependencies are needed for development (testing, linting) but not shipped to end users.

### Add from other sources

```bash
# From a Git repository
uv add "git+https://github.com/psf/requests"

# A specific branch / tag / commit
uv add "git+https://github.com/psf/requests@main"

# From a local path (editable)
uv add --editable ../my-other-package

# With optional "extras"
uv add "uvicorn[standard]"
```

### Remove a dependency

```bash
uv remove requests
uv remove --dev pytest
```

### Upgrade dependencies

```bash
uv lock --upgrade                 # upgrade everything within constraints
uv lock --upgrade-package requests  # upgrade just one package
uv add "requests --upgrade"
```

---

## ▶️ 7. Running Code

With UV you generally **don't activate the venv** — you let `uv run` handle it.

```bash
uv run main.py                 # run a script
uv run python -m http.server   # run a module
uv run pytest                  # run an installed tool
uv run python                  # open a REPL with project deps available
```

Before each run, UV checks that `.venv` matches `uv.lock` and syncs if needed. This means your environment is **always correct** — no "works on my machine" drift.

### Pass arguments

```bash
uv run python main.py --verbose --count 5
```

### Run a one-off command with an extra package (without adding it)

```bash
uv run --with rich python -c "import rich; rich.print('[bold green]hi[/]')"
```

`--with` adds the package just for that single invocation; it isn't saved to `pyproject.toml`.

---

## 🔐 8. The Lockfile & Reproducibility

`uv.lock` is UV's most important feature for teams.

- It records the **exact version + hash** of every package, direct *and* transitive.
- It is **cross-platform** (resolves for Linux/macOS/Windows in one file).
- It guarantees that everyone on the team — and your CI/production — gets *identical* dependencies.
- ✅ **Commit `uv.lock` to version control.**

### Sync the environment from the lockfile

```bash
uv sync
```

`uv sync` makes `.venv` exactly match `uv.lock`. This is the command a new teammate runs after cloning the repo:

```bash
git clone <repo>
cd <repo>
uv sync          # creates .venv with the exact locked versions
uv run main.py
```

### Regenerate the lockfile

```bash
uv lock           # re-resolve and update uv.lock
uv lock --check    # verify the lock is up to date (great for CI)
```

### Sync variations

```bash
uv sync --frozen      # install from lock WITHOUT re-locking (fast, deterministic)
uv sync --no-dev      # production install — skip dev dependencies
uv sync --all-extras  # include all optional extras
```

> 💡 **`uv add`/`uv run`/`uv sync` keep the lock in sync automatically.** You rarely call `uv lock` by hand except to upgrade or in CI checks.

---

## 📜 9. Understanding pyproject.toml

`pyproject.toml` is the single source of truth for your project. A typical UV-managed file:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A demo project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "rich>=13.0.0",
]

# Optional extras users can opt into: pip install my-project[web]
[project.optional-dependencies]
web = ["fastapi>=0.110", "uvicorn>=0.29"]

# Dev-only dependency groups (UV-aware, NOT shipped to users)
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
]

# A console command this package installs
[project.scripts]
my-cli = "my_project.cli:main"

# Build backend — only needed for packages you publish
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Key fields:

| Field                          | Meaning                                             |
| ------------------------------ | --------------------------------------------------- |
| `requires-python`              | Minimum/allowed Python versions                     |
| `dependencies`                 | Runtime dependencies (shipped to users)             |
| `optional-dependencies`        | Opt-in extras (`pip install pkg[extra]`)            |
| `dependency-groups`            | Local dev groups (dev/test/docs), not shipped       |
| `[project.scripts]`            | CLI entry points created on install                 |
| `[build-system]`               | How the package is built (only for libraries)       |

---

## 🗂️ 10. Dependency Groups

Groups let you organize dev-time dependencies separately from what ships to users.

```bash
# Add to the default "dev" group
uv add --dev pytest

# Add to a custom group
uv add --group docs mkdocs mkdocs-material
uv add --group lint ruff mypy
```

This produces:

```toml
[dependency-groups]
dev = ["pytest>=8.0"]
docs = ["mkdocs>=1.6", "mkdocs-material>=9.5"]
lint = ["ruff>=0.4", "mypy>=1.10"]
```

### Controlling what gets installed

```bash
uv sync                      # default: includes the "dev" group
uv sync --no-dev             # production: runtime deps only
uv sync --group docs         # include the docs group
uv sync --only-group lint    # ONLY the lint group
uv sync --all-groups         # everything
```

> 💡 The `dev` group is special: it's installed by default with `uv sync`. Use `--no-dev` for production builds.

---

## 🎯 11. Version Constraints Explained

Understanding version specifiers prevents surprise breakages.

### `>=` (minimum version)

```
requests>=2.31.0   →  2.31.0 or anything newer
```

### `~=` (compatible release — "tilde-equals")

```
numpy~=1.26.0   →  >=1.26.0, <1.27.0   (patch updates only)
numpy~=1.26     →  >=1.26,   <2.0      (minor updates allowed)
```

### `==` (exact pin)

```
django==5.0.4   →  exactly 5.0.4
```

### Ranges

```
"django>=5.0,<6.0"   →  any 5.x but not 6.0
```

### `*` (any version)

```
requests==2.*   →  any 2.x release
```

> 💡 **Best practice:** use `>=` lower bounds in `pyproject.toml` (flexible), and rely on `uv.lock` to pin the *exact* versions for reproducibility. Don't over-constrain — let the lockfile do the pinning.

---

## 📂 12. Working With Virtual Environments

UV creates `.venv` automatically, but you can manage it directly.

### Create a venv manually

```bash
uv venv                      # creates .venv with the default Python
uv venv --python 3.12        # specify a version
uv venv myenv                # custom name/location
```

### Activate it (optional)

You usually **don't need to** — prefer `uv run`. But if you want to:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### Where things live

- UV stores a **global cache** of downloaded packages (shared across all projects → huge speedup and disk savings).
- Each project's `.venv` uses hardlinks/copies from that cache.

```bash
uv cache clean      # clear the global cache
uv cache dir         # show cache location
```

---

## 🔧 13. Using UV as a pip Replacement

If you're not ready for the full project workflow, UV provides drop-in pip commands. These are **lower-level** — they do *not* touch `pyproject.toml` or `uv.lock`.

```bash
uv venv                              # create a virtual environment
uv pip install requests              # install (like pip install)
uv pip install -r requirements.txt   # install from requirements file
uv pip uninstall requests            # uninstall
uv pip list                          # list installed packages
uv pip freeze                        # output installed versions
uv pip show requests                 # package details
```

### Compiling requirements (pip-tools replacement)

```bash
# Compile requirements.in → pinned requirements.txt
uv pip compile requirements.in -o requirements.txt

# Sync the env to exactly match a requirements file
uv pip sync requirements.txt
```

> ⚠️ **Don't mix workflows.** Use either the project workflow (`uv add`/`uv sync`) *or* the pip workflow (`uv pip install`) for a given project — not both.

---

## 🛠️ 14. Tools: Replacing pipx

UV can install and run command-line tools globally, isolated from your projects.

### Run a tool once (ephemeral)

```bash
uvx ruff check .
uvx black .
uvx cowsay -t "Hello"
```

`uvx` is shorthand for `uv tool run`. It downloads the tool into a temporary cached environment and runs it — nothing is permanently installed.

### Install a tool permanently

```bash
uv tool install ruff
uv tool install "ansible-core"

ruff --version          # now available on your PATH
```

### Manage installed tools

```bash
uv tool list             # list installed tools
uv tool upgrade ruff     # upgrade one
uv tool upgrade --all    # upgrade all
uv tool uninstall ruff   # remove
```

> 💡 Use `uvx <tool>` for one-off runs; use `uv tool install` for tools you use constantly (like `ruff`).

---

## 📄 15. Single-File Scripts With Inline Dependencies

One of UV's best features: run a standalone `.py` file with its dependencies declared **inside the file** — no project, no manual venv. This uses the [PEP 723](https://peps.python.org/pep-0723/) inline metadata standard.

### Add inline metadata to a script

```bash
uv add --script demo.py requests rich
```

This injects a special comment block at the top:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "rich",
# ]
# ///

import requests
from rich import print

resp = requests.get("https://api.github.com")
print(f"[bold green]Status:[/] {resp.status_code}")
```

### Run it

```bash
uv run demo.py
```

UV reads the inline block, creates a temporary isolated environment with exactly those packages, and runs the script. Perfect for sharing a single file that "just works" for anyone with UV installed.

---

## 🏗️ 16. Building & Publishing Packages

For libraries you want to share on PyPI.

### Build distributions

```bash
uv build
```

Creates a wheel (`.whl`) and source distribution (`.tar.gz`) in `dist/`.

### Publish to PyPI

```bash
# Provide a token via flag or environment variable
uv publish --token <PYPI_TOKEN>

# Or set it once
export UV_PUBLISH_TOKEN=<PYPI_TOKEN>
uv publish
```

### Publish to a test index first

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

> 💡 To create a publishable library, start with `uv init --lib my_lib` so it has the proper `src/` layout and `[build-system]`.

---

## 🧩 17. Workspaces (Monorepos)

A **workspace** lets multiple related packages share one lockfile and environment — ideal for monorepos.

### Root `pyproject.toml`

```toml
[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/*"]
```

### Structure

```
my-workspace/
├── pyproject.toml          # workspace root
├── uv.lock                 # ONE shared lockfile
└── packages/
    ├── core/
    │   └── pyproject.toml
    └── api/
        └── pyproject.toml  # can depend on "core"
```

### Depend on another workspace member

```bash
# Inside packages/api, depend on the local "core" package
uv add core
```

In `packages/api/pyproject.toml`:

```toml
[tool.uv.sources]
core = { workspace = true }
```

### Run commands against a specific member

```bash
uv run --package api uvicorn api.main:app
uv sync --package core
```

---

## 🐳 18. UV in Docker / CI

UV shines in CI thanks to its speed and reproducibility.

### Minimal Dockerfile

```dockerfile
FROM python:3.12-slim

# Copy the UV binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install deps from the lockfile, no dev deps, frozen for determinism
RUN uv sync --frozen --no-dev

# Now copy the rest of the app
COPY . .

# Run via uv (uses the .venv created above)
CMD ["uv", "run", "main.py"]
```

### Typical GitHub Actions step

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

### Why `--frozen` in CI?

`--frozen` installs *exactly* what's in `uv.lock` and **fails if the lock is out of date**, instead of silently re-resolving. This guarantees CI tests the same versions you locked locally.

> 💡 Add `uv lock --check` as a CI step to fail the build if someone forgot to commit an updated lockfile.

---

## 🔄 19. Migrating From Other Tools

### From pip / requirements.txt

```bash
uv init                                   # create pyproject.toml
uv add -r requirements.txt                # import existing deps
# verify, then delete requirements.txt
```

### From Poetry / Pipenv

UV reads standard `pyproject.toml`. For Poetry projects, the dependencies live under `[tool.poetry.dependencies]`; you'll want them under the standard `[project]` table. Helper tools exist:

```bash
# Community migration helper (run via uvx, no install)
uvx migrate-to-uv
```

Then:

```bash
uv lock      # generate uv.lock
uv sync      # build the environment
```

### Command translation table

| Task                  | pip / venv                          | Poetry                  | UV                      |
| --------------------- | ----------------------------------- | ----------------------- | ----------------------- |
| Create project        | `mkdir` + `python -m venv`          | `poetry new`            | `uv init`               |
| Add dependency        | `pip install x`                     | `poetry add x`          | `uv add x`              |
| Add dev dependency    | `pip install x`                     | `poetry add --dev x`    | `uv add --dev x`        |
| Remove dependency     | `pip uninstall x`                   | `poetry remove x`       | `uv remove x`           |
| Install all           | `pip install -r requirements.txt`   | `poetry install`        | `uv sync`               |
| Run a command         | `python script.py`                  | `poetry run python ...` | `uv run python ...`     |
| Lock dependencies     | `pip freeze > requirements.txt`     | `poetry lock`           | `uv lock`               |
| Build package         | `python -m build`                   | `poetry build`          | `uv build`              |
| Publish               | `twine upload`                      | `poetry publish`        | `uv publish`            |
| Install global tool   | `pipx install x`                    | —                       | `uv tool install x`     |
| Run global tool once  | `pipx run x`                        | —                       | `uvx x`                 |

---

## 🧼 20. Command Cheat Sheet

```bash
# --- Project lifecycle ---
uv init my_project            # create a new project
uv add requests               # add a dependency
uv add --dev pytest           # add a dev dependency
uv remove requests            # remove a dependency
uv sync                       # sync .venv to match the lockfile
uv lock                       # (re)generate the lockfile
uv run main.py                # run code in the project env
uv tree                       # show the dependency tree

# --- Python versions ---
uv python install 3.12        # install a Python version
uv python list                # list available/installed versions
uv python pin 3.12            # pin version for this project

# --- Tools (pipx replacement) ---
uvx ruff check .              # run a tool once
uv tool install ruff          # install a tool globally
uv tool list                  # list installed tools

# --- pip-compatible layer ---
uv venv                       # create a virtual environment
uv pip install requests       # pip-style install
uv pip compile req.in -o req.txt   # pin requirements (pip-tools)

# --- Build & publish ---
uv build                      # build wheel + sdist
uv publish                    # upload to PyPI

# --- Maintenance ---
uv self update                # update UV itself
uv cache clean                # clear the global cache
```

---

## 🐛 21. Troubleshooting

### ❌ `uv: command not found` after install

**Solution:** Restart your terminal so `PATH` updates. If it persists, add the install location manually:

```bash
# macOS / Linux
export PATH="$HOME/.local/bin:$PATH"
```

On Windows, the installer adds UV to `%USERPROFILE%\.local\bin` — restart PowerShell or sign out/in.

---

### ❌ The lockfile is "out of date" in CI

**Cause:** You changed `pyproject.toml` but didn't commit the updated `uv.lock`.

**Solution:**

```bash
uv lock          # regenerate
git add uv.lock  # commit it
```

Add `uv lock --check` to CI to catch this early.

---

### ❌ A package fails to resolve / version conflict

**Solution:** Inspect the dependency tree and relax over-tight constraints:

```bash
uv tree                       # see what depends on what
uv add "somepkg>=1.0"         # widen the constraint
uv lock --upgrade-package somepkg
```

---

### ❌ Wrong Python version being used

**Solution:** Pin the version explicitly and re-sync:

```bash
uv python pin 3.12
uv sync
```

Check what UV resolved with:

```bash
uv run python --version
```

---

### ❌ `.venv` seems stale / corrupted

**Solution:** Delete and let UV rebuild it:

```bash
# Windows
rmdir /s /q .venv
# macOS / Linux
rm -rf .venv

uv sync
```

---

### ❌ Slow first install behind a proxy / firewall

**Solution:** Point UV at your index and configure proxy env vars:

```bash
export UV_INDEX_URL=https://your-mirror/simple
export HTTPS_PROXY=http://proxy:port
uv sync
```

---

## 📁 22. Key Files & Folders

| File / Folder        | Description                                              | Commit to git? |
| -------------------- | ------------------------------------------------------- | -------------- |
| `pyproject.toml`     | Project metadata & declared dependencies                | ✅ Yes          |
| `uv.lock`            | Exact resolved versions of all deps (cross-platform)    | ✅ Yes          |
| `.python-version`    | Pinned Python version for the project                   | ✅ Yes          |
| `.venv/`             | The virtual environment UV builds                       | ❌ No           |
| `dist/`              | Build artifacts (`.whl`, `.tar.gz`) for publishing      | ❌ No           |
| `README.md`          | Project description                                     | ✅ Yes          |

---

## ✅ 23. Typical End-to-End Workflow

```bash
# 1. Start a project
uv init weather_app
cd weather_app

# 2. Pin a Python version (optional but recommended)
uv python pin 3.12

# 3. Add dependencies
uv add requests rich
uv add --dev pytest ruff

# 4. Write code in main.py ...

# 5. Run it
uv run main.py

# 6. Run tests & lint
uv run pytest
uvx ruff check .

# 7. Commit pyproject.toml + uv.lock
git add pyproject.toml uv.lock
git commit -m "Set up weather_app with UV"

# A teammate then just runs:
#   git clone <repo> && cd weather_app && uv sync && uv run main.py
```

---

## 📚 Further Reading

- Official docs: <https://docs.astral.sh/uv/>
- GitHub: <https://github.com/astral-sh/uv>
- PEP 723 (inline script metadata): <https://peps.python.org/pep-0723/>

---

> 🎉 **You're ready!** Start with `uv init`, use `uv add` to install and `uv run` to execute, and commit your `uv.lock`. Everything else builds on those three commands.
