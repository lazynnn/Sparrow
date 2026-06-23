## Why

When Sparrow runs behind a corporate proxy, the gateway silently relies on system environment variables (HTTP_PROXY, HTTPS_PROXY, NO_PROXY) via httpx's `trust_env=True` default. This makes it difficult to diagnose network issues—there is no visible record of which proxy settings are active, and misconfigured or missing system env vars lead to opaque connection failures. Explicit proxy configuration in config.yaml gives users direct control and visibility.

## What Changes

- Add an `upstream_proxy` section to config.yaml with fields for `http_proxy`, `https_proxy`, and `no_proxy`
- Pass configured proxy values to the `httpx.AsyncClient` used by the proxy router
- When config values are set, they take precedence over system environment variables; when omitted, the existing `trust_env=True` behavior is preserved
- Update config.example.yaml and default config to document the new section

## Capabilities

### New Capabilities
- `upstream-proxy-config`: Configure upstream HTTP/HTTPS proxy and no-proxy lists in config.yaml, with explicit precedence over system env vars

### Modified Capabilities
- `gateway-config`: Add upstream_proxy section to the configuration schema and validation model
- `transparent-proxy`: Apply configured proxy settings to the httpx.AsyncClient used for forwarding requests

## Impact

- `sparrow/config.py`: Add `UpstreamProxyConfig` model and `upstream_proxy` field to `AppConfig`
- `sparrow/proxy/router.py`: Pass proxy config to `httpx.AsyncClient` constructor
- `config.yaml` / `config.example.yaml`: Add `upstream_proxy` section with documentation
- Default config string in `config.py`: Add `upstream_proxy` defaults
