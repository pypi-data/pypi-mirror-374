# html_api.py
"""
HTML-specific function-based API using ScraperyHTMLElement.
"""
from urllib.parse import urljoin
from typing import Optional
from .html_elements import ScraperyHTMLElement
from .exceptions import ParserError, SelectorError
from .utils import standardized_string

__all__ = [
    "parse_html",
    "prettify",
    "select_all",
    "select_one",
    "get_selector_content",
    "parent",
    "children",
    "siblings",
    "next_sibling",
    "prev_sibling",
    "ancestors",
    "descendants",
    "get_absolute_url",
]

def parse_html(html_content: str | bytes, **kwargs) -> ScraperyHTMLElement:
    try:
        return ScraperyHTMLElement.from_html(html_content, **kwargs)
    except Exception as e:
        raise ParserError(f"Failed to parse HTML: {e}")

def prettify(element: ScraperyHTMLElement) -> str:
    return element.html(pretty=True)

def _detect_selector_method(selector: str) -> str:
    """
    Detect whether the selector is XPath or CSS with robust rules.
    """
    selector = selector.strip()

    # Strong XPath signals
    xpath_signals = ["//", ".//", "/", "@", "contains(", "starts-with(", "text()", "::", "[", "]"]

    if any(sig in selector for sig in xpath_signals):
        return "xpath"

    # Default fallback → CSS
    return "css"    

def get_selector_elements(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    """Return all elements matching selector (CSS or XPath)."""
    method = _detect_selector_method(selector)
    if method == "xpath":
        return element.xpath(selector)
    return element.css(selector)

def select_all(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    return get_selector_elements(element, selector)

def select_one(element: ScraperyHTMLElement, selector: str) -> ScraperyHTMLElement | None:
    items = get_selector_elements(element, selector)
    return items[0] if items else None

def get_selector_content(
    element: Optional[ScraperyHTMLElement],
    selector: Optional[str] = None,
    attr: Optional[str] = None
) -> Optional[str]:
    """
    Extract content from a ScraperyHTMLElement using CSS or XPath auto-detection.

    Supports multiple cases:
    1. Return text of the first matching element for selector.
    2. Return value of the specified attribute for selector.
    3. Return value of the specified attribute from the element directly.
    4. Return text content of the entire element if no selector or attribute is provided.
    """
    if element is None:
        return None

    try:
        # Case 4: no selector provided
        if not selector:
            if attr:
                return standardized_string(element.attr(attr, default=None)) if element.attr(attr, default=None) else None 
            return standardized_string(element.text()) if element.text() else None

        # Detect selector method (css or xpath)
        method = _detect_selector_method(selector)

        # Fetch first matching element
        if method == "xpath":
            result = element.xpath_one(selector)
        else:  # css
            result = element.css_one(selector)

        if result is None:
            return None

        if attr:
            return standardized_string(result.attr(attr, default=None))
        return standardized_string(result.text())

    except Exception as e:
        print(f"Error in get_selector_content: {e}")
        return None
 

# DOM navigation functions

def parent(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    return element.parent()

def children(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    return element.children()

def siblings(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    p = element.parent()
    if p:
        return [c for c in p.children() if c._unwrap() is not element._unwrap()]
    return []

def next_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i + 1 < len(siblings_list):
                    return siblings_list[i + 1]
                break
    return None


def prev_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i > 0:
                    return siblings_list[i - 1]
                break
    return None

def ancestors(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    p = element.parent()
    while p:
        result.append(p)
        p = p.parent()
    return result

def descendants(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    def walk(node: ScraperyHTMLElement):
        for c in node.children():
            result.append(c)
            walk(c)
    walk(element)
    return result

def has_class(element: ScraperyHTMLElement, class_name: str) -> bool:
    return class_name in element.attr("class", "").split()

def get_classes(element: ScraperyHTMLElement) -> list[str]:
    return element.attr("class", "").split()



def get_absolute_url(
    element: ScraperyHTMLElement,
    selector: Optional[str] = None,
    base_url: Optional[str] = None,
    attr: str = "href"
) -> list[str]:
    """
    Extract absolute URLs from elements using get_selector_content for CSS/XPath.

    Args:
        element (ScraperyHTMLElement): Root element to search within.
        selector (str, optional): CSS or XPath selector. If None, use element itself.
        base_url (str, optional): Base URL for resolving relative links.
        attr (str): Attribute containing the URL ("href" or "src").

    Returns:
        list[str]: List of absolute URLs.
    """
    try:
        if selector:
            raw = get_selector_content(element, selector, attr=attr)
        else:
            raw = get_selector_content(element, attr=attr)

        if not raw:
            return None

        return urljoin(base_url, raw) if base_url else raw

    except Exception as e:
        raise SelectorError(f"Error extracting absolute URL: {e}") from e
