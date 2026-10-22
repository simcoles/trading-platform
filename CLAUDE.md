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
- `GET /prices?currency=` returns `list[PriceResponse]` built with a list comprehension. Conversion and rounding are extracted into `convert_price(price, currency) -> float`, shared by both endpoints. 11 tests.
- Git lesson: undoing an accidental unpushed commit with `git reset --soft HEAD~1`.

### Milestone 3 complete (2026-10-22): Pydantic models and request bodies

- `POST /orders` (simulated, nothing stored) takes `OrderRequest` (`symbol`, `side: Side = Literal["buy", "sell"]`, `quantity: int = Field(gt=0)`) and returns `OrderResponse` (adds `price` and `total`) with status `201`.
- Shared helpers: `get_price_or_404(symbol)`, `convert_price(price, currency)` (always rounds to 2 decimal places), and `calculate_total(price, quantity)` (rounds to 2 decimal places).
- 20 tests: integration tests via `TestClient`, unit tests for the helpers, and `@pytest.mark.parametrize` for invalid quantities.
- VS Code organises imports on save (`source.organizeImports.ruff`). Format-on-save alone does not sort imports.
- Prices are `float` with rounding at the edges. Switch to `decimal.Decimal` when orders are persisted.

Concepts covered: `BaseModel`, `response_model`, model instances vs dicts (errors surface at the line that caused them), type aliases, `list[T]`, list comprehensions, `dict.items()` unpacking, `all()`/`any()`, `-> T` return types, request bodies, `Field` constraints, 201 vs 200, the 422 list `detail` vs the `HTTPException` string `detail`, `parametrize` (like `test.each`), `pytest -k`, unit vs integration tests, choosing test inputs that exercise rounding, Python indentation as syntax, and Pylance `typeCheckingMode`.
- `.vscode/settings.json` points Pylance at `backend/.venv`, sets `typeCheckingMode: "standard"`, and adds `extraPaths: ["backend"]`, so type errors (e.g. unknown model fields) show in the editor.

Concepts covered: path parameters and runtime type-hint conversion, query parameters and defaults, `Literal` as a string union, `HTTPException`/`raise`, f-strings, `dict.get` and `is None`, guard clauses, float precision and `round` (`Decimal` deferred to orders), FastAPI ignoring unknown query params, the structure of a 422 body, and avoiding tests that copy the implementation.

Check the actual source files before assuming their contents match this description.

### Milestone 4 complete (2026-10-22): modules, routers, and test fixtures

Current backend layout:

```text
backend/
├── pyproject.toml         # [tool.ruff] src = ["src"]
├── src/backend/           # installed in editable mode by uv (backend.pth), so `import backend` works from any folder
│   ├── main.py            # app, include_router calls, / and /health
│   ├── models.py          # Currency, Side, PriceResponse, OrderRequest, OrderResponse
│   ├── pricing.py         # prices data, convert_price, calculate_total, get_price_or_404
│   └── routers/
│       ├── prices.py      # APIRouter(prefix="/prices")
│       └── orders.py      # APIRouter(prefix="/orders")
└── tests/
    ├── conftest.py        # `client` fixture
    ├── test_root.py
    ├── test_prices.py
    ├── test_orders.py
    └── test_pricing.py    # unit tests, no client
```

- 20 tests, unchanged in behaviour through the whole refactor.
- The `uv init` placeholder `main()` and `[project.scripts]` were removed. Pylance `extraPaths` is no longer needed.
- Known coupling to fix later: `pricing.py` raises FastAPI's `HTTPException`. Replace it with a custom domain exception that the routes translate into a 404.

Concepts covered: `sys.path` and how imports resolve, editable installs (`.pth`, like `npm link`), packages and `__init__.py`, absolute imports, one-way import direction to avoid circular imports, importing names from the module that defines them (Python has no `export`), `APIRouter` prefixes (full path = prefix + route path; use `""` not `"/"`), `git mv` to keep history, pytest fixtures (dependency injection by parameter name, `yield` for teardown), `conftest.py`, and `pytest --collect-only`.

## Running the app

From any folder:

```bash
uv run --project ~/Projects/trading-platform/backend uvicorn backend.main:app --reload
```

Docs at http://127.0.0.1:8000/docs.

## Pre-commit checklist

Run from the repo root before every commit:

```bash
uv run --directory backend ruff format --check .
uv run --directory backend ruff check .
uv run --directory backend pytest -q
```

## Immediate next steps

Lesson 5: Error handling and in-memory state.

1. Custom exceptions: define `UnknownSymbolError` in the domain code, and register a FastAPI exception handler that turns it into a 404 (removes the `HTTPException` coupling from `pricing.py`).
2. A simulated watchlist held in memory: `GET /watchlist`, `POST /watchlist` (201, 409 for duplicates), `DELETE /watchlist/{symbol}` (204, 404).
3. Test isolation: a fixture that resets in-memory state between tests, using `yield`.

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
