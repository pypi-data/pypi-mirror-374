# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
HTML Cleaning Utility
========================================

This utility provides functions for cleaning and processing HTML content.


"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import re
from typing import List

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Constants
# =============================================================================

# Compile regex once to remove HTML tags
CLEANR: re.Pattern[str] = re.compile(r"<.*?>")

# =============================================================================
# Functions
# =============================================================================


def clean_html(
    raw_html: str,
    strip: bool = True,
) -> str:
    """
    Remove HTML tags from a given raw HTML string.

    Args:
        raw_html (str): The raw HTML string to be cleaned.

    Returns:
        str: The cleaned text with HTML tags removed.
    """
    cleaned: str = re.sub(
        pattern=CLEANR,
        repl="",
        string=raw_html,
    )
    return cleaned.strip() if strip else cleaned


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "clean_html",
]
