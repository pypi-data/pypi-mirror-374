"""Color utility functions for khx_color_text."""

from typing import Union, Tuple
from .predefined import get_predefined_color, PREDEFINED_COLORS
from .custom import hex_to_rgb, rgb_to_ansi, validate_hex


def get_color_ansi(color: Union[str, Tuple[int, int, int]]) -> str:
    """Get ANSI color code from various color formats.

    Args:
        color: Color in various formats:
            - Predefined color name (str): "red", "blue", etc.
            - Hex color (str): "#FF0000", "#f00"
            - RGB tuple: (255, 0, 0)

    Returns:
        ANSI color code string

    Raises:
        ValueError: If color format is invalid or unsupported
    """
    if isinstance(color, str):
        # Check if it's a hex color
        if color.startswith("#"):
            if not validate_hex(color):
                raise ValueError(f"Invalid hex color format: {color}")
            r, g, b = hex_to_rgb(color)
            return rgb_to_ansi(r, g, b)

        # Check if it's a predefined color
        if color.lower() in PREDEFINED_COLORS:
            return get_predefined_color(color.lower())

        raise ValueError(f"Unknown color: {color}")

    elif isinstance(color, tuple) and len(color) == 3:
        # RGB tuple
        r, g, b = color
        return rgb_to_ansi(r, g, b)

    else:
        raise ValueError(f"Unsupported color format: {color}")
