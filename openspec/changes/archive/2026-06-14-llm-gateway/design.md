## Context

There is no lightweight, self-hosted Python tool that provides transparent LLM API proxying with built-in tracing and a log viewer. Existing solutions (Phoenix, Langfuse) bundle evaluation, datasets, and playground features that add complexity and resource overhead. The user needs a minimal gateway: proxy requests to OpenAI-compatible APIs, capture all data, and browse it via a web UI.

This is a greenfield Python project. No existing code or infrastructure to integrate with.

## Goals / Non-Goals

**Goals:**
- Transparent reverse proxy that clients use as a drop-in replacement for their LLM API base URL
- Full request/response tracing including SSE streaming
- SQLite storage with archive-to-tar.gz capability for long-term use
- Token usage extraction and cost calculation per model
- Clean web UI for browsing and inspecting traces
- Zero external infrastructure dependencies (no Redis, no Postgres, no Node.js)
- Local Tailwind CSS build (no CDN dependency)

**Non-Goals:**
- Multi-provider abstraction layer (future consideration, but not now)
- Authentication/authorization system (personal tool, single user)
- Distributed tracing or OpenTelemetry integration
- LLM evaluation, playground, or dataset management
- Multi-instance or horizontal scaling
- Rate limiting or request queuing

## Decisions

### 1. FastAPI + httpx for proxy server

**Choice**: FastAPI with httpx as the HTTP client.

**Alternatives considered**:
- *Flask + requests*: Synchronous, poor SSE streaming support
- *aiohttp*: Lower-level, more boilerplate for routing and middleware
- *Starlette directly*: Too low-level, FastAPI adds useful defaults (Pydantic validation, OpenAPI)

**Rationale**: FastAPI provides async natively, excellent SSE support via `StreamingResponse`, automatic OpenAPI docs, and Pydantic models for config validation. httpx is the async HTTP client that matches httpx's API design, supports streaming, and handles HTTP/2.

### 2. SQLite with SQLAlchemy + aiosqlite

**Choice**: SQLite accessed through SQLAlchemy async ORM with aiosqlite driver.

**Alternatives considered**:
- *Raw sqlite3*: No async, manual SQL, no migrations
- *PostgreSQL + asyncpg*: Overkill for personal use, requires external service
- *DuckDB*: Analytical focus, less suited for OLTP trace inserts
- *Tortoise ORM*: Less mature, smaller ecosystem

**Rationale**: SQLite handles personal-scale workloads easily (~1,000 req/day = ~1.8GB/year). SQLAlchemy provides migration support (Alembic), query building, and async via aiosqlite. The archive mechanism keeps the active DB manageable.

### 3. Archive strategy instead of auto-purge

**Choice**: Export traces to timestamped `.tar.gz` files containing a SQLite DB dump (or JSON export), then delete from active DB.

**Alternatives considered**:
- *Auto-purge with TTL*: Data loss, user can't recover
- *SQLite ATTACH + export*: Complex, fragile
- *Always keep everything in one DB*: Unbounded growth, slower queries over time

**Rationale**: Archive-to-tar.gz preserves all data, keeps the active DB fast and small, and the archives are portable and inspectable. Users can re-import archives if needed. The archive contains a self-contained SQLite snapshot or JSON export of the traces.

**Archive format**: Each archive is a `.tar.gz` containing:
- `metadata.json`: archive timestamp, trace count, date range
- `traces.jsonl`: one JSON object per trace (complete record including request/response bodies)

### 4. Standalone Tailwind CLI for local CSS

**Choice**: Use the standalone Tailwind CSS CLI binary (single ~20MB executable) to build CSS from source files. No Node.js required.

**Alternatives considered**:
- *Tailwind CDN*: Requires internet, defeated by the user's requirement
- *Full Node.js + npm build*: Heavy toolchain for a Python project
- *Hand-written CSS*: Poor DX, no utility classes
- *Bulma/Bootstrap CDN*: Still CDN dependency

**Rationale**: The standalone Tailwind CLI is a single binary that watches source files and builds CSS. It's the lightest way to get Tailwind locally without Node.js. Include it in the project or download it during setup.

### 5. Alpine.js for frontend reactivity

**Choice**: Alpine.js included as a local JS file for lightweight reactivity (state, bindings, x-for, x-if).

**Alternatives considered**:
- *Vanilla JS only*: More boilerplate for reactivity, harder to maintain
- *React/Vue SPA*: Requires build tooling, overkill for a log viewer
- *HTMX*: Server-driven, but we want a responsive SPA-like experience for log browsing

**Rationale**: Alpine.js is ~15KB, needs no build step, and provides just enough reactivity (state management, template bindings, event handling) for the log viewer. Keep it as a local file alongside Tailwind CSS.

### 6. Project structure

```
sparrow/
├── pyproject.toml
├── sparrow/
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── config.py            # YAML config loading + Pydantic models
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB setup, migrations, session management
│   ├── proxy/
│   │   ├── __init__.py
│   │   ├── router.py        # FastAPI proxy routes
│   │   ├── streaming.py     # SSE interception and forwarding
│   │   └── middleware.py    # Request/response tracing middleware
│   ├── tracing/
│   │   ├── __init__.py
│   │   ├── tracer.py        # Trace recording logic
│   │   └── cost.py          # Token counting and cost calculation
│   ├── archive/
│   │   ├── __init__.py
│   │   └── archiver.py      # Export traces to tar.gz
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py        # REST API for trace queries
│   │   └── schemas.py       # Pydantic response schemas
│   ├── web/
│   │   ├── __init__.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── input.css    # Tailwind source
│   │   │   ├── js/
│   │   │   │   ├── alpine.min.js
│   │   │   │   └── app.js       # Main frontend logic
│   │   │   └── dist/
│   │   │       └── output.css   # Built Tailwind CSS
│   │   └── templates/
│   │       └── index.html
│   └── web_ui.py            # FastAPI mount for web UI
├── config.example.yaml
├── tailwindcss               # Standalone Tailwind CLI binary
└── tests/
    ├── test_proxy.py
    ├── test_tracing.py
    └── test_archive.py
```

### 7. Proxy architecture

The gateway exposes two HTTP services on configurable ports:
- **Proxy port** (default 8080): Receives client requests, forwards to target LLM API, records trace
- **Web UI port** (default 8081): Serves the log viewer and REST API

For SSE streaming:
1. Client sends request to gateway with `stream: true`
2. Gateway opens streaming connection to target API
3. As chunks arrive, gateway simultaneously:
   - Forwards each chunk to the client
   - Accumulates chunks for the trace record
4. When stream ends, gateway parses accumulated content for token usage and saves the complete trace

### 8. Cost calculation model

Cost is calculated from token usage using a configurable pricing table in YAML:

```yaml
pricing:
  gpt-4o:
    input: 2.50    # per 1M tokens
    output: 10.00  # per 1M tokens
  gpt-4o-mini:
    input: 0.15
    output: 0.60
  gpt-3.5-turbo:
    input: 0.50
    output: 1.50
```

Cost formula: `(input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price`

If a model is not in the pricing table, cost is recorded as `null` and the UI shows "Unknown".

## Risks / Trade-offs

- **[SQLite write contention]** → WAL mode enabled, single-writer design is fine for personal use. If concurrency becomes an issue, a connection pool with `pragma busy_timeout` handles it.
- **[SSE streaming memory]** → For very long streaming responses, accumulating all chunks in memory could be problematic. Mitigation: set a configurable max trace body size; truncate with a warning if exceeded.
- **[Proxy latency overhead]** → httpx adds minimal overhead (~1-5ms). The tracing middleware should use background tasks for DB writes to avoid blocking the response.
- **[Tailwind CLI binary size]** → ~20MB binary in the repo. Alternative: download during `sparrow init` or setup script. Trade-off: convenience vs repo size. Decision: include a setup script that downloads it, add to `.gitignore`.
- **[Archive re-import complexity]** → Keep re-import simple: read JSONL from archive, INSERT OR IGNORE into SQLite. No merge/dedup logic needed.
