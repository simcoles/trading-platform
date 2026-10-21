# Trading Platform — Project Handover

## My background and goal

I am an experienced React and TypeScript developer learning Python from the ground up.

I want to build a full-stack trading platform as a practical learning project. Teach me Python and backend engineering progressively, relating new concepts to TypeScript and React where helpful.

I use macOS on Apple Silicon, VS Code, and intend to use Claude Code as a coding mentor.

## Teaching instructions

- Teach me step by step. Do not build the entire application for me.
- Explain Python syntax, types, functions, decorators, modules, exceptions, async/await, and testing as they arise.
- Compare Python concepts with TypeScript equivalents when useful.
- Give me small exercises with clear acceptance criteria.
- Let me attempt exercises before showing a complete solution.
- Review my code and explain why changes are needed.
- Prefer simple, maintainable, production-aware code over unnecessary abstraction.
- Run or explain relevant tests and lint checks after changes.
- Do not assume a command succeeded; ask for output when necessary.
- Keep project documentation and this handover updated as milestones are completed.
- Never include real brokerage credentials or connect to real-money trading systems. All trading activity must be simulated.

## Intended technology stack

- Python 3.13
- `uv` for Python project and dependency management
- FastAPI and Uvicorn
- Pydantic for runtime validation and API schemas
- pytest and HTTPX for testing
- Ruff for linting and formatting
- React and TypeScript for the frontend
- PostgreSQL, SQLAlchemy, and Alembic later
- WebSockets for streaming simulated prices
- Redis for later event-driven communication
- GitHub Actions for CI/CD
- Docker and Docker Compose later, once needed

## Planned project structure

```text
trading-platform/
├── CLAUDE.md
├── frontend/
├── backend/
├── infrastructure/
├── docs/
└── README.md
```

The actual filesystem may not yet match this target structure. Inspect it before creating or moving files.

## Environment already configured

The following versions were confirmed working:

- Python 3.13.16
- pytest 9.1.1
- Ruff 0.17.1
- FastAPI 0.156.8
- uv 0.13.4

The project was initialized using `uv` in the `backend` directory. FastAPI, Uvicorn, pytest, HTTPX, and Ruff were added as dependencies.

The working directory is intended to be:

`~/Projects/trading-platform/backend`

## Current progress

- Installed and verified `uv`.
- Created the `trading-platform` project directory and `backend`, `frontend`, and `docs` directories.
- Initialized a Git repository.
- Initialized the Python backend project.
- Created a basic FastAPI application in `backend/main.py`.
- Encountered and resolved a Uvicorn error caused by Python being unable to import the `main` module.
- The FastAPI development server is now running successfully.

### Milestone 1 complete (2026-10-21): first endpoints, tests, first commit

- `backend/main.py` exposes `GET /` → `{"message": "Trading Platform API is running"}` and `GET /health` → `{"status": "ok"}`.
- `backend/test_main.py` tests both endpoints with FastAPI's `TestClient`.
- The dev dependency `httpx` was replaced with `httpx2`, because Starlette 1.9's test client deprecates `httpx`.
- A root `.gitignore` ignores `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.DS_Store`, and `.env`.
- Git author email configured; first commits made on `main` (no remote yet).
- `main.py` still sits at the root of `backend/`, outside the `src/backend/` package that `uv init` created. Moving it into the package is a later lesson.

Concepts covered: pytest discovery and `assert`, reading pytest diffs, TDD red/green, decorators as route registration, `async def` vs `def` in FastAPI (intro), Ruff `check` vs `format`, import grouping (I001), `.gitignore` patterns and `git check-ignore`, `git commit --amend`.

### Milestone 2 complete (2026-10-21): path/query parameters and status codes

- `GET /prices/{symbol}` looks up a hard-coded `prices` dict (case-insensitive) and returns `{"symbol", "price", "currency"}`.
- Unknown symbols raise `HTTPException(404, detail="Symbol XYZ not found")`.
- The `currency: Literal["USD", "GBP"] = "USD"` query parameter converts with the constant `USD_TO_GBP_RATE = 0.79` and `round(price, 2)`. Any other value returns `422`.
- Tests cover success, case-insensitivity, the USD default, GBP conversion, 404, and 422 (asserting `loc == ["query", "currency"]`). 8 tests in total.
- `backend/pyproject.toml` has `[tool.ruff] src = ["."]`, so import sorting agrees whether Ruff runs from the repo root (VS Code) or `backend/`.
- `.vscode/settings.json` (Ruff as the formatter, format on save) is committed.
- Lesson 3 (in progress): `PriceResponse(BaseModel)` and the `Currency = Literal["USD", "GBP"]` alias. `/prices/{symbol}` uses `response_model=PriceResponse` and returns a model instance.
- `.vscode/settings.json` points Pylance at `backend/.venv`, sets `typeCheckingMode: "standard"`, and adds `extraPaths: ["backend"]`, so type errors (e.g. unknown model fields) show in the editor.

Concepts covered: path parameters and runtime type-hint conversion, query parameters and defaults, `Literal` as a string union, `HTTPException`/`raise`, f-strings, `dict.get` and `is None`, guard clauses, float precision and `round` (`Decimal` deferred to orders), FastAPI ignoring unknown query params, the structure of a 422 body, and avoiding tests that copy the implementation.

Check the actual source files before assuming their contents match this description.

## Pre-commit checklist

Run from the repo root before every commit:

```bash
uv run --directory backend ruff format --check .
uv run --directory backend ruff check .
uv run --directory backend pytest -q
```

## Immediate next steps

Lesson 3: Pydantic models.

1. Define a `PriceResponse(BaseModel)` and use it as the `/prices/{symbol}` response model. Check how it appears in `/docs`.
2. Add `GET /prices` listing all symbols, returning `list[PriceResponse]`.
3. Introduce a request body: a `POST` endpoint that validates its input with a Pydantic model (e.g. a simulated order with `symbol`, `side`, and `quantity > 0`). Test valid input and 422 cases.

## Longer-term roadmap

1. Python fundamentals through small exercises.
2. FastAPI routing, HTTP methods, status codes, and error handling.
3. Pydantic models and request/response validation.
4. Automated tests and code quality checks.
5. A simulated market watchlist and price endpoints.
6. WebSockets that broadcast simulated live price updates.
7. React/TypeScript frontend integration.
8. PostgreSQL persistence, SQLAlchemy, and Alembic migrations.
9. Simulated portfolios, orders, and trading rules.
10. Redis and event-driven architecture.
11. GitHub Actions CI/CD, containerization, and deployment.

## Your first task

Start by inspecting the existing project. Do not overwrite working files or regenerate the project. Report what exists, identify missing pieces, and guide me through the next small lesson: testing the root endpoint and implementing `/health`.
