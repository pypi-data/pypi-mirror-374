"""
urw-scroll-table: A scrollable and editable table widget for urwid.

This package provides a comprehensive table widget that supports:
- Horizontal and vertical scrolling
- Editable cells with different types (text, dropdown)
- Keyboard navigation
- Customizable styling and colors
"""

from .table import UrwScrollTable
from .widgets import (
    SafeText,
    SingleLineText,
    HeightEnforcer,
    EditableCell,
    DropdownCell,
)

__version__ = "0.1.2"
__all__ = [
    "UrwScrollTable",
    "SafeText",
    "SingleLineText",
    "HeightEnforcer",
    "EditableCell",
    "DropdownCell",
]
