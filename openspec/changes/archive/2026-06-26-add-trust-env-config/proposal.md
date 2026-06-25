## Why

When `upstream_proxy` is omitted or empty in config.yaml, the gateway silently reads proxy settings from system environment variables (HTTP_PROXY, HTTPS_PROXY, NO_PROXY) via httpx's `trust_env=True`. There is no way to explicitly disable this — users on machines with corporate proxy env vars get unexpected proxy behavior even when they want direct connections. Additionally, a NameError bug in `_build_proxy_client` crashes the gateway when different http/https proxy URLs are configured with a `no_proxy` list.

## What Changes

- Add `trust_env` field to `upstream_proxy` config section, allowing explicit control over whether environment variables are used as a proxy fallback
- Fix NameError in `_build_proxy_client` (`router.py:147`) where `https_pt` references itself before assignment — should be `if https_proxy`
- Default `trust_env` to `True` when the `upstream_proxy` section is absent (backward compatible), and `False` when any proxy field is explicitly set

## Capabilities

### New Capabilities

_None_

### Modified Capabilities

- `upstream-proxy-config`: Add `trust_env` field to the upstream proxy configuration, with smart defaults (absent section → True, explicit config → False, explicit override → as specified)

## Impact

- `sparrow/config.py` — add `trust_env` field to `UpstreamProxyConfig`
- `sparrow/proxy/router.py` — fix NameError, use `trust_env` from config in `_build_proxy_client`
- `config.example.yaml` — document `trust_env` option
- `tests/test_proxy_client.py` — add tests for `trust_env` behavior
