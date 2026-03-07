"""Track API usage costs across requests."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UsageRecord:
    """Record of a single API call's usage."""
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Pricing per million tokens (USD)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
    "claude-haiku-3-20250307": {"input": 0.25, "output": 1.25},
}


class CostTracker:
    """Track and report on API usage costs."""

    def __init__(self, budget_limit: Optional[float] = None):
        self._records: List[UsageRecord] = []
        self.budget_limit = budget_limit

    def record(self, response: Any) -> UsageRecord:
        """Record usage from a Claude API response."""
        model = response.model
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        pricing = MODEL_PRICING.get(model, {"input": 3.0, "output": 15.0})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

        record = UsageRecord(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        self._records.append(record)

        if self.budget_limit and self.total_cost > self.budget_limit:
            raise BudgetExceededError(f"Budget of ${self.budget_limit:.2f} exceeded")

        return record

    @property
    def total_cost(self) -> float:
        """Get total cost across all recorded requests."""
        return sum(r.cost_usd for r in self._records)

    @property
    def total_tokens(self) -> Dict[str, int]:
        """Get total token counts."""
        return {
            "input": sum(r.input_tokens for r in self._records),
            "output": sum(r.output_tokens for r in self._records),
        }

    def summary(self) -> Dict[str, Any]:
        """Generate a usage summary."""
        return {
            "total_requests": len(self._records),
            "total_cost_usd": round(self.total_cost, 6),
            "total_tokens": self.total_tokens,
            "budget_remaining": round(self.budget_limit - self.total_cost, 6) if self.budget_limit else None,
        }


class BudgetExceededError(Exception):
    """Raised when the cost budget is exceeded."""
    pass
