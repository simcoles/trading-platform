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

### Milestone 5 complete (2026-10-26): custom exceptions and in-memory state

- `exceptions.py` holds the domain errors `UnknownSymbolError`, `SymbolAlreadyInWatchlistError`, and `SymbolNotInWatchlistError`. Handlers in `main.py` map them to 404, 409, and 404 with `{"detail": str(exc)}`. Domain modules (`pricing.py`, `watchlist.py`) have no FastAPI imports.
- `pricing.get_price_or_404` was renamed to `look_up_price`. It raises `UnknownSymbolError`.
- `watchlist.py` holds a module-level `_watchlist: set[str]` with `get_watchlist` (sorted list), `add_to_watchlist`, and `remove_from_watchlist`.
- `routers/watchlist.py`: `GET /watchlist` → `list[str]`; `POST /watchlist` (body `WatchlistItem`) → 201; `DELETE /watchlist/{symbol}` → 204 with no body.
- `tests/conftest.py` has an `autouse` fixture that calls `clear_watchlist()` before every test. Tests pass alone, reordered, and reversed.
- 28 tests.

Concepts covered: exception classes (`__init__`, `self`, `super()`), `raise` and `try`/`except` (filtering by type), exceptions travelling up the call stack (no return-code checks), FastAPI `exception_handler` and `JSONResponse`, `pytest.raises` (and `exc_info.value`), `with` context managers, `set` vs `dict` (`set()` vs `{}`), `in`/`not in`, `remove` vs `discard`, built-in types as classes, annotation (`:`) vs assignment (`=`) and chained assignment, query parameter vs body vs path parameter (decided by type and name), 201/204/409 status codes, 204 having no `response_model`, `python -c "import backend.main"` to check that the app loads, order-dependent tests, running single tests and reordered tests, and `autouse` fixtures.

Recurring review points to keep watching: assert `detail` bodies on error tests (a status code alone can pass because of a missing route), make each test set up its own data, check indentation after pasting, and run `git status` before committing.

### Milestone 6 complete (2026-11-02): async and WebSockets

- `playground/async_demo.py` compares sequential `await` (3s) with `asyncio.gather` (1s).
- `market.py`: `MAX_MOVE = 0.01`, `next_price(price, rng)` (random walk of at most ±1%, rounded to 2 places), and `simulate_tick(current, rng)`, which returns a new dict and never mutates its input. `rng: random.Random` is injected so tests can pass a seeded generator.
- `routers/stream.py`: `WS /ws/prices` accepts the connection, copies `prices`, creates one `random.Random()` per connection, then loops forever: `simulate_tick` → `send_json` → `await asyncio.sleep(TICK_SECONDS)` (1.0). It catches `WebSocketDisconnect` when the client leaves.
- `tests/test_stream.py`: first message has every symbol within 1% of its start price; 5 messages arrive quickly with `monkeypatch.setattr(stream, "TICK_SECONDS", 0)`, and prices move; the shared `prices` dict is unchanged after streaming.
- Manual experiment: with `time.sleep` in place of `asyncio.sleep`, `/health` hung until the stream stopped, and Ctrl+C could not shut the server down (needed `pkill -f "uvicorn backend.main:app"`). Reverted with `git restore`.
- 35 tests.

Concepts covered: the event loop (one thread, like JS), coroutines are lazy ("never awaited"), `asyncio.run`, `asyncio.sleep` vs blocking `time.sleep` (Ruff ASYNC251), `asyncio.gather`, `time.perf_counter` (seconds, not ms), `random.Random(seed)` and dependency injection for deterministic tests, dict comprehensions, returning new dicts vs mutating, `dict(d)`/`d.copy()` vs aliasing, `dict.items()` yielding `(key, value)` in that order, WebSocket routes (`@router.websocket`, `accept`, `send_json`, `WebSocketDisconnect`), `TestClient.websocket_connect`, `monkeypatch.setattr` on module constants, browser `new WebSocket(...)`, and stopping stuck processes (`Ctrl+C`, `pkill`, `lsof -i :8000`).

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

Lesson 7: React/TypeScript frontend integration (roadmap item 7).

1. Scaffold `frontend/` (Vite + React + TypeScript) and run it alongside the backend.
2. CORS: why the browser blocks `localhost:5173` → `localhost:8000`, and FastAPI's `CORSMiddleware`.
3. Fetch `GET /prices` and the watchlist from React; type the responses to match the Pydantic models.
4. Subscribe to `/ws/prices` in a hook and render live prices.

Possible backend follow-ups: each WebSocket connection currently has its own independent price walk (clients see different prices); a shared broadcaster comes with Redis/event-driven work later.

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
