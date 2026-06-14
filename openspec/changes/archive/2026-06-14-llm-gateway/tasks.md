## 1. Project Setup

- [x] 1.1 Create Python project structure with `pyproject.toml` (FastAPI, httpx, SQLAlchemy, aiosqlite, PyYAML, uvicorn dependencies)
- [x] 1.2 Create `sparrow/__init__.py` and `sparrow/__main__.py` with CLI entry point
- [x] 1.3 Create `config.example.yaml` with all configuration options documented
- [x] 1.4 Implement `sparrow/config.py` with Pydantic models for config validation and YAML loading
- [x] 1.5 Download standalone Tailwind CLI binary and Alpine.js, set up `sparrow/web/static/` directory structure
- [x] 1.6 Create Tailwind source CSS (`sparrow/web/static/css/input.css`) and build script

## 2. Database Layer

- [x] 2.1 Implement `sparrow/models.py` with SQLAlchemy Trace model (all fields: request/response data, timing, tokens, cost, model name, status)
- [x] 2.2 Implement `sparrow/database.py` with async engine setup, WAL mode, session factory, and table creation
- [x] 2.3 Add database indexes on timestamp, request_path, status_code, model_name, and duration columns
- [x] 2.4 Implement max body size truncation logic with `[TRUNCATED]` marker

## 3. Transparent Proxy

- [x] 3.1 Implement `sparrow/proxy/router.py` with FastAPI catch-all route that forwards requests to target URL
- [x] 3.2 Implement route prefix matching to select target URL from configuration
- [x] 3.3 Implement header forwarding (excluding hop-by-hop headers) and API key passthrough
- [x] 3.4 Implement `sparrow/proxy/streaming.py` with SSE chunk forwarding and accumulation
- [x] 3.5 Implement `sparrow/proxy/middleware.py` with request/response tracing middleware
- [x] 3.6 Add latency measurement: total duration for non-streaming, TTFB + duration for streaming
- [x] 3.7 Add streaming timeout handling and error mid-stream handling
- [x] 3.8 Implement async background task for trace DB writes (non-blocking)

## 4. Cost Tracking

- [x] 4.1 Implement `sparrow/tracing/cost.py` with cost calculation from token counts and pricing table
- [x] 4.2 Implement `sparrow/tracing/tracer.py` with token usage extraction from non-streaming response JSON
- [x] 4.3 Implement token usage extraction from accumulated SSE chunks (parse final chunk's usage field)
- [x] 4.4 Implement model name extraction from request body
- [x] 4.5 Handle missing usage data and unknown model pricing (store null)

## 5. Archive System

- [x] 5.1 Implement `sparrow/archive/archiver.py` with trace export to JSONL format
- [x] 5.2 Implement tar.gz archive creation with metadata.json and traces.jsonl
- [x] 5.3 Implement trace deletion from active DB after successful archive
- [x] 5.4 Implement archive re-import (read JSONL, INSERT OR IGNORE into SQLite)

## 6. REST API

- [x] 6.1 Implement `sparrow/api/schemas.py` with Pydantic response models for traces, filters, dashboard
- [x] 6.2 Implement `sparrow/api/routes.py` with trace list endpoint (paginated, filtered, sorted)
- [x] 6.3 Implement trace detail endpoint (single trace by ID)
- [x] 6.4 Implement dashboard endpoint (aggregated token usage and cost metrics)
- [x] 6.5 Implement archive/list/create/import endpoints
- [x] 6.6 Implement SSE endpoint for real-time trace streaming to web UI

## 7. Web UI

- [x] 7.1 Implement `sparrow/web_ui.py` with FastAPI app serving static files and HTML template
- [x] 7.2 Build HTML template (`sparrow/web/templates/index.html`) with Tailwind + Alpine.js layout
- [x] 7.3 Implement trace list component with pagination
- [x] 7.4 Implement filter controls (model, status, date range, duration)
- [x] 7.5 Implement trace detail view with JSON pretty-printing and syntax highlighting
- [x] 7.6 Implement token usage and cost dashboard
- [x] 7.7 Implement dark mode (default) with light mode toggle and localStorage persistence
- [x] 7.8 Implement real-time trace list updates via SSE connection
- [x] 7.9 Implement `sparrow/web/static/js/app.js` with Alpine.js application logic
- [x] 7.10 Build and verify Tailwind CSS output locally

## 8. Integration & Startup

- [x] 8.1 Implement CLI startup command that launches both proxy and web UI servers
- [x] 8.2 Implement config file auto-creation with defaults if missing
- [x] 8.3 Wire all components together: proxy → tracer → database, API → database, web UI → API
- [x] 8.4 Add graceful shutdown handling

## 9. Testing

- [x] 9.1 Write unit tests for cost calculation logic (`tests/test_tracing.py`)
- [x] 9.2 Write unit tests for token extraction from streaming and non-streaming responses
- [x] 9.3 Write integration tests for proxy forwarding with mock target (`tests/test_proxy.py`)
- [x] 9.4 Write tests for archive creation and re-import (`tests/test_archive.py`)
- [x] 9.5 Write tests for config validation and defaults
