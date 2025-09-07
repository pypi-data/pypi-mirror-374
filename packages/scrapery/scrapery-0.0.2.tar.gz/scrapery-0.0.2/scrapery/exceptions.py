# exceptions.py
"""
Custom exceptions for Scrapery package.
"""

class ScraperyError(Exception):
    """Base class for all Scrapery exceptions."""
    pass

class ParserError(ScraperyError):
    """Raised when parsing of HTML, XML, or JSON fails."""
    pass

class FileError(ScraperyError):
    """Raised when reading a file fails."""
    pass

class InvalidSelectorError(ScraperyError):
    """Raised when a CSS or XPath selector is invalid."""
    pass

class ElementNotFoundError(ScraperyError):
    """Raised when a requested element is not found."""
    pass

class ValidationError(ScraperyError):
    """Exception raised for validation errors."""
    pass

class SelectorError(ScraperyError):
    """Exception raised for selector errors."""
    pass

class NetworkError(ScraperyError):
    """Exception raised for network errors."""
    pass

class EncodingError(ScraperyError):
    """Exception raised for encoding-related errors."""
    pass