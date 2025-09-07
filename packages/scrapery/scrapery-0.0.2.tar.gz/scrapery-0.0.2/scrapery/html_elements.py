# html_elements.py
"""
ScraperyHTMLElement: high-performance wrapper for HTML elements using lxml.html
"""
from __future__ import annotations
import os
import io
import re
from functools import lru_cache
from types import MappingProxyType
from typing import Any, Mapping, Optional
from lxml import etree, html
from .exceptions import ParserError, FileError
from .utils import read_file, validate_input, normalize_html, detect_encoding

try:
    from lxml.cssselect import CSSSelector  # type: ignore
    _CSS_AVAILABLE = True
except Exception:
    CSSSelector = None  # type: ignore
    _CSS_AVAILABLE = False

# Precompiled regex for performance
_SCRIPT_RE = re.compile(r"<script.*?</script>", re.DOTALL | re.IGNORECASE)
_STYLE_RE = re.compile(r"<style.*?</style>", re.DOTALL | re.IGNORECASE)
_NOSCRIPT_RE = re.compile(r"<noscript.*?</noscript>", re.DOTALL | re.IGNORECASE)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

@lru_cache(maxsize=1024)
def _compile_xpath(expr: str, ns_items: tuple[tuple[str, str], ...] | None) -> etree.XPath:
    namespaces = dict(ns_items) if ns_items else None
    return etree.XPath(expr, namespaces=namespaces, smart_strings=False)

if _CSS_AVAILABLE:
    @lru_cache(maxsize=512)
    def _compile_css(selector: str) -> CSSSelector:
        return CSSSelector(selector)

def _to_string(node: etree._Element, pretty: bool, method: str) -> str:
    return etree.tostring(node, encoding=str, with_tail=False, pretty_print=pretty, method=method)

def _is_html_node(node: etree._Element) -> bool:
    return isinstance(node, html.HtmlElement) or hasattr(node, "text_content")

class ScraperyHTMLElement:
    __slots__ = ("_node", "_tag")

    @classmethod
    def from_html(cls, html_content: str | bytes, *, encoding: Optional[str] = None, normalize: bool = True,
                  recover: bool = True, remove_comments: bool = True, remove_scripts: bool = False,
                  remove_styles: bool = False, remove_noscript: bool = False, **parser_kwargs) -> "ScraperyHTMLElement":
        if isinstance(html_content, str) and os.path.isfile(html_content):
            try:
                html_content = read_file(html_content, encoding)
            except Exception as e:
                raise ParserError(f"Failed to read HTML file: {e}")
        validate_input(html_content)
        if isinstance(html_content, bytes):
            if not encoding:
                encoding = detect_encoding(html_content)
            html_content = html_content.decode(encoding or "utf-8", errors="replace")
        if normalize:
            html_content = normalize_html(html_content)
            if remove_scripts:
                html_content = _SCRIPT_RE.sub("", html_content)
            if remove_styles:
                html_content = _STYLE_RE.sub("", html_content)
            if remove_noscript:
                html_content = _NOSCRIPT_RE.sub("", html_content)
            if remove_comments:
                html_content = _COMMENT_RE.sub("", html_content)
        if len(html_content) >= 1_000_000:
            try:
                stream = io.BytesIO(html_content.encode(encoding or "utf-8"))
                context = etree.iterparse(stream, events=("start", "end"), html=True, recover=recover)
                for _ev, _el in context:
                    pass
                root = context.root
                del context
                return cls(root)
            except Exception as e:
                raise ParserError(f"Lazy parse failed: {e}")
        else:
            try:
                parser = html.HTMLParser(recover=recover, encoding=encoding or "utf-8", **parser_kwargs)
                root = html.fromstring(html_content, parser=parser)
                return cls(root)
            except Exception as e:
                raise ParserError(f"HTML parse failed: {e}")

    def __init__(self, node: etree._Element):
        if not isinstance(node, etree._Element):
            raise TypeError("ScraperyHTMLElement expects lxml element")
        self._node = node
        self._tag = node.tag if isinstance(node.tag, str) else str(node.tag)

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def is_html(self) -> bool:
        return _is_html_node(self._node)

    def text(self, normalize: bool = False, strip: bool = True, joiner: str = " ") -> str:
        raw = self._node.text_content()
        if strip:
            raw = raw.strip()
        if normalize:
            raw = joiner.join(raw.split())
        return raw

    def html(self, pretty: bool = False) -> str:
        return _to_string(self._node, pretty, "html")

    def inner_html(self, pretty: bool = False) -> str:
        return "".join(_to_string(c, pretty, "html") for c in self._node)

    def attr(self, name: str, default: Any = None) -> Any:
        return self._node.get(name, default)

    def attrs(self, copy: bool = False) -> Mapping[str, str]:
        return dict(self._node.attrib) if copy else MappingProxyType(self._node.attrib)

    def parent(self) -> "ScraperyHTMLElement | None":
        p = self._node.getparent()
        return ScraperyHTMLElement(p) if p is not None else None


    def children(self) -> list["ScraperyHTMLElement"]:
        return [ScraperyHTMLElement(c) for c in self._node]

    def css(self, selector: str) -> list["ScraperyHTMLElement"]:
        if not _CSS_AVAILABLE:
            raise ImportError("Install cssselect to use CSS selectors")
        try:
            sel = _compile_css(selector)
            return [ScraperyHTMLElement(n) for n in sel(self._node)]
        except Exception as e:
            raise ParserError(f"Invalid CSS selector: {e}")

    def css_one(self, selector: str) -> "ScraperyHTMLElement | None":
        items = self.css(selector)
        return items[0] if len(items) > 0 else None

    def xpath(self, expr: str, namespaces: Mapping[str, str] | None = None) -> list["ScraperyHTMLElement | Any"]:
        ns_items = tuple(sorted(namespaces.items())) if namespaces else None
        xp = _compile_xpath(expr, ns_items)
        out = xp(self._node)
        if not isinstance(out, (list, tuple)):
            out = [out]
        return [ScraperyHTMLElement(i) if isinstance(i, etree._Element) else i for i in out]

    def xpath_one(self, expr: str, namespaces: Mapping[str, str] | None = None) -> "ScraperyHTMLElement | Any | None":
        res = self.xpath(expr, namespaces=namespaces)
        return res[0] if len(res) > 0 else None

    def _unwrap(self) -> etree._Element:
        return self._node
