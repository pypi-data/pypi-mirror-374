# utils.py
import re
import os
import chardet
from typing import Any, Optional, Union
from ftfy import fix_text
from .exceptions import FileError, EncodingError, ValidationError

def standardized_string(string: Optional[str] = None) -> str:
    """
    Standardizes a string by:
    - Replacing `\n`, `\t`, and `\r` with spaces.
    - Removing HTML tags.
    - Replacing multiple spaces with a single space.
    - Stripping leading/trailing spaces.

    Args:
    - string (str, optional): The string to be standardized. Defaults to None.

    Returns:
    - str: The standardized string, or an empty string if input is None.
    """
    old_string = string
    if string is None:
        return ""
    if not isinstance(string, str):
        string = str(string)

    # Fix encoding issues (mojibake)
    try:
        try:
            string = fix_text(string)
        except:
            pass

        string = string.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
        string = re.sub(r"<.*?>", " ", string)  # Remove HTML tags
        string = re.sub(r"\s+", " ", string)  # Collapse multiple spaces into one
        string = string.strip()  # Strip leading/trailing spaces
        return string
    except:
        return old_string

# -------------------------------
# File Reading
# -------------------------------
def read_file(file_path: str, encoding: Optional[str] = None) -> str:
    """Read file content with efficient encoding detection."""
    if not os.path.isfile(file_path):
        raise FileError(f"File not found or not a file: {file_path}")
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    if not encoding:
        encoding = detect_encoding(content)
    
    try:
        return content.decode(encoding)
    except UnicodeDecodeError:
        # Fallback to utf-8 with replacement
        try:
            return content.decode('utf-8', errors='replace')
        except Exception:
            raise EncodingError(f"Failed to decode file: {file_path}")


# -------------------------------
# Input Validation
# -------------------------------

def validate_input(data: Any, data_type: Optional[type] = None) -> None:
    """Validate input data with type checking."""
    if data is None:
        raise ValidationError("Input data cannot be None")
    if isinstance(data, str) and not data.strip():
        raise ValidationError("Input data cannot be empty string")
    if data_type and not isinstance(data, data_type):
        raise ValidationError(f"Input data must be of type {data_type.__name__}")


# -------------------------------
# HTML Normalization
# -------------------------------

_normalize_comments_re = re.compile(r'<!--.*?-->', re.DOTALL)

def normalize_html(html_content: str) -> str:
    """Normalize HTML for faster parsing."""
    html_content = re.sub(r'>\s+<', '><', html_content)
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = _normalize_comments_re.sub('', html_content)
    return html_content


def detect_encoding(data: Union[str, bytes]) -> str:
    """Detect encoding of data efficiently."""
    if isinstance(data, str):
        return 'utf-8'
    result = chardet.detect(data)
    encoding = result.get('encoding') or 'utf-8'
    try:
        data.decode(encoding)
        return encoding
    except (UnicodeDecodeError, LookupError):
        return 'utf-8'

__all__ = [
    "standardized_string",
]
