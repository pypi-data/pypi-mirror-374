# json_elements.py
"""
ScraperyJSONElement: lightweight wrapper for JSON data structures (dict/list)
"""
from __future__ import annotations
from typing import Any, Mapping, Sequence, Union, List, Optional
from .exceptions import ParserError

class ScraperyJSONElement:
    __slots__ = ("_data",)

    @classmethod
    def from_data(cls, data: Any) -> "ScraperyJSONElement":
        if not isinstance(data, (dict, list)):
            raise ParserError(f"Expected dict or list for JSONElement, got {type(data)}")
        return cls(data)

    def __init__(self, data: Any):
        self._data = data

    def get(self, key: Union[str, int], default: Any = None) -> Any:
        try:
            if isinstance(self._data, dict) and isinstance(key, str):
                value = self._data.get(key, default)
            elif isinstance(self._data, list) and isinstance(key, int):
                value = self._data[key] if 0 <= key < len(self._data) else default
            else:
                return default

            # Wrap dict/list into ScraperyJSONElement
            if isinstance(value, (dict, list)):
                return ScraperyJSONElement(value)
            return value

        except Exception:
            return default


    def children(self) -> List["ScraperyJSONElement"]:
        if isinstance(self._data, dict):
            return [ScraperyJSONElement(v) for v in self._data.values()]
        elif isinstance(self._data, list):
            return [ScraperyJSONElement(v) for v in self._data]
        else:
            return []

    def keys(self) -> Optional[Sequence[str]]:
        if isinstance(self._data, dict):
            return list(self._data.keys())
        return None

    def values(self) -> Optional[Sequence[Any]]:
        if isinstance(self._data, dict):
            return list(self._data.values())
        elif isinstance(self._data, list):
            return self._data
        return None

    def items(self) -> Optional[Sequence[tuple]]:
        if isinstance(self._data, dict):
            return list(self._data.items())
        return None

    def text(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return f"<ScraperyJSONElement type={type(self._data).__name__}>"

    def _unwrap(self) -> Any:
        return self._data
