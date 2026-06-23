## MODIFIED Requirements

### Requirement: YAML configuration file
The gateway SHALL read its configuration from a YAML file. The configuration SHALL include: server ports, target API base URLs with route prefixes, model pricing table, storage settings, logging level, and upstream proxy settings.

#### Scenario: Load configuration from file
- **WHEN** the gateway starts
- **THEN** it SHALL read the configuration from the specified YAML file and apply all settings including upstream proxy if present

#### Scenario: Missing configuration file
- **WHEN** the specified configuration file does not exist
- **THEN** the gateway SHALL create a default configuration file at the specified path and log a warning

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
