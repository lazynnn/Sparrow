# Upstream Proxy Configuration

## Purpose

Configure upstream HTTP/HTTPS proxy and no-proxy lists in config.yaml, with explicit precedence over system environment variables.

## Requirements

### Requirement: Upstream proxy configuration
The gateway SHALL support configuring upstream HTTP and HTTPS proxy URLs and a no-proxy list via the `upstream_proxy` section in config.yaml. The section SHALL contain optional fields: `http_proxy`, `https_proxy`, and `no_proxy`.

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
