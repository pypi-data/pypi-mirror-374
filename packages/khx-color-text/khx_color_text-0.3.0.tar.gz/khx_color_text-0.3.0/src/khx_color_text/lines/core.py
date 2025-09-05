"""Core functionality for creating decorative lines."""

import os
import shutil
from typing import Optional, Union, Literal
from ..core import cprint
from .characters import get_char

# Define all well-known character names for IDE autocomplete
CharacterName = Literal[
    # Basic ASCII
    "asterisk",
    "dash",
    "hyphen",
    "plus",
    "dot",
    "period",
    "underscore",
    "equals",
    "tilde",
    "caret",
    "pipe",
    "forward_slash",
    "backslash",
    "hash",
    "pound",
    # Unicode box drawing
    "horizontal",
    "heavy_horizontal",
    "double_horizontal",
    "light_triple_dash",
    "heavy_triple_dash",
    "light_quadruple_dash",
    "heavy_quadruple_dash",
    # Block characters
    "full_block",
    "dark_shade",
    "medium_shade",
    "light_shade",
    "upper_half_block",
    "lower_half_block",
    "black_rectangle",
    "white_rectangle",
    "black_small_square",
    "white_small_square",
    "black_medium_square",
    "white_medium_square",
    # Wave and curved
    "tilde_operator",
    "almost_equal",
    "triple_tilde",
    "wave_dash",
    "reversed_not",
    "top_half_integral",
    "bottom_half_integral",
    # Decorative
    "black_diamond",
    "white_diamond",
    "black_circle",
    "white_circle",
    "black_star",
    "white_star",
    "diamond_suit",
    "spade_suit",
    "club_suit",
    "heart_suit",
    "reference_mark",
    "asterism",
    "low_asterisk",
    "four_balloon_asterisk",
    # Geometric
    "black_up_triangle",
    "white_up_triangle",
    "black_down_triangle",
    "white_down_triangle",
    "black_left_pointer",
    "black_right_pointer",
    "black_left_triangle",
    "black_right_triangle",
    # Mathematical
    "infinity",
    "integral",
    "summation",
    "product",
    "square_root",
    "increment",
    "nabla",
    "partial_differential",
]


def get_terminal_width() -> int:
    """Get the current terminal width."""
    try:
        # Try to get terminal size
        return shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        # Fallback to environment variable or default
        try:
            return int(os.environ.get("COLUMNS", 80))
        except (ValueError, TypeError):
            return 80


def cline(
    char: Union[str, CharacterName] = "-",
    width: Optional[int] = None,
    color: Optional[str] = None,
    bg_color: Optional[str] = None,
    style: Optional[Union[str, list]] = None,
    fill_terminal: bool = True,
) -> None:
    """
    Create a decorative line using the specified character.

    Args:
        char (Union[str, CharacterName]): Character to use for the line or character name.
                                         Can be a direct character like "*" or a name like "asterisk".
                                         Default is "-".
        width (Optional[int]): Width of the line. If None and fill_terminal is True,
                              uses terminal width. If None and fill_terminal is False,
                              defaults to 50.
        color (Optional[str]): Text color (hex, rgb, or color name).
        bg_color (Optional[str]): Background color (hex, rgb, or color name).
        style (Optional[Union[str, list]]): Text style(s) like 'bold', 'italic', etc.
        fill_terminal (bool): If True and width is None, fills the entire terminal width.
                             Default is True.

    Examples:
        >>> cline()  # Simple line filling terminal width
        >>> cline("*", color="#FF0000")  # Red asterisk line
        >>> cline("asterisk", color="#FF0000")  # Same as above using name
        >>> cline("full_block", width=30, color="blue")  # Blue block line
        >>> cline("wave_dash", bg_color="#00FF00")  # Wave line with green background
    """
    if width is None:
        if fill_terminal:
            width = get_terminal_width()
        else:
            width = 50

    # Ensure width is at least 1
    width = max(1, width)

    # Get the actual character (handles both direct chars and names)
    actual_char = get_char(char)

    # Create the line
    line = actual_char * width

    # Print with color and style
    cprint(line, color=color, bg_color=bg_color, style=style)


# Predefined line styles for convenience
def solid_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a solid line using full block character."""
    cline("full_block", width=width, color=color)


def dashed_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a dashed line."""
    cline("dash", width=width, color=color)


def dotted_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a dotted line."""
    cline("dot", width=width, color=color)


def wave_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a wavy line."""
    cline("tilde", width=width, color=color)


def double_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a double line using box drawing character."""
    cline("double_horizontal", width=width, color=color)


def star_line(width: Optional[int] = None, color: Optional[str] = None) -> None:
    """Create a decorative star line."""
    cline("asterisk", width=width, color=color)
