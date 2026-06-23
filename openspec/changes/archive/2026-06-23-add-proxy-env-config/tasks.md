## 1. Config Model

- [x] 1.1 Add `UpstreamProxyConfig` Pydantic model to `sparrow/config.py` with optional fields `http_proxy`, `https_proxy`, `no_proxy` (all `str | None = None`) and URL validation via Pydantic
- [x] 1.2 Add `upstream_proxy` field to `AppConfig` with default factory producing an empty `UpstreamProxyConfig`
- [x] 1.3 Update `_DEFAULT_CONFIG` string in `sparrow/config.py` to include `upstream_proxy` section with commented-out examples

## 2. Proxy Client Setup

- [x] 2.1 Add helper function to `sparrow/proxy/router.py` that builds an `httpx.AsyncClient` with proxy configuration from `UpstreamProxyConfig` (use `proxy` parameter for single proxy, `mounts` for split http/https or no_proxy)
- [x] 2.2 Replace the existing `httpx.AsyncClient(...)` call in `create_proxy_app` with the new helper function
- [x] 2.3 When no proxy is configured, ensure `trust_env=True` remains the default for backward compatibility

## 3. Example Config

- [x] 3.1 Update `config.example.yaml` to include the `upstream_proxy` section with documented comments explaining each field and precedence over env vars

## 4. Tests

- [x] 4.1 Add unit tests for `UpstreamProxyConfig` validation (valid URLs, invalid URLs, empty fields)
- [x] 4.2 Add unit tests for proxy client construction (single proxy, split http/https, no_proxy, no config)
- [x] 4.3 Add integration test verifying proxied requests use the configured upstream proxy
- [x] 4.4 Add integration test verifying no_proxy bypass works correctly
