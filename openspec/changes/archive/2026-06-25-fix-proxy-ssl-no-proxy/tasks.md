## 1. Config changes

- [x] 1.1 Add `ssl_verify: bool = True` field to `UpstreamProxyConfig` in `sparrow/config.py`
- [x] 1.2 Update `config.example.yaml` and `_DEFAULT_CONFIG` to include `ssl_verify` field with default value

## 2. no_proxy matching utility

- [x] 2.1 Create `_should_bypass_proxy(host: str, no_proxy: str) -> bool` helper in `sparrow/proxy/router.py` that supports exact hostname, domain suffix, and CIDR matching
- [x] 2.2 Add unit tests for `_should_bypass_proxy` covering: exact match, domain suffix match, CIDR match, no match, multiple patterns, whitespace handling

## 3. Custom transport for per-request no_proxy

- [x] 3.1 Create `_NoProxyTransport` class (extends `httpx.AsyncBaseTransport`) in `sparrow/proxy/router.py` that holds a proxy transport and a direct transport, and delegates based on `_should_bypass_proxy`
- [x] 3.2 Refactor `_build_proxy_client` to use `_NoProxyTransport` when `no_proxy` is configured, instead of using simple scheme-based mounts

## 4. SSL verify support

- [x] 4.1 Pass `verify=proxy_config.ssl_verify` to all `httpx.AsyncClient` and `httpx.AsyncHTTPTransport` constructions in `_build_proxy_client`
- [x] 4.2 Add startup warning log when `ssl_verify: false` is configured in `sparrow/__main__.py` or the proxy app creation

## 5. Integration testing

- [x] 5.1 Test that `ssl_verify: false` allows requests to self-signed cert endpoints
- [x] 5.2 Test that `no_proxy` patterns correctly bypass proxy for matching hosts
- [x] 5.3 Test that non-matching hosts still use the proxy when `no_proxy` is set
