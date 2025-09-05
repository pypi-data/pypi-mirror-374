"""Text styling definitions for khx_color_text."""

from enum import Enum
from typing import List, Union
from colorama import Style


class TextStyle(Enum):
    """Available text styles."""

    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    DIM = "dim"
    BRIGHT = "bright"


# ANSI codes for text styles
STYLE_CODES = {
    TextStyle.BOLD: "\033[1m",
    TextStyle.ITALIC: "\033[3m",
    TextStyle.UNDERLINE: "\033[4m",
    TextStyle.STRIKETHROUGH: "\033[9m",
    TextStyle.DIM: Style.DIM,
    TextStyle.BRIGHT: Style.BRIGHT,
}


def get_style_codes(styles: Union[str, List[str], TextStyle, List[TextStyle]]) -> str:
    """Get ANSI codes for text styles.

    Args:
        styles: Single style or list of styles (strings or TextStyle enums)

    Returns:
        Combined ANSI codes for all styles

    Raises:
        ValueError: If style is not recognized
    """
    if not styles:
        return ""

    # Normalize to list
    if not isinstance(styles, list):
        styles = [styles]

    codes = []
    for style in styles:
        if isinstance(style, str):
            # Convert string to TextStyle enum
            try:
                style_enum = TextStyle(style.lower())
            except ValueError:
                available = [s.value for s in TextStyle]
                raise ValueError(
                    f"Unknown style '{style}'. Available: {', '.join(available)}"
                )
        elif isinstance(style, TextStyle):
            style_enum = style
        else:
            raise ValueError(f"Invalid style type: {type(style)}")

        codes.append(STYLE_CODES[style_enum])

    return "".join(codes)


def combine_styles(*styles: Union[str, TextStyle]) -> str:
    """Combine multiple styles into a single ANSI code string.

    Args:
        *styles: Variable number of styles to combine

    Returns:
        Combined ANSI codes
    """
    return get_style_codes(list(styles))
