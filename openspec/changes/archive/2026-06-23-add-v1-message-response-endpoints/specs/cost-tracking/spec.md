## MODIFIED Requirements

### Requirement: Token usage extraction
The gateway SHALL extract token usage data from API response JSON. The system SHALL parse the `usage` field from the response body, supporting both OpenAI Chat Completions format (`prompt_tokens`/`completion_tokens`/`total_tokens`) and the format used by Anthropic Messages and OpenAI Responses APIs (`input_tokens`/`output_tokens`). When `input_tokens`/`output_tokens` are present, they SHALL be mapped to `prompt_tokens`/`completion_tokens` respectively. For streaming responses, the gateway SHALL use the appropriate SSE parser based on the request path.

#### Scenario: Extract tokens from non-streaming response with prompt_tokens format
- **WHEN** a non-streaming response contains a `usage` field with `prompt_tokens`, `completion_tokens`, and `total_tokens`
- **THEN** the gateway SHALL store these values in the trace record

#### Scenario: Extract tokens from non-streaming response with input_tokens format
- **WHEN** a non-streaming response contains a `usage` field with `input_tokens` and `output_tokens` but no `prompt_tokens`
- **THEN** the gateway SHALL map `input_tokens` to `prompt_tokens`, `output_tokens` to `completion_tokens`, and compute `total_tokens` as their sum if not present

#### Scenario: Extract tokens from streaming response with endpoint-specific parser
- **WHEN** a streaming response is received and the request path is `/v1/messages`
- **THEN** the gateway SHALL use the Anthropic Messages SSE parser to extract token usage from `message_start` and `message_delta` events

#### Scenario: Extract tokens from streaming response with OpenAI Responses parser
- **WHEN** a streaming response is received and the request path is `/v1/responses`
- **THEN** the gateway SHALL use the OpenAI Responses SSE parser to extract token usage from the `response.completed` event

#### Scenario: Missing usage data
- **WHEN** a response does not contain a `usage` field
- **THEN** the gateway SHALL store null values for token counts in the trace record

### Requirement: Model name extraction
The gateway SHALL extract the model name from the request body's `model` field and store it in the trace record for filtering and cost calculation. This applies to all supported API formats (OpenAI Chat Completions, Anthropic Messages, and OpenAI Responses).

#### Scenario: Extract model from request
- **WHEN** a request body contains `"model": "gpt-4o"`
- **THEN** the trace record SHALL store `gpt-4o` as the model name

#### Scenario: Missing model field
- **WHEN** a request body does not contain a `model` field
- **THEN** the trace record SHALL store null as the model name
