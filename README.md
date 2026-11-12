# Trading Platform

[![CI](https://github.com/simcoles/trading-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/simcoles/trading-platform/actions/workflows/ci.yml)

A full-stack **simulated** trading platform: live streaming prices, order entry, a portfolio valued in real time, and role-based access through single sign-on. It is a learning project, built step by step to expand Python knowledge and backend engineering coming from React and TypeScript.

> **Everything is simulated.** Prices are a random walk, orders fill instantly at the simulated price, and nothing connects to a real broker or real money.

## What it does

- **Live prices.** A background task moves prices every second, and a WebSocket pushes each tick to every connected browser. AG Grid updates the cells in place and flashes them when they change.
- **Order entry.** An order ticket (symbol, buy or sell, quantity) places simulated orders. A blotter grid lists them newest first, with sorting, filtering and formatted money and times.
- **Portfolio.** Cash and positions are calculated from the order history. The positions grid and a Highcharts allocation chart revalue holdings on every price tick.
- **Single sign-on with roles.** Users log in through Keycloak (OpenID Connect, authorization code flow with PKCE). Traders can place orders. Viewers can see the portfolio and orders but not trade. The API enforces this on every request.
- **Per-user accounts.** Each order records who placed it (the token's `sub`), so every user sees only their own orders and portfolio.
- **Watchlist.** Symbols you follow, stored in PostgreSQL.

## Tech stack

| Area | Tools |
|---|---|
| Frontend | React 19, TypeScript, Vite, MUI, AG Grid Community, Highcharts, `react-oidc-context` |
| Backend | Python 3.13, FastAPI, Pydantic, SQLAlchemy 2, Alembic, PyJWT |
| Data | PostgreSQL 18 |
| Identity | Keycloak 26 (OIDC) |
| Testing | pytest, Vitest, React Testing Library |
| Tooling | uv, Ruff, ESLint, Docker Compose, GitHub Actions |

## Architecture

```text
 Browser (React, :5173)
   │  1. Sign in ─────────────► Keycloak (:8080)
   │     (redirect + PKCE)        realm "trading": roles trader / viewer
   │  ◄──── access token (JWT) ──┘
   │
   │  2. REST with "Authorization: Bearer <JWT>"
   │     WebSocket /ws/prices (public market data)
   ▼
 FastAPI (:8000)
   ├─ checks the JWT signature against Keycloak's public keys (JWKS),
   │  plus expiry, issuer and audience; then checks the role
   ├─ price broadcaster: one background task, fans out ticks to all clients
   └─ SQLAlchemy ──► PostgreSQL (:5433)
                      orders (append-only ledger), watchlist
```

## Design decisions

- **Money is `Decimal`, never `float`.** Amounts are rounded half-up to the cent, and Postgres stores them as `NUMERIC`. The JSON API still sends plain numbers. The fast-moving price feed stays `float`, because it's display-only.
- **The ledger is append-only.** Cash and positions are not stored. They are calculated from the orders table with `SUM(CASE …)` queries, so the totals can never drift away from the history.
- **The server enforces access.** The UI hides the order ticket from viewers for a better experience, but the API checks the `trader` role itself and returns 403 otherwise. Tests prove it.
- **The owner comes from the token, never the request.** Order and portfolio queries filter by the verified user id, so no request parameter can open another user's account.
- **Tokens are verified locally.** FastAPI caches Keycloak's public keys and checks each token's signature without calling Keycloak. The algorithm is pinned to RS256, and the audience must be `trading-api`.
- **One shared price stream.** A single broadcaster task feeds every WebSocket client, so all users see the same prices. If a client is slow, it misses a tick rather than holding up the others.
- **The grids are built for streaming.** AG Grid uses `getRowId`, so a tick updates existing rows instead of rebuilding the table. The chart turns off its intro animation so live updates don't replay it.
- **Accessibility counts.** Buy and sell are shown by text as well as colour, controls have accessible names, the Highcharts accessibility module is loaded, and the component tests query by role and label.

## Performance

The app streams a price tick every second to every browser, so most of the performance work is about keeping each tick cheap from end to end.

### Streaming (backend)

- **One simulation, fanned out.** A single `PriceBroadcaster` task computes each tick once and hands the same dict to every subscriber. The cost of the simulation doesn't grow with the number of clients. Only the send does.
- **Slow clients can't stall fast ones.** Each WebSocket gets an `asyncio.Queue(maxsize=1)`. If a client hasn't read the last tick yet, the broadcaster drops the stale tick and puts in the new one (`get_nowait` / `put_nowait`). It never `await`s a client, so memory per client is bounded at one tick, and a stalled browser only falls behind itself.
- **Nothing blocks the event loop.** The stream is fully `async` and uses `asyncio.sleep`, never `time.sleep`. (A blocking `time.sleep` in the stream loop was tried as an experiment: it froze `/health` for every client until the stream stopped.) Routes that use the synchronous SQLAlchemy session are plain `def`, so FastAPI runs them in its thread pool instead of on the event loop.
- **A snapshot on connect.** A new client gets `current_prices` straight away instead of waiting up to a second for the next tick.

### Rendering (frontend)

- **One socket per tab.** `App` owns the only `useLivePrices()` call and passes prices down, so the price grid, portfolio, positions and charts share one connection.
- **Grids update rows in place.** Every grid sets `getRowId` (the symbol, or the order id), so AG Grid diffs each tick against existing rows and only touches cells that changed. It doesn't rebuild the DOM, and the cell flash works because the row keeps its identity. `columnDefs` live at module level, so the grid gets the same array on every render and doesn't reinitialise its columns.
- **Derived data is memoised.** Live position values (`Portfolio`), weights (`PositionsGrid`) and Highcharts `options` (both charts) are wrapped in `useMemo`, keyed on the data they depend on. They are recalculated once per tick, not on every unrelated render.
- **Charts skip animation.** `animation: false` stops Highcharts replaying its intro animation every second. The line chart also hides point markers.
- **Bounded history.** The line chart keeps a rolling window of 120 points per symbol (`MAX_POINTS`, two minutes). Memory and redraw cost stay flat however long the tab is open. `appendTick` is a pure function with unit tests.
- **The network is used sparingly.** The portfolio is fetched again only when an order is placed (`refreshKey`), not on every tick. Live revaluation happens in the browser from prices it already has. Reconnects use capped exponential backoff with jitter, so clients don't all retry at the same moment after a server restart.

### Data and auth

- **Totals are computed in the database.** Cash and positions are single `SUM(CASE …)` / `GROUP BY` queries, so only the result crosses the wire, not every order row.
- **Queries filter on an indexed column.** `orders.owner_sub` has an index, because every order and portfolio query filters by the current user.
- **Pooled connections.** SQLAlchemy reuses connections from a pool. `pool_pre_ping` throws away dead connections before use, instead of failing the request.
- **Token checks don't call Keycloak.** `PyJWKClient` caches Keycloak's public keys, so verifying a JWT is a local signature check. Keycloak is contacted again only when a token arrives with an unknown key id, after key rotation.

### Known limits and what I'd do next

These are deliberate trade-offs for a simulator with a handful of symbols. Each one would be the next step at a larger scale:

- **Every tick re-renders the whole `App` tree.** Price state lives in `App`, so sections that don't use prices (watchlist, orders) re-render too. They are cheap today. At scale, I'd move prices into a store with selector subscriptions (`useSyncExternalStore`, Zustand), so each component re-renders only when its own slice changes. Or I'd push ticks straight into AG Grid with `applyTransactionAsync`, bypassing React.
- **The line chart rebuilds its series each tick.** For a few symbols × 120 points that's negligible. At higher frequencies, I'd keep a chart ref and call `series.addPoint(point, true, shift)`, so Highcharts appends one point instead of diffing the whole series.
- **Ticks are full snapshots.** Every message carries every symbol. With hundreds of symbols, I'd send only what changed, and let clients subscribe to the symbols they show.
- **The ledger is recomputed on every read.** Summing the order history is simple and can't drift, but it grows with order count. The usual fix is a positions table or a materialised snapshot, updated in the same transaction as each order.
- **One process.** The broadcaster lives in the server's memory, so several Uvicorn workers would each run their own simulation. The roadmap item is Redis pub/sub: one publisher, with every worker forwarding to its own clients.
- **No measurements yet.** The points above come from the design, not from profiling. Next, I'd measure: React Profiler commit times per tick, Chrome Performance traces with many open tabs, and a WebSocket load test (for example, a few thousand `websockets` clients) to find where the send loop saturates.

## Getting started

Prerequisites: Docker, [uv](https://docs.astral.sh/uv/) and Node 26.

```bash
cp .env.example .env              # then fill in local values (see below)
docker compose up -d --wait       # PostgreSQL and Keycloak
uv run --directory backend alembic upgrade head
docker compose exec db createdb -U <POSTGRES_USER> trading_test   # once, for the tests
```

`.env` needs `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`, `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`. For example, `DATABASE_URL=postgresql+psycopg://<user>:<password>@localhost:5433/trading`. The file is ignored by Git.

Run the servers in two terminals:

```bash
uv run --directory backend uvicorn backend.main:app --reload    # API on :8000, docs at /docs
npm --prefix frontend install && npm --prefix frontend run dev  # app on http://localhost:5173
```

### Demo users

The Keycloak realm is imported from `infrastructure/keycloak/trading-realm.json` and includes two local test users:

| User | Password | Role | Can |
|---|---|---|---|
| `alice` | `alice` | trader | view and place orders |
| `bob` | `bob` | viewer | view only |

## Testing

```bash
uv run --directory backend ruff format --check .
uv run --directory backend ruff check .
uv run --directory backend pytest -q        # needs the database container
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend test -- run
```

- **Backend (pytest):** unit tests for pricing and the market simulation, and API tests through FastAPI's `TestClient`. They run against a separate `trading_test` database, where each test runs in a transaction that is rolled back afterwards. Auth tests sign their own tokens with a throwaway RSA key, covering missing, expired, wrong-key, wrong-audience and wrong-issuer tokens, and the trader and viewer roles.
- **Frontend (Vitest + React Testing Library):** formatting helpers, and the order ticket driven the way a user would use it, with the API module mocked.
- **CI (GitHub Actions):** every push to `main` and every pull request runs both suites on Ubuntu. The backend job runs against a Postgres service container.

## Project structure

```text
trading-platform/
├── backend/
│   ├── src/backend/
│   │   ├── main.py          # app, CORS, lifespan (starts the price broadcaster)
│   │   ├── auth.py          # JWT validation, CurrentUser / TraderUser dependencies
│   │   ├── orders.py        # place and list orders
│   │   ├── portfolio.py     # cash and positions from the order ledger
│   │   ├── pricing.py       # Decimal money helpers
│   │   ├── broadcaster.py   # shared live price stream
│   │   ├── orm.py, db.py    # SQLAlchemy models and sessions
│   │   └── routers/         # HTTP and WebSocket endpoints
│   ├── migrations/          # Alembic
│   └── tests/
├── frontend/src/
│   ├── App.tsx, auth.ts     # layout, sign-in, roles
│   ├── api.ts               # the only module that calls fetch
│   ├── useLivePrices.ts     # WebSocket hook with reconnect backoff
│   ├── PriceGrid, OrdersBlotter, PositionsGrid   # AG Grid
│   ├── AllocationChart.tsx  # Highcharts
│   └── OrderTicket.tsx (+ .test.tsx)
├── infrastructure/keycloak/ # realm import
├── docker-compose.yml       # PostgreSQL + Keycloak
└── .github/workflows/ci.yml
```

## Roadmap

- Redis pub/sub so the price stream works across several server processes
- Containerised deployment

## Licences

Highcharts is free for non-commercial use, which covers this learning project. Commercial use needs a [Highcharts licence](https://shop.highsoft.com/). AG Grid Community is MIT-licensed.
