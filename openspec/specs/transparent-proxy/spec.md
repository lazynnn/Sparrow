# Transparent Proxy

## Purpose

Act as a transparent reverse proxy to OpenAI-compatible API endpoints, forwarding requests unchanged while supporting SSE streaming, route-based target selection, and latency measurement.

## Requirements

### Requirement: Transparent reverse proxy
The gateway SHALL act as a transparent reverse proxy to OpenAI-compatible API endpoints. All HTTP methods, headers, query parameters, and request bodies SHALL be forwarded unchanged to the target URL. Response status codes, headers, and bodies SHALL be returned to the client unchanged. When upstream proxy is configured, requests SHALL be routed through the specified proxy.

#### Scenario: Proxy a chat completion request
- **WHEN** a client sends a POST request to the gateway with path `/v1/chat/completions` and a JSON body
- **THEN** the gateway forwards the request to the configured target API base URL with the same path, method, headers, and body, and returns the target's response to the client unchanged

#### Scenario: Proxy preserves HTTP method and headers
- **WHEN** a client sends a request with any HTTP method (GET, POST, PUT, DELETE, PATCH) and custom headers
- **THEN** the gateway forwards the request with the identical method and all headers (excluding hop-by-hop headers) to the target

#### Scenario: Proxy returns target error responses
- **WHEN** the target API returns an error (4xx or 5xx status code)
- **THEN** the gateway SHALL return the exact same status code, headers, and body to the client

#### Scenario: Proxy request through configured upstream proxy
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080" }` and a client sends a request to an HTTPS target
- **THEN** the gateway SHALL forward the request through `http://proxy.corp:8080` to reach the target

#### Scenario: Proxy request bypasses proxy for no-proxy host
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: "localhost,.internal" }` and a client sends a request to a host matching a no-proxy pattern
- **THEN** the gateway SHALL connect directly to the target without using the proxy

### Requirement: SSE streaming proxy
The gateway SHALL support Server-Sent Events (SSE) streaming. When a request is made with `stream: true`, the gateway SHALL forward chunks to the client in real-time while accumulating the full response for tracing.

#### Scenario: Streaming chat completion
- **WHEN** a client sends a POST to `/v1/chat/completions` with `"stream": true` in the body
- **THEN** the gateway opens a streaming connection to the target, forwards each SSE chunk to the client immediately, and accumulates all chunks for the trace record

#### Scenario: Streaming error mid-stream
- **WHEN** the target API returns an error after some SSE chunks have been sent
- **THEN** the gateway SHALL forward the error to the client and record the partial trace with an error status

#### Scenario: Streaming connection timeout
- **WHEN** the streaming connection to the target is idle for longer than the configured timeout
- **THEN** the gateway SHALL close the connection and record the trace with a timeout status

### Requirement: Route-based target configuration
The gateway SHALL support configuring different target URLs per route prefix. Requests matching a route prefix SHALL be proxied to the corresponding target.

#### Scenario: Multiple target APIs
- **WHEN** the gateway is configured with route `/v1/openai` targeting `https://api.openai.com/v1` and route `/v1/azure` targeting `https://myresource.openai.azure.com/v1`
- **THEN** requests to `/v1/openai/chat/completions` SHALL be proxied to `https://api.openai.com/v1/chat/completions` and requests to `/v1/azure/chat/completions` SHALL be proxied to `https://myresource.openai.azure.com/v1/chat/completions`

### Requirement: API key passthrough
The gateway SHALL forward the client's Authorization header to the target API without modification. The gateway SHALL NOT require its own API key configuration for proxying.

#### Scenario: Forward bearer token
- **WHEN** a client sends a request with `Authorization: Bearer sk-xxx` header
- **THEN** the gateway SHALL forward the same header to the target API

### Requirement: Proxy latency measurement
The gateway SHALL measure and record the total proxy latency (time from receiving the request to sending the complete response) for each request.

#### Scenario: Record latency for non-streaming request
- **WHEN** a non-streaming request is proxied
- **THEN** the trace SHALL include the total round-trip latency in milliseconds

#### Scenario: Record latency for streaming request
- **WHEN** a streaming request is proxied
- **THEN** the trace SHALL include the time-to-first-byte (TTFB) and total stream duration in milliseconds
