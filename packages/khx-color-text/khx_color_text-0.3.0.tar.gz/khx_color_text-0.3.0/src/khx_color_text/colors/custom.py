"""Custom color support (hex and RGB) for khx_color_text."""

import re
from typing import Tuple


def validate_hex(hex_color: str) -> bool:
    """Validate hex color format.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "#f00")

    Returns:
        True if valid hex color format
    """
    if not hex_color.startswith("#"):
        return False

    hex_part = hex_color[1:]
    if len(hex_part) == 3:
        return bool(re.match(r"^[0-9A-Fa-f]{3}$", hex_part))
    elif len(hex_part) == 6:
        return bool(re.match(r"^[0-9A-Fa-f]{6}$", hex_part))

    return False


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "#f00")

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Raises:
        ValueError: If hex color format is invalid
    """
    if not validate_hex(hex_color):
        raise ValueError(f"Invalid hex color format: {hex_color}")

    hex_part = hex_color[1:]

    # Handle 3-digit hex (e.g., #f00 -> #ff0000)
    if len(hex_part) == 3:
        hex_part = "".join([c * 2 for c in hex_part])

    r = int(hex_part[0:2], 16)
    g = int(hex_part[2:4], 16)
    b = int(hex_part[4:6], 16)

    return (r, g, b)


def validate_rgb(r: int, g: int, b: int) -> bool:
    """Validate RGB values.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        True if all values are valid
    """
    return all(0 <= val <= 255 for val in [r, g, b])


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape sequence.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        ANSI escape sequence for the RGB color

    Raises:
        ValueError: If RGB values are invalid
    """
    if not validate_rgb(r, g, b):
        raise ValueError(f"Invalid RGB values: ({r}, {g}, {b}). Values must be 0-255.")

    return f"\033[38;2;{r};{g};{b}m"
