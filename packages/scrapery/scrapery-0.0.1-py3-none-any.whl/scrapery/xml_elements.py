# xml_elements.py
"""
ScraperyXMLElement: high-performance wrapper for XML elements using lxml.etree
"""
from __future__ import annotations
from functools import lru_cache
from types import MappingProxyType
from typing import Any, Mapping, Optional
from lxml import etree
from .exceptions import ParserError

@lru_cache(maxsize=1024)
def _compile_xpath(expr: str, ns_items: tuple[tuple[str, str], ...] | None) -> etree.XPath:
    namespaces = dict(ns_items) if ns_items else None
    return etree.XPath(expr, namespaces=namespaces, smart_strings=False)

class ScraperyXMLElement:
    __slots__ = ("_node", "_tag")

    @classmethod
    def from_xml(cls, data: str | bytes, recover: bool = True) -> "ScraperyXMLElement":
        if not data:
            raise ValueError("Empty XML content")
        try:
            parser = etree.XMLParser(recover=recover)
            root = etree.fromstring(data, parser=parser)
            return cls(root)
        except Exception as e:
            raise ParserError(f"Failed to parse XML: {e}") from e

    def __init__(self, node: etree._Element):
        if not isinstance(node, etree._Element):
            raise TypeError("ScraperyXMLElement expects lxml element")
        self._node = node
        self._tag = node.tag if isinstance(node.tag, str) else str(node.tag)

    @property
    def tag(self) -> str:
        return self._tag

    def text(self, normalize: bool = False, strip: bool = True, joiner: str = " ") -> str:
        raw = "".join(self._node.itertext())
        if strip:
            raw = raw.strip()
        if normalize:
            raw = joiner.join(raw.split())
        return raw

    def attr(self, name: str, default: Any = None) -> Any:
        return self._node.get(name, default)

    def attrs(self, copy: bool = False) -> Mapping[str, str]:
        return dict(self._node.attrib) if copy else MappingProxyType(self._node.attrib)

    def parent(self) -> "ScraperyXMLElement | None":
        p = self._node.getparent()
        return ScraperyXMLElement(p) if p else None

    def children(self) -> list["ScraperyXMLElement"]:
        return [ScraperyXMLElement(c) for c in self._node]

    def find(self, tag: str) -> "ScraperyXMLElement | None":
        n = self._node.find(tag)
        return ScraperyXMLElement(n) if n is not None else None

    def find_all(self, tag: str) -> list["ScraperyXMLElement"]:
        return [ScraperyXMLElement(n) for n in self._node.findall(tag)]

    def xpath(self, expr: str, namespaces: Mapping[str, str] | None = None) -> list["ScraperyXMLElement | Any"]:
        ns_items = tuple(sorted(namespaces.items())) if namespaces else None
        xp = _compile_xpath(expr, ns_items)
        out = xp(self._node)
        if not isinstance(out, (list, tuple)):
            out = [out]
        return [ScraperyXMLElement(i) if isinstance(i, etree._Element) else i for i in out]

    def xpath_one(self, expr: str, namespaces: Mapping[str, str] | None = None) -> "ScraperyXMLElement | Any | None":
        res = self.xpath(expr, namespaces)
        return res[0] if res else None

    def html(self, pretty: bool = False) -> str:
        from lxml import etree
        return etree.tostring(self._node, encoding=str, with_tail=False, pretty_print=pretty, method="xml")

    def _unwrap(self) -> etree._Element:
        return self._node
