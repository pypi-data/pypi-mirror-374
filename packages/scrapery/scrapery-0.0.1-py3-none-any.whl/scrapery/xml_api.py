# xml_api.py
"""
XML-specific function-based API using ScraperyXMLElement.
"""
from typing import Optional, Mapping
from .xml_elements import ScraperyXMLElement
from .exceptions import ParserError

__all__ = [
    "parse_xml",
    "prettify",
    "select_all",
    "select_one",
    "parent",
    "children",
    "find",
    "find_all",
    "xpath",
    "xpath_one",
]

def parse_xml(xml_content: str | bytes, **kwargs) -> ScraperyXMLElement:
    try:
        return ScraperyXMLElement.from_xml(xml_content, **kwargs)
    except Exception as e:
        raise ParserError(f"Failed to parse XML: {e}")

def prettify(element: ScraperyXMLElement) -> str:
    return element.html(pretty=True)

def select_all(element: ScraperyXMLElement, xpath_expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath(xpath_expr, namespaces)

def select_one(element: ScraperyXMLElement, xpath_expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath_one(xpath_expr, namespaces)

# DOM navigation functions

def parent(element: ScraperyXMLElement) -> ScraperyXMLElement | None:
    return element.parent()

def children(element: ScraperyXMLElement) -> list[ScraperyXMLElement]:
    return element.children()

def find(element: ScraperyXMLElement, tag: str) -> ScraperyXMLElement | None:
    return element.find(tag)

def find_all(element: ScraperyXMLElement, tag: str) -> list[ScraperyXMLElement]:
    return element.find_all(tag)

def xpath(element: ScraperyXMLElement, expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath(expr, namespaces)

def xpath_one(element: ScraperyXMLElement, expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath_one(expr, namespaces)
