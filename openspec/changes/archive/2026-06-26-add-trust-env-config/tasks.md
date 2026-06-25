## 1. Config Model

- [x] 1.1 Add `trust_env: bool | None = None` field to `UpstreamProxyConfig` in `sparrow/config.py`
- [x] 1.2 Add `resolved_trust_env` computed property to `UpstreamProxyConfig` that resolves `None` → `True` when no proxy fields set, `None` → `False` when any proxy field is set, explicit values pass through

## 2. Fix NameError Bug

- [x] 2.1 Fix `if https_pt` → `if https_proxy` on line 147 of `sparrow/proxy/router.py`

## 3. Client Builder

- [x] 3.1 Update `_build_proxy_client` in `sparrow/proxy/router.py` to use `proxy_config.resolved_trust_env` instead of hardcoded `trust_env=True`/`trust_env=False`
- [x] 3.2 When `resolved_trust_env` is `True` and no proxy fields are set, use the existing `trust_env=True` path (httpx reads env vars)
- [x] 3.3 When `resolved_trust_env` is `False` and no proxy fields are set, return `httpx.AsyncClient(trust_env=False)` — no proxy, no env vars
- [x] 3.4 When proxy fields are set with `resolved_trust_env=False`, use existing proxy config paths with `trust_env=False`
- [x] 3.5 When proxy fields are set with `resolved_trust_env=True`, use existing proxy config paths with `trust_env=True`

## 4. Config Documentation

- [x] 4.1 Add `trust_env` documentation to `config.example.yaml` with comments explaining the three-state behavior

## 5. Tests

- [x] 5.1 Add test for `resolved_trust_env` property: `None` with no proxy fields → `True`
- [x] 5.2 Add test for `resolved_trust_env` property: `None` with proxy fields → `False`
- [x] 5.3 Add test for `resolved_trust_env` property: explicit `True` → `True`
- [x] 5.4 Add test for `resolved_trust_env` property: explicit `False` → `False`
- [x] 5.5 Add test for `_build_proxy_client` with empty config and `resolved_trust_env=False` → client has `trust_env=False`
- [x] 5.6 Add test for `_build_proxy_client` with empty config and `resolved_trust_env=True` → client has `trust_env=True`
- [x] 5.7 Add test for different http/https proxies with no_proxy list (exercises the NameError fix)
