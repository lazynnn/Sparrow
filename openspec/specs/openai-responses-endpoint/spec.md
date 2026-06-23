# OpenAI Responses Endpoint

## Purpose

Parse OpenAI Responses API requests and responses at the `/v1/responses` endpoint, extracting model names and token usage for tracing and cost tracking.

## Requirements

### Requirement: OpenAI Responses API request parsing
The gateway SHALL extract the model name from the `model` field of OpenAI Responses API requests sent to `/v1/responses`. The gateway SHALL detect streaming requests by the `stream` field in the request body.

#### Scenario: Extract model from Responses API request
- **WHEN** a POST request is sent to `/v1/responses` with body `{"model": "gpt-4o", "input": "Hello"}`
- **THEN** the gateway SHALL store `gpt-4o` as the model name in the trace record

#### Scenario: Responses API request without model field
- **WHEN** a POST request is sent to `/v1/responses` with a body that does not contain a `model` field
- **THEN** the gateway SHALL store null as the model name in the trace record

### Requirement: OpenAI Responses API non-streaming response parsing
The gateway SHALL extract token usage from OpenAI Responses API non-streaming responses. The `usage.input_tokens` field SHALL be mapped to `prompt_tokens`, `usage.output_tokens` SHALL be mapped to `completion_tokens`, and `usage.total_tokens` SHALL be used directly if present, or computed as the sum of input and output tokens.

#### Scenario: Extract tokens from Responses API non-streaming response
- **WHEN** a non-streaming response from `/v1/responses` contains `{"usage": {"input_tokens": 100, "output_tokens": 200, "total_tokens": 300}}`
- **THEN** the gateway SHALL store `prompt_tokens: 100`, `completion_tokens: 200`, `total_tokens: 300` in the trace record

#### Scenario: Responses API response without total_tokens
- **WHEN** a non-streaming response from `/v1/responses` contains `{"usage": {"input_tokens": 100, "output_tokens": 200}}`
- **THEN** the gateway SHALL store `prompt_tokens: 100`, `completion_tokens: 200`, `total_tokens: 300` (computed) in the trace record

#### Scenario: Responses API response with missing usage
- **WHEN** a non-streaming response from `/v1/responses` does not contain a `usage` field
- **THEN** the gateway SHALL store null values for all token counts in the trace record

### Requirement: OpenAI Responses API streaming response parsing
The gateway SHALL extract token usage from OpenAI Responses API streaming responses by parsing SSE events. The `response.completed` event contains the full `response.usage` object. The gateway SHALL map `input_tokens` to `prompt_tokens` and `output_tokens` to `completion_tokens`.

#### Scenario: Extract tokens from Responses API streaming response
- **WHEN** a streaming response from `/v1/responses` contains a `response.completed` event with `{"response": {"usage": {"input_tokens": 50, "output_tokens": 75, "total_tokens": 125}}}`
- **THEN** the gateway SHALL store `prompt_tokens: 50`, `completion_tokens: 75`, `total_tokens: 125` in the trace record

#### Scenario: Responses API streaming without completed event
- **WHEN** a streaming response from `/v1/responses` does not contain a `response.completed` event (e.g., connection interrupted)
- **THEN** the gateway SHALL store null values for all token counts in the trace record
