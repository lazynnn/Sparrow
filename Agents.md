# Agents.md — Sparrow System Documentation

## 1. System Overview

Sparrow is a lightweight local LLM gateway that provides transparent reverse proxying, request/response tracing, cost tracking, and a web-based log viewer. It sits between LLM client applications and upstream API providers (OpenRouter, OpenAI, Anthropic, etc.), intercepting all traffic for observability without requiring any client-side changes.

**Separation of concerns:**

- **Python backend** — handles all runtime logic: reverse proxying, request routing, streaming/non-streaming response forwarding, trace persistence, cost calculation, SSE push notifications, archive management, and serving the Web UI
- **JavaScript frontend** — vanilla Alpine.js single-page app for browsing traces, viewing dashboards, and managing archives; communicates exclusively via the backend REST API

---

## 2. Architecture & Data Flow

### Dual-server design

Two FastAPI apps run simultaneously via separate Uvicorn processes:

| Server | Port | Purpose |
|--------|------|---------|
| Proxy  | 8080 (configurable) | Catch-all reverse proxy — intercepts all HTTP methods and forwards to upstream APIs |
| Web UI | 8081 (configurable) | Serves the SPA and exposes the `/api/*` REST endpoints |

### Full request lifecycle

```
Client → Proxy (8080) → Route matching → Target API → Response → Client
                                    ↓
                              Trace saved (background)
                                    ↓
                              SSE notify → Web UI (8081)
```

1. Client sends an LLM request to the proxy port (e.g., `POST /v1/chat/completions`)
2. `proxy_request()` calls `_match_route()` — longest-prefix-match against configured route prefixes
3. Target URL is constructed: `{route.target_base_url}{request.path}`
4. Hop-by-hop headers are filtered; request body is read
5. `stream: true` in the JSON body triggers streaming mode
6. Request forwarded via `httpx.AsyncClient` (with optional upstream proxy transport)
7. **Non-streaming**: response body returned to client; trace saved via `FastAPI BackgroundTasks`
8. **Streaming**: SSE chunks accumulated and yielded to client; trace saved after stream completes
9. `notify_new_trace()` pushes a lightweight event to all SSE listeners on `/api/traces/stream`
10. Frontend `EventSource` receives the event and updates the trace list in real-time

### Data contracts

**Trace JSON** (stored in SQLite, served via API):

```json
{
  "id": "uuid-string",
  "timestamp": "ISO-8601",
  "method": "POST",
  "path": "/v1/chat/completions",
  "target_url": "https://openrouter.ai/api/v1/chat/completions",
  "status_code": 200,
  "duration_ms": 1523.4,
  "ttfb_ms": 340.2,
  "model": "openai/gpt-4o",
  "prompt_tokens": 120,
  "completion_tokens": 45,
  "total_tokens": 165,
  "cost": 0.0032,
  "request_body": "...",
  "response_body": "...",
  "is_stream": true,
  "route_name": "openrouter"
}
```

**SSE chunk event** (pushed to frontend):

```json
{"type": "new_trace", "trace_id": "uuid", "model": "...", "path": "..."}
```

**Archive structure** (tar.gz):

```
metadata.json   — {exported_at, trace_count, sparrow_version}
traces.jsonl    — one JSON object per line (full trace records)
```

---

## 3. Component Breakdown

### Frontend

| Module | File | Responsibility |
|--------|------|----------------|
| App root | `sparrow/web/static/js/app.js` | Alpine.js `App` component — view routing, state management, API calls |
| HTML template | `sparrow/web/templates/index.html` | Single-page layout with three views: Traces, Dashboard, Archives |
| CSS source | `sparrow/web/static/css/input.css` | Tailwind CSS v4 source with custom components (JSON viewer, trace cards, etc.) |

**Key frontend state**: `traces[]`, `currentTrace`, `dashboardData`, `archives[]`, `view` (traces/dashboard/archives), `theme` (dark/light)

**API calls** (all to Web UI port 8081):
- `GET /api/traces` — list traces with pagination/filtering
- `GET /api/traces/{id}` — single trace detail
- `GET /api/traces/stream` — SSE real-time updates
- `DELETE /api/traces` — clear all traces
- `GET /api/dashboard` — aggregated stats
- `GET /api/archives` — list archives
- `POST /api/archives/create` — create archive from current traces
- `POST /api/archives/{name}/import` — import archive

### Backend

| Component | File | Responsibility |
|-----------|------|----------------|
| Entry point | `sparrow/__main__.py` | Starts dual Uvicorn servers (proxy + web UI) |
| Config | `sparrow/config.py` | Pydantic `AppConfig` — YAML config loading, validation, defaults |
| Database | `sparrow/database.py` | Async SQLite wrapper — init, session management, WAL mode |
| Models | `sparrow/models.py` | SQLAlchemy `Trace` model + `truncate_body()` |
| Proxy router | `sparrow/proxy/router.py` | Core proxy logic — route matching, request forwarding, streaming handling |
| Streaming utils | `sparrow/proxy/streaming.py` | Header filtering, SSE chunk accumulation |
| Middleware | `sparrow/proxy/middleware.py` | `TracingMiddleware` (minimal, currently unused) |
| Tracer | `sparrow/tracing/tracer.py` | `save_trace()` — parser dispatch, cost calculation, SSE notification |
| Cost calc | `sparrow/tracing/cost.py` | Token usage → cost using pricing config |
| Parser registry | `sparrow/tracing/parsers/registry.py` | `ParserRegistry` — prefix-based parser lookup |
| Parser base | `sparrow/tracing/parsers/base.py` | `BaseParser` abstract class |
| OpenAI Chat parser | `sparrow/tracing/parsers/openai_chat.py` | Parses `/v1/chat/completions` responses (default parser) |
| OpenAI Responses parser | `sparrow/tracing/parsers/openai_responses.py` | Parses `/v1/responses` responses |
| Anthropic parser | `sparrow/tracing/parsers/anthropic_messages.py` | Parses `/v1/messages` responses (handles `message_start`/`message_delta` SSE events) |
| API routes | `sparrow/api/routes.py` | REST endpoints — traces CRUD, dashboard, archives, SSE stream |
| API schemas | `sparrow/api/schemas.py` | Pydantic response models for API serialization |
| Archiver | `sparrow/archive/archiver.py` | tar.gz archive create/import/list |
| Web UI app | `sparrow/web_ui.py` | FastAPI app setup — mounts static files, templates, API router |

### Storage & Configuration

| Item | Details |
|------|---------|
| Database | SQLite via SQLAlchemy async (`aiosqlite`), WAL mode, 5s busy timeout |
| Table | `traces` — indexed on `timestamp`, `path`, `status_code`, `model`, `duration_ms` |
| Body truncation | Request/response bodies truncated at `max_body_size` (default 1MB) |
| Config format | YAML (`config.yaml`), auto-generated from `config.example.yaml` if missing |
| Config sections | `proxy_port`, `ui_port`, `log_level`, `routes[]`, `storage`, `pricing[]`, `upstream_proxy`, `stream_timeout` |
| Route config | Each route: `name`, `prefix` (path matcher), `target_base_url` (upstream API base) |
| Upstream proxy | Supports HTTP/HTTPS/SOCKS5 with `no_proxy` bypass list and custom `_NoProxyTransport` |

---

## 4. Dependency Map

### Python (backend)

| Package | Purpose |
|---------|---------|
| `fastapi` | Async web framework for both proxy and Web UI apps |
| `uvicorn` | ASGI server — two instances for dual-port design |
| `httpx` | Async HTTP client for proxying requests to upstream APIs |
| `sqlalchemy[asyncio]` | ORM + async session management for SQLite |
| `aiosqlite` | Async SQLite driver |
| `pydantic` | Config validation (`AppConfig`), API response schemas |
| `pyyaml` | YAML config file parsing |
| `sse-starlette` | Server-Sent Events support for real-time trace push |
| `starlette` | Underlying framework (FastAPI dependency), used for `BackgroundTasks` |

### JavaScript (frontend)

| Library | Purpose |
|---------|---------|
| `Alpine.js` (CDN) | Lightweight reactive framework for SPA state management and DOM binding |
| `Tailwind CSS v4` | Utility-first CSS framework; compiled locally via standalone binary |

---

## 5. Current State & Limitations

### Bottlenecks

- **Single SQLite database** — concurrent writes from many simultaneous proxy requests may hit WAL checkpoint contention despite the 5s busy timeout
- **SSE fan-out** — `notify_new_trace()` iterates over all connected SSE queues in-process; does not scale beyond a single process
- **Full body storage** — request and response bodies are stored in full (up to `max_body_size`); large responses fill the database quickly

### Hardcoded values

- Default proxy port `8080` and UI port `8081` — set in `AppConfig` defaults but commonly left unchanged
- Default `max_body_size` = 1MB — not exposed in YAML config, only in code
- Parser route prefix matches are fixed at registration time in `__init__.py` — adding a new parser requires code changes

### Fragile logic

- **`stream: true` detection** — relies on JSON-parsing the request body to find the `stream` key; malformed or non-JSON bodies will default to non-streaming
- **Longest-prefix route matching** — overlapping route prefixes (e.g., `/v1` and `/v1/chat`) may cause unexpected routing if config is misordered
- **Anthropic SSE parsing** — handles `message_start`/`message_delta`/`message_stop` events but does not gracefully handle unexpected event types; may silently skip token counts
- **Archive import** — overwrites traces with matching IDs without conflict resolution
- **`TracingMiddleware`** — defined but effectively unused; all tracing happens inside `proxy_request()` directly
- **No authentication** — the Web UI API has no auth; anyone with network access to port 8081 can read all traces and manage archives
