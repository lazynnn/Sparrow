## MODIFIED Requirements

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
