"""Batch processing for multiple Claude API requests."""

from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class BatchResult:
    """Result of a single batch item."""
    index: int
    success: bool
    response: Optional[Any] = None
    error: Optional[str] = None


class BatchProcessor:
    """Process multiple Claude API requests in parallel."""

    def __init__(self, client: Any, max_workers: int = 5, rate_limit: float = 0.1):
        self.client = client
        self.max_workers = max_workers
        self.rate_limit = rate_limit

    def process(
        self,
        requests: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> List[BatchResult]:
        """Process a batch of requests in parallel."""
        results: List[BatchResult] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for i, req in enumerate(requests):
                future = executor.submit(self._process_single, req)
                futures[future] = i

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    response = future.result()
                    results.append(BatchResult(index=idx, success=True, response=response))
                except Exception as e:
                    results.append(BatchResult(index=idx, success=False, error=str(e)))

                if on_progress:
                    on_progress(len(results), len(requests))

        results.sort(key=lambda r: r.index)
        return results

    def _process_single(self, request: Dict[str, Any]) -> Any:
        """Process a single request."""
        return self.client.create_message(**request)

    def map(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        **kwargs,
    ) -> List[BatchResult]:
        """Map a list of prompts to batch requests."""
        requests = [
            {"messages": [{"role": "user", "content": p}], "system": system, **kwargs}
            for p in prompts
        ]
        return self.process(requests)
