# SSL Verify Configuration

## Purpose

Control SSL certificate verification for upstream requests routed through an upstream proxy.

## Requirements

### Requirement: SSL verification configuration
The gateway SHALL support a `ssl_verify` boolean field in the `upstream_proxy` config section. When set to `false`, the gateway SHALL disable SSL certificate verification for all upstream requests. The default value SHALL be `true` to preserve existing secure behavior. When `ssl_verify` is `false`, the gateway SHALL emit a warning log at startup.

#### Scenario: SSL verification enabled by default
- **WHEN** the `upstream_proxy` section does not specify `ssl_verify`
- **THEN** the gateway SHALL verify SSL certificates for all upstream HTTPS requests

#### Scenario: SSL verification explicitly disabled
- **WHEN** the configuration contains `upstream_proxy: { ssl_verify: false }`
- **THEN** the gateway SHALL disable SSL certificate verification for all upstream requests and emit a startup warning

#### Scenario: SSL verification explicitly enabled
- **WHEN** the configuration contains `upstream_proxy: { ssl_verify: true }`
- **THEN** the gateway SHALL verify SSL certificates for all upstream HTTPS requests (same as default)

#### Scenario: SSL verify disabled with proxy configured
- **WHEN** the configuration contains `upstream_proxy: { https_proxy: "http://proxy.corp:8080", ssl_verify: false }`
- **THEN** the gateway SHALL route requests through the proxy AND disable SSL verification for the upstream connection
