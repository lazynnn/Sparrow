# Gateway Configuration

## Purpose

Define the YAML-based configuration system for the LLM gateway, covering server ports, route mapping, storage, pricing, upstream proxy, and validation.

## Requirements

### Requirement: YAML configuration file
The gateway SHALL read its configuration from a YAML file. The configuration SHALL include: server ports, target API base URLs with route prefixes, model pricing table, storage settings, logging level, and upstream proxy settings.

#### Scenario: Load configuration from file
- **WHEN** the gateway starts
- **THEN** it SHALL read the configuration from the specified YAML file and apply all settings including upstream proxy if present

#### Scenario: Missing configuration file
- **WHEN** the specified configuration file does not exist
- **THEN** the gateway SHALL create a default configuration file at the specified path and log a warning

### Requirement: Route-to-target mapping
The configuration SHALL define a list of route prefixes and their corresponding target API base URLs. Each route SHALL have a `prefix` and a `target_url`.

#### Scenario: Configure single target
- **WHEN** the configuration contains one route mapping prefix `/v1` to target `https://api.openai.com/v1`
- **THEN** all requests starting with `/v1` SHALL be proxied to `https://api.openai.com/v1`

#### Scenario: Configure multiple targets
- **WHEN** the configuration contains multiple route mappings
- **THEN** requests SHALL be matched to the longest matching prefix and proxied to the corresponding target

### Requirement: Server port configuration
The configuration SHALL allow specifying separate ports for the proxy server and the web UI server.

#### Scenario: Custom ports
- **WHEN** the configuration specifies `proxy_port: 9090` and `ui_port: 9091`
- **THEN** the proxy SHALL listen on port 9090 and the web UI SHALL listen on port 9091

#### Scenario: Default ports
- **WHEN** port configuration is omitted
- **THEN** the proxy SHALL default to port 8080 and the web UI SHALL default to port 8081

### Requirement: Storage configuration
The configuration SHALL allow specifying the SQLite database path and the maximum trace body size.

#### Scenario: Custom database path
- **WHEN** the configuration specifies `database: /data/sparrow.db`
- **THEN** traces SHALL be stored in `/data/sparrow.db`

#### Scenario: Default database path
- **WHEN** the database path is omitted
- **THEN** traces SHALL be stored in `./sparrow.db` relative to the working directory

#### Scenario: Max body size configuration
- **WHEN** the configuration specifies `max_body_size: 1MB`
- **THEN** request and response bodies exceeding 1MB SHALL be truncated in trace records

### Requirement: Model pricing configuration
The configuration SHALL include a pricing section mapping model names to their input and output token prices per million tokens.

#### Scenario: Define model pricing
- **WHEN** the configuration includes pricing for model `gpt-4o` with `input: 2.50` and `output: 10.00`
- **THEN** cost calculation for `gpt-4o` SHALL use $2.50 per 1M input tokens and $10.00 per 1M output tokens

### Requirement: Config validation
The gateway SHALL validate the configuration at startup using Pydantic models. Invalid configuration SHALL cause the gateway to exit with a descriptive error message.

#### Scenario: Invalid port number
- **WHEN** the configuration specifies a non-integer or out-of-range port
- **THEN** the gateway SHALL fail to start and print a validation error message

#### Scenario: Missing required route target URL
- **WHEN** a route mapping is missing the `target_url` field
- **THEN** the gateway SHALL fail to start and print a validation error identifying the invalid route

#### Scenario: Invalid proxy URL in upstream_proxy
- **WHEN** the configuration contains an invalid URL in the upstream_proxy section
- **THEN** the gateway SHALL fail to start and print a validation error identifying the invalid proxy URL

### Requirement: Example configuration file
The gateway SHALL include an `config.example.yaml` file in the project root with all available configuration options documented with comments.

#### Scenario: User creates config from example
- **WHEN** the user copies `config.example.yaml` to `config.yaml` and fills in their values
- **THEN** the gateway SHALL start successfully using the new configuration
