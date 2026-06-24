## MODIFIED Requirements

### Requirement: Upstream proxy configuration
The gateway SHALL support configuring upstream HTTP and HTTPS proxy URLs and a no-proxy list via the `upstream_proxy` section in config.yaml. The section SHALL contain optional fields: `http_proxy`, `https_proxy`, `no_proxy`, and `ssl_verify`. When `no_proxy` is configured, the gateway SHALL evaluate each request's target host against the no-proxy patterns and bypass the proxy for matching hosts. The no_proxy field SHALL support: exact hostnames, domain suffixes (patterns starting with `.`), and CIDR network ranges.

#### Scenario: Configure HTTP proxy only
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "http://proxy.corp:8080" }`
- **THEN** the gateway SHALL route all upstream HTTP requests through `http://proxy.corp:8080`

#### Scenario: Configure HTTPS proxy only
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080" }`
- **THEN** the gateway SHALL route all upstream HTTPS requests through `http://proxy.corp:8080`

#### Scenario: Configure both HTTP and HTTPS proxy
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "http://proxy.corp:8080", https_proxy: "http://proxy.corp:8443" }`
- **THEN** the gateway SHALL route upstream HTTP requests through the http_proxy URL and upstream HTTPS requests through the https_proxy URL

#### Scenario: Configure no-proxy list
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: "localhost,10.0.0.0/8,.internal" }`
- **THEN** the gateway SHALL bypass the proxy for hosts matching the no-proxy patterns

#### Scenario: No-proxy exact hostname match
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: "localhost" }` and a request targets `https://localhost/api`
- **THEN** the gateway SHALL connect directly to localhost without using the proxy

#### Scenario: No-proxy domain suffix match
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: ".internal" }` and a request targets `https://api.service.internal/v1`
- **THEN** the gateway SHALL connect directly to api.service.internal without using the proxy

#### Scenario: No-proxy CIDR match
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: "10.0.0.0/8" }` and a request targets `https://10.1.2.3/api`
- **THEN** the gateway SHALL connect directly to 10.1.2.3 without using the proxy

#### Scenario: No-proxy host does not match
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", no_proxy: "localhost,.internal" }` and a request targets `https://api.openai.com/v1/chat`
- **THEN** the gateway SHALL route the request through the proxy

#### Scenario: No proxy configuration (backward compatible)
- **WHEN** the `upstream_proxy` section is omitted or all its fields are empty
- **THEN** the gateway SHALL use httpx's default `trust_env=True` behavior, reading proxy settings from system environment variables

#### Scenario: Config takes precedence over env vars
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://my-proxy:3128" }` and the system also sets HTTPS_PROXY
- **THEN** the gateway SHALL use the configured `https_proxy` value, ignoring the system environment variable

### Requirement: Upstream proxy validation
The gateway SHALL validate upstream proxy configuration at startup. Invalid proxy URLs SHALL cause the gateway to exit with a descriptive error message.

#### Scenario: Invalid proxy URL
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "not-a-url" }`
- **THEN** the gateway SHALL fail to start and print a validation error identifying the invalid proxy URL

#### Scenario: Empty upstream_proxy section
- **WHEN** the configuration contains `upstream_proxy: {}`
- **THEN** the gateway SHALL start successfully with no proxy configured (same as omitting the section)
