"""Extended Claude client with retry logic, middleware, and enhanced configuration."""

from typing import Any, Dict, List, Optional, Callable
import anthropic


class ClaudeClient:
    """Extended Anthropic client with retry, middleware, and advanced features."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        max_retries: int = 3,
        timeout: int = 120,
        middleware: Optional[List[Callable]] = None,
    ):
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self._middleware = middleware or []
        self._cost_tracker = None

    def with_cost_tracking(self, tracker: Any) -> "ClaudeClient":
        """Enable cost tracking for all requests."""
        self._cost_tracker = tracker
        return self

    def add_middleware(self, fn: Callable) -> None:
        """Add a middleware function to the request pipeline."""
        self._middleware.append(fn)

    def create_message(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        tools: Optional[List[Dict]] = None,
        **kwargs,
    ) -> Any:
        """Create a message with retry logic and middleware support."""
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }
        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools

        for mw in self._middleware:
            params = mw(params)

        attempt = 0
        while attempt < self.max_retries:
            try:
                response = self._client.messages.create(**params)
                if self._cost_tracker:
                    self._cost_tracker.record(response)
                return response
            except anthropic.RateLimitError:
                attempt += 1
                if attempt >= self.max_retries:
                    raise
            except anthropic.APIError:
                attempt += 1
                if attempt >= self.max_retries:
                    raise

    def stream_message(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """Stream a message response."""
        params = {
            "model": self.model,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            "messages": messages,
            **kwargs,
        }
        return self._client.messages.stream(**params)
