# Cost Tracking

## Purpose

Track token usage and calculate costs for LLM API requests proxied through the gateway. Extracts usage data from responses, applies configurable pricing, and surfaces cost information in the UI.

## Requirements

### Requirement: Token usage extraction
The gateway SHALL extract token usage data from OpenAI-compatible response JSON. The system SHALL parse the `usage` field from the response body to capture `prompt_tokens`, `completion_tokens`, and `total_tokens`.

#### Scenario: Extract tokens from non-streaming response
- **WHEN** a non-streaming response contains a `usage` field with `prompt_tokens`, `completion_tokens`, and `total_tokens`
- **THEN** the gateway SHALL store these values in the trace record

#### Scenario: Extract tokens from streaming response
- **WHEN** a streaming response contains a final chunk with `usage` field
- **THEN** the gateway SHALL parse the accumulated SSE chunks, extract the usage data from the final chunk, and store the token counts in the trace record

#### Scenario: Missing usage data
- **WHEN** a response does not contain a `usage` field
- **THEN** the gateway SHALL store null values for token counts in the trace record

### Requirement: Model name extraction
The gateway SHALL extract the model name from the request body's `model` field and store it in the trace record for filtering and cost calculation.

#### Scenario: Extract model from request
- **WHEN** a request body contains `"model": "gpt-4o"`
- **THEN** the trace record SHALL store `gpt-4o` as the model name

#### Scenario: Missing model field
- **WHEN** a request body does not contain a `model` field
- **THEN** the trace record SHALL store null as the model name

### Requirement: Cost calculation
The gateway SHALL calculate the cost of each request based on token usage and a configurable per-model pricing table. The pricing table SHALL define input and output token prices per million tokens.

#### Scenario: Calculate cost for known model
- **WHEN** a trace records `prompt_tokens: 1000` and `completion_tokens: 500` for model `gpt-4o` with pricing `input: 2.50, output: 10.00` (per 1M tokens)
- **THEN** the cost SHALL be calculated as `(1000/1_000_000)*2.50 + (500/1_000_000)*10.00 = 0.0075`

#### Scenario: Unknown model pricing
- **WHEN** a trace records tokens for a model not present in the pricing table
- **THEN** the cost SHALL be recorded as null and the UI SHALL display "Unknown" for the cost

#### Scenario: Partial token data
- **WHEN** a trace has token usage for only input or only output
- **THEN** the cost SHALL be calculated using the available token counts, treating missing values as 0

### Requirement: Configurable pricing table
The gateway SHALL load model pricing from the YAML configuration file. The pricing table SHALL support adding new models without code changes.

#### Scenario: Add new model pricing
- **WHEN** the user adds a new model entry to the pricing section of the config YAML
- **THEN** subsequent requests using that model SHALL have cost calculated using the new pricing

#### Scenario: Update existing model pricing
- **WHEN** the user updates the pricing for an existing model in the config
- **THEN** only new traces SHALL use the updated pricing; existing trace costs SHALL NOT be recalculated

### Requirement: Cost display in trace list
The web UI SHALL display the calculated cost for each trace in the trace list and aggregate cost in the dashboard.

#### Scenario: Cost in trace list
- **WHEN** the trace list is displayed
- **THEN** each trace row SHALL show the calculated cost formatted as currency (e.g., $0.0075)

#### Scenario: Total cost in dashboard
- **WHEN** the dashboard is displayed
- **THEN** the total cost across all traces SHALL be shown, along with cost breakdown by model
