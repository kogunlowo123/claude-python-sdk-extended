"""Tool registration and execution framework for Claude function calling."""

from typing import Any, Callable, Dict, List, Optional, get_type_hints
import json
import inspect


class ToolRegistry:
    """Registry for managing tools that Claude can call."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable:
        """Decorator to register a function as a tool."""
        def decorator(fn: Callable) -> Callable:
            tool_name = name or fn.__name__
            tool_desc = description or fn.__doc__ or ""
            hints = get_type_hints(fn)
            sig = inspect.signature(fn)

            properties = {}
            required = []
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                param_type = hints.get(param_name, str)
                type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
                properties[param_name] = {
                    "type": type_map.get(param_type, "string"),
                    "description": f"Parameter: {param_name}",
                }
                if param.default is inspect.Parameter.empty:
                    required.append(param_name)

            self._tools[tool_name] = {
                "name": tool_name,
                "description": tool_desc,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            self._handlers[tool_name] = fn
            return fn
        return decorator

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools in Claude API format."""
        return list(self._tools.values())

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a registered tool by name."""
        if tool_name not in self._handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._handlers[tool_name](**tool_input)

    def handle_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Process tool calls from a Claude response."""
        results = []
        for block in response.content:
            if block.type == "tool_use":
                result = self.execute(block.name, block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })
        return results
