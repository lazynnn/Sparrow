## Context

Sparrow is an LLM gateway that proxies requests to upstream API endpoints. The existing `UpstreamProxyConfig` in `sparrow/config.py` supports `http_proxy`, `https_proxy`, and `no_proxy` fields. The `_build_proxy_client` function in `sparrow/proxy/router.py` constructs an `httpx.AsyncClient` based on these settings.

Two problems exist:

1. **No SSL verify option**: `httpx.AsyncClient` defaults to `verify=True`. Users behind corporate proxies with self-signed CAs or testing against internal endpoints with untrusted certs cannot disable verification. There is no config field to control this.

2. **no_proxy not enforced at request time**: When `no_proxy` is set, `_build_proxy_client` falls into the mounts path (lines 82–99 of `router.py`). The mounts use `httpx.AsyncHTTPTransport(proxy=...)` for `http://` and `https://` schemes unconditionally — there is no logic to check whether a specific request's target host matches a no-proxy pattern. httpx's mount system matches by URL scheme only, not by host, so no_proxy patterns are never evaluated.

## Goals / Non-Goals

**Goals:**
- Allow users to disable SSL verification via `ssl_verify: false` in `upstream_proxy` config
- Enforce `no_proxy` patterns at request time so that matching hosts bypass the proxy
- Support standard no_proxy pattern formats: exact hostname, domain suffix (`.example.com`), and CIDR (`10.0.0.0/8`)
- Maintain backward compatibility — existing configs work unchanged

**Non-Goals:**
- No changes to the transparent proxy behavior (request/response passthrough stays unchanged)
- No changes to proxy authentication or SOCKS support
- Not adding per-route or per-target SSL verify overrides
- Not implementing WPAD or PAC-based proxy discovery

## Decisions

### Decision 1: Add `ssl_verify` field to `UpstreamProxyConfig`

Add `ssl_verify: bool = True` to `UpstreamProxyConfig`. Pass `verify=ssl_verify` to every `httpx.AsyncClient` and `httpx.AsyncHTTPTransport` construction in `_build_proxy_client`.

**Rationale**: This is the simplest and most standard approach. httpx natively supports the `verify` parameter (accepts `bool` or path to CA bundle). Defaulting to `True` preserves existing behavior.

**Alternative considered**: A separate top-level `tls` config section — rejected as over-engineering for a single boolean.

### Decision 2: Per-request no_proxy matching via custom transport

Instead of relying on httpx mounts (which only match by scheme), implement a custom `httpx.AsyncBaseTransport` that wraps the proxy transport and a direct transport. On each request, it checks the target host against no_proxy patterns and routes to the direct transport if matched, otherwise to the proxy transport.

**Rationale**: httpx's mount system is scheme-based only (`http://`, `https://`). There is no built-in way to do host-based routing. A custom transport gives full control over per-request proxy decisions while keeping the httpx client API unchanged.

**Alternative considered**: Creating two clients (one with proxy, one without) and selecting per request — rejected because it doubles connection pools and makes client lifecycle management harder.

### Decision 3: no_proxy pattern parsing

Implement a helper function `_should_bypass_proxy(host: str, no_proxy: str) -> bool` that:
- Splits `no_proxy` by commas
- Matches exact hostnames (e.g., `localhost`)
- Matches domain suffixes with leading dot (e.g., `.internal` matches `host.internal`)
- Matches CIDR ranges using `ipaddress` stdlib (e.g., `10.0.0.0/8`)
- Strips whitespace from each pattern

**Rationale**: This mirrors the behavior of standard tools (curl, wget) and Python's `urllib` no_proxy handling, while adding CIDR support which is common in corporate environments.

### Decision 4: When no_proxy is set, always use the custom transport

When `no_proxy` is configured (even if `same_proxy` is true), use the custom transport approach instead of the simple `proxy=` shortcut. This ensures no_proxy is actually evaluated.

## Risks / Trade-offs

- **[Custom transport complexity]** → The custom transport adds a thin layer over httpx's built-in transport. Mitigation: the wrapper is small (~40 lines) and delegates entirely to httpx for actual HTTP; it only decides which underlying transport to call.

- **[SSL verify=false security]** → Disabling SSL verification exposes requests to MITM attacks. Mitigation: default is `True`; users must explicitly set `ssl_verify: false`. A startup log warning is emitted when disabled.

- **[CIDR matching only works for IP addresses]** → If the target URL uses a hostname (not IP), CIDR patterns won't match. Mitigation: this is standard behavior matching curl/wget; no DNS resolution is performed for no_proxy matching (avoids latency and security issues).
