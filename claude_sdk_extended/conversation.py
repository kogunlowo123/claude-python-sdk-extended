"""Multi-turn conversation management with history and context window handling."""

from typing import Any, Dict, List, Optional
import json


class Conversation:
    """Manages multi-turn conversations with automatic history management."""

    def __init__(
        self,
        client: Any,
        system: Optional[str] = None,
        max_history: int = 100,
        auto_summarize: bool = False,
    ):
        self.client = client
        self.system = system
        self.max_history = max_history
        self.auto_summarize = auto_summarize
        self._messages: List[Dict[str, str]] = []
        self._metadata: List[Dict[str, Any]] = []

    @property
    def messages(self) -> List[Dict[str, str]]:
        """Get the current message history."""
        return list(self._messages)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self._messages.append({"role": "user", "content": content})
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation."""
        self._messages.append({"role": "assistant", "content": content})
        self._trim_history()

    def send(self, message: str, **kwargs) -> Any:
        """Send a message and get a response, maintaining history."""
        self.add_user_message(message)
        response = self.client.create_message(
            messages=self._messages,
            system=self.system,
            **kwargs,
        )
        assistant_text = response.content[0].text
        self.add_assistant_message(assistant_text)
        return response

    def _trim_history(self) -> None:
        """Trim history to max_history messages."""
        if len(self._messages) > self.max_history:
            self._messages = self._messages[-self.max_history:]

    def clear(self) -> None:
        """Clear conversation history."""
        self._messages.clear()
        self._metadata.clear()

    def export_history(self) -> str:
        """Export conversation history as JSON."""
        return json.dumps(self._messages, indent=2)

    def fork(self) -> "Conversation":
        """Create a fork of this conversation with the same history."""
        new_conv = Conversation(
            client=self.client,
            system=self.system,
            max_history=self.max_history,
        )
        new_conv._messages = list(self._messages)
        return new_conv
