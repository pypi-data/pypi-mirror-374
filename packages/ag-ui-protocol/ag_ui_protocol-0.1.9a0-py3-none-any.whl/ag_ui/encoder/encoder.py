"""
This module contains the EventEncoder class
"""
from typing import Any
import json
from ag_ui.core.events import BaseEvent

AGUI_MEDIA_TYPE = "application/vnd.ag-ui.event+proto"

class EventEncoder:
    """
    Encodes Agent User Interaction events.
    """
    def __init__(self, accept: str = None):
        pass

    def get_content_type(self) -> str:
        """
        Returns the content type of the encoder.
        """
        return "text/event-stream"

    def encode(self, event: BaseEvent) -> str:
        """
        Encodes an event.
        """
        return self._encode_sse(event)

    def make_json_safe(self, value: Any) -> Any:
        """
        Recursively convert a value into a JSON-serializable structure.

        - Handles Pydantic models via `model_dump`.
        - Handles LangChain messages via `to_dict`.
        - Recursively walks dicts, lists, and tuples.
        - For arbitrary objects, falls back to `__dict__` if available, else `repr()`.
        """
        # Pydantic models
        if hasattr(value, "model_dump"):
            try:
                return self.make_json_safe(value.model_dump(by_alias=True, exclude_none=True))
            except Exception:
                pass

        # LangChain-style objects
        if hasattr(value, "to_dict"):
            try:
                return self.make_json_safe(value.to_dict())
            except Exception:
                pass

        # Dict
        if isinstance(value, dict):
            return {key: self.make_json_safe(sub_value) for key, sub_value in value.items()}

        # List / tuple
        if isinstance(value, (list, tuple)):
            return [self.make_json_safe(sub_value) for sub_value in value]

        # Already JSON safe
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value

        # Arbitrary object: try __dict__ first, fallback to repr
        if hasattr(value, "__dict__"):
            return {
                "__type__": type(value).__name__,
                **self.make_json_safe(value.__dict__),
            }

        return repr(value)

    def _encode_sse(self, event: BaseEvent) -> str:
        """
        Encodes an event into an SSE string.
        """
        event_dict = event.model_dump(by_alias=True, exclude_none=True)
        json_ready = self.make_json_safe(event_dict)
        json_string = json.dumps(json_ready)
        return f"data: {json_string}\n\n"
