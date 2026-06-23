# Anthropic Messages Endpoint

## Purpose

Parse Anthropic Messages API requests and responses at the `/v1/messages` endpoint, extracting model names and token usage for tracing and cost tracking.

## Requirements

### Requirement: Anthropic Messages API request parsing
The gateway SHALL extract the model name from the `model` field of Anthropic Messages API requests sent to `/v1/messages`. The gateway SHALL detect Anthropic streaming requests by the `stream` field in the request body.

#### Scenario: Extract model from Anthropic request
- **WHEN** a POST request is sent to `/v1/messages` with body `{"model": "claude-3-opus-20240229", "messages": [...]}`
- **THEN** the gateway SHALL store `claude-3-opus-20240229` as the model name in the trace record

#### Scenario: Anthropic request without model field
- **WHEN** a POST request is sent to `/v1/messages` with a body that does not contain a `model` field
- **THEN** the gateway SHALL store null as the model name in the trace record

### Requirement: Anthropic Messages API non-streaming response parsing
The gateway SHALL extract token usage from Anthropic Messages API non-streaming responses. The `usage.input_tokens` field SHALL be mapped to `prompt_tokens`, `usage.output_tokens` SHALL be mapped to `completion_tokens`, and `total_tokens` SHALL be computed as the sum of input and output tokens.

#### Scenario: Extract tokens from Anthropic non-streaming response
- **WHEN** a non-streaming response from `/v1/messages` contains `{"usage": {"input_tokens": 25, "output_tokens": 50}}`
- **THEN** the gateway SHALL store `prompt_tokens: 25`, `completion_tokens: 50`, `total_tokens: 75` in the trace record

#### Scenario: Anthropic response with missing usage
- **WHEN** a non-streaming response from `/v1/messages` does not contain a `usage` field
- **THEN** the gateway SHALL store null values for all token counts in the trace record

### Requirement: Anthropic Messages API streaming response parsing
The gateway SHALL extract token usage from Anthropic Messages API streaming responses by parsing SSE events. The `message_start` event contains `message.usage.input_tokens` and the `message_delta` event contains `usage.output_tokens`. The gateway SHALL accumulate usage across these events.

#### Scenario: Extract tokens from Anthropic streaming response
- **WHEN** a streaming response from `/v1/messages` contains a `message_start` event with `{"message": {"usage": {"input_tokens": 30}}}` and a `message_delta` event with `{"usage": {"output_tokens": 60}}`
- **THEN** the gateway SHALL store `prompt_tokens: 30`, `completion_tokens: 60`, `total_tokens: 90` in the trace record

#### Scenario: Anthropic streaming with only input tokens
- **WHEN** a streaming response from `/v1/messages` contains a `message_start` event with input tokens but no `message_delta` event with output tokens (e.g., connection interrupted)
- **THEN** the gateway SHALL store the available `prompt_tokens` and null for `completion_tokens` and `total_tokens`

#### Scenario: Anthropic SSE with event and data lines
- **WHEN** a streaming response from `/v1/messages` sends `event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":10}}}\n\n`
- **THEN** the gateway SHALL correctly parse the event type and extract the input tokens from the associated data payload
