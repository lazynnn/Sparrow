from __future__ import annotations

from typing import Optional

from sparrow.config import AppConfig, ModelPricing


def calculate_cost(
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
    model_name: Optional[str],
    pricing: dict[str, ModelPricing],
) -> Optional[float]:
    if model_name is None or model_name not in pricing:
        return None

    model_pricing = pricing[model_name]
    input_tokens = prompt_tokens or 0
    output_tokens = completion_tokens or 0

    cost = (input_tokens / 1_000_000) * model_pricing.input + (
        output_tokens / 1_000_000
    ) * model_pricing.output

    return round(cost, 10)
