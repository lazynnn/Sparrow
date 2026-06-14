## 1. Project Setup

- [ ] 1.1 Create Python project structure with `pyproject.toml` (FastAPI, httpx, SQLAlchemy, aiosqlite, PyYAML, uvicorn dependencies)
- [ ] 1.2 Create `sparrow/__init__.py` and `sparrow/__main__.py` with CLI entry point
- [ ] 1.3 Create `config.example.yaml` with all configuration options documented
- [ ] 1.4 Implement `sparrow/config.py` with Pydantic models for config validation and YAML loading
- [ ] 1.5 Download standalone Tailwind CLI binary and Alpine.js, set up `sparrow/web/static/` directory structure
- [ ] 1.6 Create Tailwind source CSS (`sparrow/web/static/css/input.css`) and build script

## 2. Database Layer

- [ ] 2.1 Implement `sparrow/models.py` with SQLAlchemy Trace model (all fields: request/response data, timing, tokens, cost, model name, status)
- [ ] 2.2 Implement `sparrow/database.py` with async engine setup, WAL mode, session factory, and table creation
- [ ] 2.3 Add database indexes on timestamp, request_path, status_code, model_name, and duration columns
- [ ] 2.4 Implement max body size truncation logic with `[TRUNCATED]` marker

## 3. Transparent Proxy

- [ ] 3.1 Implement `sparrow/proxy/router.py` with FastAPI catch-all route that forwards requests to target URL
- [ ] 3.2 Implement route prefix matching to select target URL from configuration
- [ ] 3.3 Implement header forwarding (excluding hop-by-hop headers) and API key passthrough
- [ ] 3.4 Implement `sparrow/proxy/streaming.py` with SSE chunk forwarding and accumulation
- [ ] 3.5 Implement `sparrow/proxy/middleware.py` with request/response tracing middleware
- [ ] 3.6 Add latency measurement: total duration for non-streaming, TTFB + duration for streaming
- [ ] 3.7 Add streaming timeout handling and error mid-stream handling
- [ ] 3.8 Implement async background task for trace DB writes (non-blocking)

## 4. Cost Tracking

- [ ] 4.1 Implement `sparrow/tracing/cost.py` with cost calculation from token counts and pricing table
- [ ] 4.2 Implement `sparrow/tracing/tracer.py` with token usage extraction from non-streaming response JSON
- [ ] 4.3 Implement token usage extraction from accumulated SSE chunks (parse final chunk's usage field)
- [ ] 4.4 Implement model name extraction from request body
- [ ] 4.5 Handle missing usage data and unknown model pricing (store null)

## 5. Archive System

- [ ] 5.1 Implement `sparrow/archive/archiver.py` with trace export to JSONL format
- [ ] 5.2 Implement tar.gz archive creation with metadata.json and traces.jsonl
- [ ] 5.3 Implement trace deletion from active DB after successful archive
- [ ] 5.4 Implement archive re-import (read JSONL, INSERT OR IGNORE into SQLite)

## 6. REST API

- [ ] 6.1 Implement `sparrow/api/schemas.py` with Pydantic response models for traces, filters, dashboard
- [ ] 6.2 Implement `sparrow/api/routes.py` with trace list endpoint (paginated, filtered, sorted)
- [ ] 6.3 Implement trace detail endpoint (single trace by ID)
- [ ] 6.4 Implement dashboard endpoint (aggregated token usage and cost metrics)
- [ ] 6.5 Implement archive/list/create/import endpoints
- [ ] 6.6 Implement SSE endpoint for real-time trace streaming to web UI

## 7. Web UI

- [ ] 7.1 Implement `sparrow/web_ui.py` with FastAPI app serving static files and HTML template
- [ ] 7.2 Build HTML template (`sparrow/web/templates/index.html`) with Tailwind + Alpine.js layout
- [ ] 7.3 Implement trace list component with pagination
- [ ] 7.4 Implement filter controls (model, status, date range, duration)
- [ ] 7.5 Implement trace detail view with JSON pretty-printing and syntax highlighting
- [ ] 7.6 Implement token usage and cost dashboard
- [ ] 7.7 Implement dark mode (default) with light mode toggle and localStorage persistence
- [ ] 7.8 Implement real-time trace list updates via SSE connection
- [ ] 7.9 Implement `sparrow/web/static/js/app.js` with Alpine.js application logic
- [ ] 7.10 Build and verify Tailwind CSS output locally

## 8. Integration & Startup

- [ ] 8.1 Implement CLI startup command that launches both proxy and web UI servers
- [ ] 8.2 Implement config file auto-creation with defaults if missing
- [ ] 8.3 Wire all components together: proxy → tracer → database, API → database, web UI → API
- [ ] 8.4 Add graceful shutdown handling

## 9. Testing

- [ ] 9.1 Write unit tests for cost calculation logic (`tests/test_tracing.py`)
- [ ] 9.2 Write unit tests for token extraction from streaming and non-streaming responses
- [ ] 9.3 Write integration tests for proxy forwarding with mock target (`tests/test_proxy.py`)
- [ ] 9.4 Write tests for archive creation and re-import (`tests/test_archive.py`)
- [ ] 9.5 Write tests for config validation and defaults
