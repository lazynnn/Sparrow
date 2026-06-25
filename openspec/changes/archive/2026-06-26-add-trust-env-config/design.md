## Context

Sparrow is an LLM gateway that proxies requests to upstream API endpoints. The `upstream_proxy` config section controls how the gateway routes outbound requests through an HTTP proxy. Currently, when no proxy fields are set, the gateway falls back to httpx's `trust_env=True`, which silently reads `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` from the process environment. There is no way for users to explicitly disable this fallback.

Additionally, `router.py:147` has a NameError (`if https_pt` instead of `if https_proxy`) that crashes the gateway when different http/https proxy URLs are configured alongside a `no_proxy` list.

## Goals / Non-Goals

**Goals:**
- Give users explicit control over whether environment variables influence proxy behavior
- Maintain backward compatibility (absent config still reads env vars)
- Fix the NameError in `_build_proxy_client`

**Non-Goals:**
- Rewriting or simplifying the full `_build_proxy_client` logic beyond the bug fix
- Supporting per-route proxy configuration
- Adding proxy authentication configuration

## Decisions

### Decision 1: Add `trust_env` as `bool | None` with three-state semantics

`trust_env: bool | None = None` in `UpstreamProxyConfig`:

| Config State | Resolved `trust_env` | Behavior |
|---|---|---|
| Section absent | `True` | httpx reads env vars (backward compat) |
| Section present, no proxy fields | `False` | No proxy, no env vars |
| Section present, proxy fields set | `False` | YAML proxy values only |
| `trust_env: true` explicitly | `True` | httpx reads env vars |
| `trust_env: false` explicitly | `False` | No env var reading |

**Alternative considered:** Two-state `bool` defaulting to `True`. Rejected because an empty `upstream_proxy: {}` would still leak env vars, which is the core user complaint.

**Alternative considered:** Separate `disable_env_proxy: bool`. Rejected because `trust_env` matches the httpx parameter name directly, reducing cognitive overhead.

### Decision 2: Resolve `trust_env` at config load time, not at client build time

A `resolved_trust_env` computed property on `UpstreamProxyConfig` will resolve the three-state value once. `_build_proxy_client` reads this property. This keeps the resolution logic in one place and keeps `_build_proxy_client` simple.

### Decision 3: Fix NameError inline, no refactor

The `https_pt` → `https_proxy` fix is a one-line typo correction. No broader restructuring of `_build_proxy_client`.

## Risks / Trade-offs

- **[Behavior change]** Users with `upstream_proxy: {}` in their config who rely on env vars will lose that behavior → Mitigated: this is the desired fix; the old behavior was a bug (unintentional env var leakage). Document in changelog.
- **[Three-state confusion]** `None` vs `True` vs `False` may confuse contributors → Mitigated: clear comments and the computed property make resolution explicit.
