"""Enhanced streaming support with callbacks and event handling."""

from typing import Any, Callable, Dict, List, Optional


class StreamHandler:
    """Handle streaming responses with callbacks and event processing."""

    def __init__(self):
        self._on_text: Optional[Callable[[str], None]] = None
        self._on_complete: Optional[Callable[[str], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None
        self._on_tool_use: Optional[Callable[[Dict], None]] = None
        self._collected_text: str = ""

    def on_text(self, callback: Callable[[str], None]) -> "StreamHandler":
        """Register a callback for text chunks."""
        self._on_text = callback
        return self

    def on_complete(self, callback: Callable[[str], None]) -> "StreamHandler":
        """Register a callback for stream completion."""
        self._on_complete = callback
        return self

    def on_error(self, callback: Callable[[Exception], None]) -> "StreamHandler":
        """Register a callback for errors."""
        self._on_error = callback
        return self

    def on_tool_use(self, callback: Callable[[Dict], None]) -> "StreamHandler":
        """Register a callback for tool use events."""
        self._on_tool_use = callback
        return self

    def process_stream(self, stream: Any) -> str:
        """Process a streaming response with registered callbacks."""
        self._collected_text = ""
        try:
            with stream as s:
                for event in s:
                    if hasattr(event, "type"):
                        if event.type == "content_block_delta":
                            if hasattr(event.delta, "text"):
                                chunk = event.delta.text
                                self._collected_text += chunk
                                if self._on_text:
                                    self._on_text(chunk)
                        elif event.type == "content_block_start":
                            if hasattr(event.content_block, "type") and event.content_block.type == "tool_use":
                                if self._on_tool_use:
                                    self._on_tool_use({"name": event.content_block.name})
            if self._on_complete:
                self._on_complete(self._collected_text)
        except Exception as e:
            if self._on_error:
                self._on_error(e)
            else:
                raise
        return self._collected_text
