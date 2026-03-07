"""Structured output parsing and validation using Pydantic models."""

from typing import Any, Dict, List, Optional, Type, TypeVar
import json
import re

T = TypeVar("T")


class StructuredOutput:
    """Parse and validate structured outputs from Claude responses."""

    @staticmethod
    def extract_json(text: str) -> Any:
        """Extract JSON from a Claude response, handling markdown code blocks."""
        json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def parse_with_model(text: str, model_class: Type[T]) -> T:
        """Parse Claude response into a Pydantic model instance."""
        data = StructuredOutput.extract_json(text)
        if data is None:
            raise ValueError("No valid JSON found in response")
        return model_class(**data)

    @staticmethod
    def parse_list(text: str) -> List[str]:
        """Parse a bulleted or numbered list from Claude response."""
        lines = text.strip().split("\n")
        items = []
        for line in lines:
            cleaned = re.sub(r"^[\s]*[-*\d.]+[\s.)\]]*", "", line).strip()
            if cleaned:
                items.append(cleaned)
        return items

    @staticmethod
    def parse_table(text: str) -> List[Dict[str, str]]:
        """Parse a markdown table from Claude response."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        table_lines = [l for l in lines if "|" in l]
        if len(table_lines) < 3:
            return []
        headers = [h.strip() for h in table_lines[0].split("|") if h.strip()]
        rows = []
        for line in table_lines[2:]:
            values = [v.strip() for v in line.split("|") if v.strip()]
            if len(values) == len(headers):
                rows.append(dict(zip(headers, values)))
        return rows
