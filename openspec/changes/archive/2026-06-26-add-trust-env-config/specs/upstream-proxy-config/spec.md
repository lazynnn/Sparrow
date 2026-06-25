## MODIFIED Requirements

### Requirement: Upstream proxy configuration
The gateway SHALL support configuring upstream HTTP and HTTPS proxy URLs, a no-proxy list, and a `trust_env` flag via the `upstream_proxy` section in config.yaml. The section SHALL contain optional fields: `http_proxy`, `https_proxy`, `no_proxy`, `ssl_verify`, and `trust_env`. When `no_proxy` is configured, the gateway SHALL evaluate each request's target host against the no-proxy patterns and bypass the proxy for matching hosts. The no_proxy field SHALL support: exact hostnames, domain suffixes (patterns starting with `.`), and CIDR network ranges. The `trust_env` field SHALL control whether httpx reads proxy settings from system environment variables, with the following resolution: when `trust_env` is explicitly set, use that value; when `trust_env` is `None` (not set) and any proxy field (`http_proxy`, `https_proxy`, `no_proxy`) is configured, resolve to `False`; when `trust_env` is `None` and no proxy fields are configured, resolve to `True`.

#### Scenario: Configure HTTP proxy only
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "http://proxy.corp:8080" }`
- **THEN** the gateway SHALL route all upstream HTTP requests through `http://proxy.corp:8080` and SHALL NOT read proxy settings from environment variables

#### Scenario: Configure HTTPS proxy only
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080" }`
- **THEN** the gateway SHALL route all upstream HTTPS requests through `http://proxy.corp:8080` and SHALL NOT read proxy settings from environment variables

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

#### Scenario: No proxy configuration with trust_env default
- **WHEN** the `upstream_proxy` section is omitted or all its fields are empty and `trust_env` is not explicitly set
- **THEN** the gateway SHALL use httpx's `trust_env=True` behavior, reading proxy settings from system environment variables

#### Scenario: Empty upstream_proxy section disables env vars
- **WHEN** the configuration contains `upstream_proxy: {}` and `trust_env` is not explicitly set
- **THEN** the gateway SHALL NOT read proxy settings from system environment variables (resolved trust_env is False)

#### Scenario: Explicit trust_env true preserves env var reading
- **WHEN** the configuration contains `upstream_proxy: { trust_env: true }` and system environment variables set HTTP_PROXY
- **THEN** the gateway SHALL read proxy settings from environment variables

#### Scenario: Explicit trust_env false disables env vars regardless of other fields
- **WHEN** the configuration contains `upstream_proxy: { trust_env: false }` and no proxy URLs are configured
- **THEN** the gateway SHALL NOT read proxy settings from system environment variables and SHALL connect directly to all targets

#### Scenario: Config takes precedence over env vars
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://my-proxy:3128" }` and the system also sets HTTPS_PROXY
- **THEN** the gateway SHALL use the configured `https_proxy` value, ignoring the system environment variable

#### Scenario: Different HTTP and HTTPS proxies with no_proxy list
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "http://proxy-http:8080", https_proxy: "http://proxy-https:8443", no_proxy: "localhost" }` and a request targets `https://localhost/api`
- **THEN** the gateway SHALL connect directly to localhost without using the proxy

### Requirement: Upstream proxy validation
The gateway SHALL validate upstream proxy configuration at startup. Invalid proxy URLs SHALL cause the gateway to exit with a descriptive error message.

#### Scenario: Invalid proxy URL
- **WHEN** the configuration contains `upstream_proxy: { http_proxy: "not-a-url" }`
- **THEN** the gateway SHALL fail to start and print a validation error identifying the invalid proxy URL

#### Scenario: Empty upstream_proxy section
- **WHEN** the configuration contains `upstream_proxy: {}`
- **THEN** the gateway SHALL start successfully with no proxy configured and SHALL NOT read proxy settings from environment variables

## ADDED Requirements

### Requirement: trust_env configuration
The gateway SHALL support a `trust_env` field in the `upstream_proxy` config section. The field SHALL accept `true`, `false`, or be omitted. When omitted, the resolved value SHALL be `True` if no other proxy fields are configured, and `False` if any proxy field is configured. The resolved value SHALL be passed as the `trust_env` parameter to the httpx `AsyncClient`.

#### Scenario: trust_env omitted with no proxy fields
- **WHEN** the `upstream_proxy` section is present with no proxy fields and `trust_env` is not set
- **THEN** the resolved trust_env SHALL be True

#### Scenario: trust_env omitted with proxy fields
- **WHEN** the `upstream_proxy` section contains `https_proxy: "http://proxy:8080"` and `trust_env` is not set
- **THEN** the resolved trust_env SHALL be False

#### Scenario: trust_env explicitly set to true
- **WHEN** the configuration contains `upstream_proxy: { trust_env: true }`
- **THEN** the resolved trust_env SHALL be True regardless of other fields

#### Scenario: trust_env explicitly set to false
- **WHEN** the configuration contains `upstream_proxy: { trust_env: false }`
- **THEN** the resolved trust_env SHALL be False regardless of other fields
