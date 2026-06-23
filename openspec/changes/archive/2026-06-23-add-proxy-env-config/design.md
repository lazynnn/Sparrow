## Context

Sparrow is an LLM gateway that proxies requests to OpenAI-compatible APIs using `httpx.AsyncClient`. Currently, httpx's default `trust_env=True` silently reads system environment variables (HTTP_PROXY, HTTPS_PROXY, NO_PROXY) for upstream proxy configuration. This creates a debugging blind spot—users cannot see which proxy settings are active, and connection failures caused by misconfigured env vars are hard to trace.

## Goals / Non-Goals

**Goals:**
- Allow users to explicitly configure upstream proxy settings (http_proxy, https_proxy, no_proxy) in config.yaml
- Config values take precedence over system env vars when set
- Preserve existing `trust_env=True` behavior when no config values are provided (backward compatible)
- Make proxy configuration visible and auditable via the config file

**Non-Goals:**
- SOCKS proxy support (can be added later)
- Per-route proxy configuration (all routes share the same proxy)
- Proxy authentication (httpx handles this via URL-embedded credentials if needed)
- Web UI for proxy configuration

## Decisions

### Decision 1: Use httpx `proxy` parameter instead of environment variable injection

**Choice**: Pass proxy URL directly to `httpx.AsyncClient(proxy=...)` rather than setting os.environ at runtime.

**Rationale**: Setting env vars at runtime is a global side effect that can leak across threads and is hard to reason about. httpx's `proxy` parameter is explicit, scoped to the client instance, and well-documented. When `proxy` is set, httpx uses it regardless of `trust_env`, giving us clean precedence.

**Alternative considered**: Inject env vars into os.environ before creating the client. Rejected due to global scope and testability concerns.

### Decision 2: Single `upstream_proxy` config section with optional fields

**Choice**: Add an `upstream_proxy` section with optional `http_proxy`, `https_proxy`, and `no_proxy` fields, all defaulting to empty/None.

**Rationale**: Optional fields mean existing configs work unchanged. Users only add what they need. A dedicated section keeps proxy concerns grouped and discoverable.

**Alternative considered**: Flat top-level fields (e.g., `http_proxy: ...`). Rejected because it clutters the top-level namespace and doesn't scale if we add more proxy options later.

### Decision 3: Use httpx `proxy` for single proxy and `mounts` for split http/https

**Choice**: When only `http_proxy` or only `https_proxy` is set, use the `proxy` parameter. When both are set (or when `no_proxy` is needed), use httpx `mounts` with separate proxy configurations per scheme.

**Rationale**: httpx supports a simple `proxy` string for a single proxy, but split http/https and no_proxy require the more explicit mounts API. Using mounts when needed gives full control without overcomplicating the common single-proxy case.

**Alternative considered**: Always use mounts. Rejected as overly complex for the common case of a single corporate proxy.

### Decision 4: `no_proxy` as comma-separated string

**Choice**: Store `no_proxy` as a comma-separated string (matching the standard env var format) and parse it for httpx mounts.

**Rationale**: Familiar format for users already accustomed to NO_PROXY env vars. No need to invent a YAML list format for something that maps directly to an existing standard.

## Risks / Trade-offs

- **[Risk] httpx proxy API changes**: httpx's proxy configuration API has evolved across versions. → Mitigation: Pin the current approach to httpx's stable `proxy` parameter and `mounts` API, which are documented as of httpx 0.27+.
- **[Risk] Users expect env vars to still work**: Some users may set HTTP_PROXY and not realize config takes precedence. → Mitigation: Document the precedence clearly in config.example.yaml comments.
- **[Trade-off] No per-route proxy**: All routes share the same proxy. This simplifies the config but may not cover all corporate network topologies. → Can be extended later with a per-route override if needed.
