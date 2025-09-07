# json_api.py
"""
JSON-specific function-based API using ScraperyJSONElement.
"""
from typing import Any
from .json_elements import ScraperyJSONElement
from .exceptions import ParserError

__all__ = [
    "parse_json",
    "get",
    "children",
    "keys",
    "values",
    "items",
    "text",
]

def parse_json(data: Any) -> ScraperyJSONElement:
    try:
        return ScraperyJSONElement.from_data(data)
    except Exception as e:
        raise ParserError(f"Failed to parse JSON: {e}")

def get(element: ScraperyJSONElement, key: Any, default: Any = None) -> Any:
    return element.get(key, default)

def children(element: ScraperyJSONElement) -> list[ScraperyJSONElement]:
    return element.children()

def keys(element: ScraperyJSONElement) -> list[str] | None:
    return element.keys()

def values(element: ScraperyJSONElement) -> list[Any] | None:
    return element.values()

def items(element: ScraperyJSONElement) -> list[tuple] | None:
    return element.items()

def text(element: ScraperyJSONElement) -> str:
    return element.text()
