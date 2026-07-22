import json
from typing import Any


class ResponseParser:
    """Normalizes text and optional JSON responses from AI providers."""

    def parse(self, content: str, expect_json: bool = False) -> tuple[str, Any | None]:
        normalized = content.strip()
        if not expect_json:
            return normalized, None

        try:
            return normalized, json.loads(normalized)
        except json.JSONDecodeError:
            extracted = self._extract_json_object(normalized)
            if extracted is None:
                return normalized, None
            try:
                return normalized, json.loads(extracted)
            except json.JSONDecodeError:
                return normalized, None

    def _extract_json_object(self, content: str) -> str | None:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return content[start : end + 1]
