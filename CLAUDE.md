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
- `routers/stream.py` (superseded by the shared broadcaster in Milestone 7): `WS /ws/prices` accepts the connection, copies `prices`, creates one `random.Random()` per connection, then loops forever: `simulate_tick` → `send_json` → `await asyncio.sleep(TICK_SECONDS)` (1.0). It catches `WebSocketDisconnect` when the client leaves.
- `tests/test_stream.py`: first message has every symbol within 1% of its start price; 5 messages arrive quickly with `monkeypatch.setattr(stream, "TICK_SECONDS", 0)`, and prices move; the shared `prices` dict is unchanged after streaming.
- Manual experiment: with `time.sleep` in place of `asyncio.sleep`, `/health` hung until the stream stopped, and Ctrl+C could not shut the server down (needed `pkill -f "uvicorn backend.main:app"`). Reverted with `git restore`.
- 35 tests.

Concepts covered: the event loop (one thread, like JS), coroutines are lazy ("never awaited"), `asyncio.run`, `asyncio.sleep` vs blocking `time.sleep` (Ruff ASYNC251), `asyncio.gather`, `time.perf_counter` (seconds, not ms), `random.Random(seed)` and dependency injection for deterministic tests, dict comprehensions, returning new dicts vs mutating, `dict(d)`/`d.copy()` vs aliasing, `dict.items()` yielding `(key, value)` in that order, WebSocket routes (`@router.websocket`, `accept`, `send_json`, `WebSocketDisconnect`), `TestClient.websocket_connect`, `monkeypatch.setattr` on module constants, browser `new WebSocket(...)`, and stopping stuck processes (`Ctrl+C`, `pkill`, `lsof -i :8000`).

### Milestone 7 complete (2026-11-05): React frontend, CORS, shared price broadcaster

Frontend (`frontend/`, Vite + React 19 + TypeScript, Node 26 / npm 11):

- `typescript` is pinned to `~6.0.3`, because `typescript-eslint` 8.72 does not support TS 7 yet (the Vite template's `~7.0.2` caused an `ERESOLVE` peer conflict). Bump it when typescript-eslint supports 7.
- MUI 9.5 (`@mui/material` + Emotion) and AG Grid Community 36.2 (`ag-grid-community`, `ag-grid-react`). `main.tsx` registers `AllCommunityModule`, wraps the app in `ThemeProvider` + `CssBaseline`; `index.css` was removed.
- `src/api.ts` is the only place that calls `fetch`: `API_URL`, `WS_URL` (built from `API_URL`), types mirroring the Pydantic models (`Currency`, `PriceResponse`, `WatchlistItem`), `ApiError(status, message)`, and `request<T>` (turns `detail` string-or-list into a message, handles 204, falls back for non-JSON errors).
- `src/useLivePrices.ts`: WebSocket hook with `ignore` guard, status `connecting | open | reconnecting | closed`, reconnect with capped exponential backoff and jitter (500ms base, 10s cap, 8 attempts), cleanup clears the timer and closes the current socket.
- `src/PriceGrid.tsx`: typed `AgGridReact<PriceResponse>` with module-level `columnDefs`/`getRowId`, `enableCellChangeFlash` on price, warning/error alerts above the last known prices.
- `src/Watchlist.tsx`: MUI form + chips, re-fetches after each change (server is the source of truth), `ApiError` messages in a dismissible `Alert`, Add disabled for blank input.
- `App.tsx` owns layout and headings (`Container`, `Stack`, `Typography` with `component="h1"/"h2"`).
- No frontend test runner yet; behaviour verified manually (CORS errors, preflights, reconnect, 403 on `npm run preview` at :4173).

Backend:

- `config.py`: `FRONTEND_ORIGIN = "http://localhost:5173"`, imported by `main.py` (`CORSMiddleware`: that origin, `GET/POST/DELETE`, `Content-Type`) and `stream.py` (Origin check, because browsers do not apply CORS to WebSockets; rejects with close code 1008 before `accept()`, which uvicorn turns into a 403).
- `WatchlistItem`: `model_config = ConfigDict(str_strip_whitespace=True)`, `symbol: str = Field(min_length=1, max_length=10)`.
- `broadcaster.py`: `PriceBroadcaster(rng)` with `current_prices`, `subscribe()` → `asyncio.Queue(maxsize=1)`, `unsubscribe()`, `tick()` (drops a stale tick rather than waiting on slow clients), `run()`; module-level `broadcaster` instance. This replaces the per-connection loop described in Milestone 6, so all clients see the same prices.
- `main.py` `lifespan` (`@asynccontextmanager`, `-> AsyncGenerator[None]`) starts `broadcaster.run()` with `asyncio.create_task` and cancels/awaits it on shutdown.
- `stream.py` only reads shared state: sends `current_prices` on connect, then forwards ticks from its queue; `unsubscribe` in `finally`.
- `tests/conftest.py`: `with TestClient(app) as client: yield client`, so the lifespan runs in tests (without `with`, the task never starts and only the snapshot arrives).
- Tests: `test_cors.py` (allowed/other origin, preflight, parametrized rejected preflights), `test_broadcaster.py` (unit tests, no timing), `test_stream.py` (snapshot shape, two clients get the same prices, rejected origins). 49 tests.
- Known limits: watchlist and broadcaster state are in process memory (lost on reload, separate per worker); next fix is persistence (roadmap 8) and Redis pub/sub for multiple workers (roadmap 10).

Concepts covered: npm peer dependency conflicts vs uv resolution, lockfiles (`package-lock.json` ↔ `uv.lock`), Node resolving `node_modules` up the tree (install in the right folder), CORS (browser-enforced, server opts in, exact origin match, simple vs preflighted requests, `Access-Control-Max-Age` caching), middleware and `add_middleware`, keyword arguments, `in` vs `==` for exact assertions, `parametrize` `ids` and one-variable-per-case rows, TS types as unchecked mirrors of Pydantic models, `detail` as string or list, `erasableSyntaxOnly`, `FormEvent` → `SubmitEvent` (React 19 types), macOS case-insensitive filenames vs Linux, headings/spacing owned by the parent, Pydantic `ConfigDict` (unknown keys silently ignored) vs `Field` constraints, validating on both client (UX) and server (correctness), WebSocket lifecycle and StrictMode double effects, WebSockets not covered by CORS (check `Origin`), circular imports and `config.py`, combined `with (a, b):` (Ruff SIM117), classes with state (`self`, `__init__`, conventional `_private`), `asyncio.Queue` and `*_nowait`, look-before-you-leap vs EAFP, reads vs writes to shared state, `finally` for cleanup, `asyncio.create_task`, FastAPI `lifespan` (replaces deprecated `on_event`), `AsyncGenerator` vs deprecated `AsyncIterator` annotation (type-stub deprecations are editor-only), no hoisting in Python, `TestClient` as a context manager, avoiding timing-dependent tests, exponential backoff with jitter, and in-memory state lasting only as long as the process.

Recurring review points (frontend): save files before asking for a check (enable Auto Save), run `npm` from `frontend/`, remove leftover TODOs and unused imports (`noUnusedLocals` fails the build), avoid shadowing outer variables.

### Milestone 8 complete (2026-11-10): PostgreSQL, SQLAlchemy, Alembic

- `docker-compose.yml` (repo root): `postgres:18-alpine` on `127.0.0.1:5433` (an EDB PostgreSQL 15 system service already owns 5432; leave it alone), volume mounted at `/var/lib/postgresql` (the Postgres 18 layout), `pg_isready` healthcheck. Credentials come from the gitignored root `.env`; `.env.example` lists the keys with empty values.
- `.env` also holds `DATABASE_URL=postgresql+psycopg://...@localhost:5433/trading`. The `+psycopg` driver part is required; plain `postgresql://` makes SQLAlchemy look for psycopg2.
- Dependencies: `sqlalchemy` 2.1, `psycopg[binary]` 3.3, `pydantic-settings` 2.16, `alembic` 1.20.
- `config.py`: `REPO_ROOT`, `Settings(BaseSettings)` with `database_url: str` read from `REPO_ROOT / ".env"` (`extra="ignore"`), module-level `settings`. `Settings()` carries `# pyright: ignore[reportCallIssue]` because the checker cannot see env-filled fields.
- `db.py`: `engine` (`pool_pre_ping=True`), `SessionLocal`, `get_session()` generator dependency, and `SessionDep = Annotated[Session, Depends(get_session)]`.
- `orm.py`: `Base(DeclarativeBase)` and `WatchlistEntry` (`watchlist` table: `id` integer primary key/SERIAL, `symbol` `String(10)` unique). Pydantic models (`models.py`) describe the API; ORM models describe tables.
- `watchlist.py`: domain functions take a `Session` first. `add_to_watchlist` relies on the unique constraint (catches `IntegrityError`, rolls back, raises `SymbolAlreadyInWatchlistError ... from None`) instead of check-then-insert. Still no FastAPI imports.
- Watchlist routes and `GET /health/db` (`routers/health.py`, runs `select 1`) are plain `def`, because the SQLAlchemy session blocks.
- Alembic in `backend/`: `alembic.ini` has no URL (post-write hooks run `ruff check --fix` and `ruff format` on new migrations); `migrations/env.py` uses `Base.metadata` and falls back to `settings.database_url` only when no URL was passed in. First migration `81f88f345651` creates `watchlist`.
- Tests use a separate `trading_test` database (name derived from `DATABASE_URL` + `_test`). `conftest.py`: session-scoped `engine` fixture runs `alembic upgrade head` once per run (URL `%` escaped as `%%` for configparser); function-scoped `session` fixture wraps each test in a transaction with `join_transaction_mode="create_savepoint"` and rolls it back; `client` overrides `get_session` via `app.dependency_overrides`. Dev data survives test runs and the test database is empty afterwards. 50 tests.
- The watchlist now survives server restarts.

Concepts covered: Docker Compose (services, ports bound to `127.0.0.1`, named volumes, healthchecks, `up -d --wait`, `down` vs `down -v`, `${VAR}` vs `$${VAR}`), `.env` vs `.env.example`, pydantic-settings, `Path` and the `/` operator, type-checker limits and targeted `pyright: ignore[rule]`, public vs internal imports (`fastapi` vs `fastapi.params`), engine/connection pool vs session, `def` vs `async def` with blocking libraries (thread pool), `Depends`/`Annotated` and generator dependencies (like `yield` fixtures), pytest fixtures vs FastAPI dependencies, declarative models (`Mapped`, `mapped_column`, `__tablename__`), reading generated SQL (`CreateTable`), SERIAL and sequences that never reuse ids, `select`/`where`/`order_by`, `scalars` vs `scalar`, `add`/`delete`/`commit`/`rollback`, overloaded `==` building SQL, unique constraints over check-then-insert (race conditions), `raise ... from None`, catching only where you can handle it, Alembic (revisions chain, autogenerate as a draft to read, `upgrade`/`downgrade`/`current`/`check`, post-write hooks), fixture scopes (`session` vs `function`; pytest "session" ≠ SQLAlchemy `Session`), fixtures depending on fixtures, transactions and savepoints, `dependency_overrides`, Ruff's magic trailing comma.

Deferred: switch money values to `decimal.Decimal` when orders are persisted (start of Lesson 9).

## Running the app

Start the database first (from the repo root), then the servers in two terminals:

```bash
docker compose up -d --wait
uv run --directory backend alembic upgrade head   # after pulling new migrations
```

One-time setup for tests: `docker compose exec db createdb -U trading trading_test` (the test fixtures migrate it).

```bash
uv run --project ~/Projects/trading-platform/backend uvicorn backend.main:app --reload
npm --prefix ~/Projects/trading-platform/frontend run dev
```

API docs at http://127.0.0.1:8000/docs. Frontend at http://localhost:5173 (must be `localhost`, matching `FRONTEND_ORIGIN`).

## Pre-commit checklist

Run from the repo root before every commit:

```bash
uv run --directory backend ruff format --check .
uv run --directory backend ruff check .
uv run --directory backend pytest -q
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend test -- run
```

Backend tests need the database container running. Then `git status` to check nothing unexpected is modified (and that `.env` is never listed). When work is ready, the mentor suggests a commit message; the user makes the commit.

## Immediate next steps

Lesson 9: simulated portfolios, orders, and trading rules (roadmap item 9). Fast-tracked toward data grids, charts and authentication (decided 2026-11-10, for a frontend interview focused on investment analytics).

Done so far: money is `Decimal` (`round_money`, half-up; `Money` serializes as a JSON number; the live feed stays float, converted in `PriceBroadcaster`); `orders` table (second migration `0bda7016625a`), `POST /orders` saves, `GET /orders` newest first. 53 tests.

1. Done: `portfolio.py` derives cash and positions from the order history (`case`/`sum`/`coalesce`/`group_by`/`having`, `scalar_one()`); `GET /portfolio`. 57 tests.
2. Done: `OrdersBlotter` (AG Grid, `format.ts` with `Intl` formatters, Vitest with `TZ=UTC`) and `OrderTicket` (MUI select, side toggle, client-side quantity check). `App` owns the single `useLivePrices()` socket and an `ordersVersion` counter; `Orders` prepends the placed order and calls `onPlaced()`; `Portfolio` refetches on `refreshKey` and values positions at live prices with `useMemo`.
3. Done: `PositionsGrid` (AG Grid in `Portfolio`): quantity, live price (cell flash), market value, weight (`Intl` percent, guarded against zero invested); rows updated in place via `getRowId`.
4. Charts with **Highcharts** 13.1 + `@highcharts/react` 5.4 (non-commercial licence). Done: `AllocationChart` (bar chart, `<Accessibility />` module). `vite.config.ts` has `optimizeDeps.exclude: ["@highcharts/react"]`, because dev pre-bundling of its lazy series imports caused "Class extends value undefined". Still to do: a live price line chart.
5. Done: React Testing Library (`jsdom` environment, `src/test-setup.ts` loads jest-dom matchers and runs `cleanup`). `OrderTicket.test.tsx` mocks `placeOrder` with `vi.mock` + `importOriginal`, drives the UI with `userEvent` (MUI Select opens on mousedown, so `element.click()` is not enough), queries by role/label, and checks both the request sent and the `onPlaced` callback. 6 frontend tests.
6. Trading rules: no buying beyond cash, no selling more than held (409, shown in the order form).
7. Authentication with **Keycloak in Docker Compose** (OIDC auth code + PKCE in React; FastAPI validates JWTs via JWKS; a roles claim for RBAC, e.g. only traders can place orders; orders get an owner `sub` for per-user entitlements). Note where Entra ID/MSAL differs.

Later: Redis, CI, and possibly replacing the hard-coded `prices` with live prices when filling orders.

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
