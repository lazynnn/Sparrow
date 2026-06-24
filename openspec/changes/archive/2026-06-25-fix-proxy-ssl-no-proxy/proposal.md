## Why

The current proxy implementation has two functional bugs: (1) there is no way to disable SSL certificate verification, making it impossible to use the gateway against upstream servers with self-signed or corporate CA certificates; (2) the `no_proxy` configuration is ignored at runtime — even when a target host matches a no-proxy pattern, the request is still sent through the proxy, defeating the purpose of `no_proxy`.

## What Changes

- Add `ssl_verify` boolean field to `UpstreamProxyConfig` (default `true`) so users can disable SSL verification when needed
- Fix the `_build_proxy_client` logic so that when `no_proxy` is configured and a request's target host matches a no-proxy pattern, the request bypasses the proxy entirely and connects directly
- Ensure `no_proxy` patterns support comma-separated values, domain suffixes (`.example.com`), exact hostnames, and CIDR notation (e.g., `10.0.0.0/8`)

## Capabilities

### New Capabilities

- `ssl-verify-config`: Allow users to disable SSL certificate verification for upstream requests via config

### Modified Capabilities

- `upstream-proxy-config`: Fix no_proxy enforcement so that matching hosts bypass the proxy at request time

## Impact

- **Config**: `UpstreamProxyConfig` gains a new `ssl_verify` field; existing configs are backward compatible (defaults to `true`)
- **Proxy router**: `_build_proxy_client` in `sparrow/proxy/router.py` must be refactored to evaluate no_proxy per-request rather than only at client construction time
- **Dependencies**: May need `ipaddress` stdlib for CIDR matching in no_proxy
