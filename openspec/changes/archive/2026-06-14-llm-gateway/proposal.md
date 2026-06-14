## Why

Existing LLM observability tools like Phoenix are too heavy, bundling evaluation, playground, and dataset features that aren't needed. There's no lightweight, self-hosted Python gateway that simply traces LLM API calls, provides a clean log viewer, and transparently proxies to any OpenAI-compatible endpoint — while also tracking token usage and cost.

## What Changes

- Build a lightweight Python LLM gateway (Sparrow) that acts as a transparent reverse proxy to OpenAI-compatible API endpoints
- Intercept and store all requests/responses (headers, body, timing, token usage, cost) in SQLite
- Support both regular request/response and SSE streaming proxying with full trace capture
- Provide a web UI for browsing, filtering, and inspecting request logs with token/cost dashboard
- Support archiving old traces to compressed `.tar.gz` files to keep the active DB small without data loss
- Include a configurable model pricing table for automatic cost calculation from token usage
- Serve Tailwind CSS locally (no CDN dependency) using the standalone Tailwind CLI

## Capabilities

### New Capabilities
- `transparent-proxy`: Reverse proxy to OpenAI-compatible endpoints with SSE streaming support, preserving all headers, status codes, and timing
- `trace-storage`: SQLite-backed trace storage for requests, responses, timing, token usage, and cost; archive old traces to `.tar.gz`
- `log-viewer`: Web UI for browsing, filtering, and inspecting LLM request logs with real-time streaming and dark mode
- `cost-tracking`: Token usage extraction from response JSON and cost calculation based on configurable per-model pricing
- `gateway-config`: YAML-based configuration for target API URLs, route definitions, model pricing, and storage settings

### Modified Capabilities
<!-- No existing capabilities to modify -->

## Impact

- New Python project with FastAPI, httpx, SQLAlchemy, aiosqlite, PyYAML dependencies
- Local Tailwind CLI binary (~20MB) for building CSS assets
- SQLite database file for trace storage
- YAML configuration file for gateway setup
- Web UI served on a separate port or path from the proxy endpoint
