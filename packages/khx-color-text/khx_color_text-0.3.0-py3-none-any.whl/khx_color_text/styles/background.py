"""Background color support for khx_color_text."""

from typing import Union, Tuple
from colorama import Back
from ..colors.utils import get_color_ansi
from ..colors.custom import hex_to_rgb, rgb_to_ansi, validate_hex
from ..colors.predefined import PREDEFINED_COLORS

# Background color mappings for predefined colors
BACKGROUND_COLORS = {
    "red": Back.RED,
    "green": Back.GREEN,
    "blue": Back.BLUE,
    "yellow": Back.YELLOW,
    "cyan": Back.CYAN,
    "magenta": Back.MAGENTA,
    "white": Back.WHITE,
    "black": Back.BLACK,
    "bright_red": Back.LIGHTRED_EX,
    "bright_green": Back.LIGHTGREEN_EX,
    "bright_blue": Back.LIGHTBLUE_EX,
    "bright_yellow": Back.LIGHTYELLOW_EX,
    "bright_cyan": Back.LIGHTCYAN_EX,
    "bright_magenta": Back.LIGHTMAGENTA_EX,
    "bright_white": Back.LIGHTWHITE_EX,
    "bright_black": Back.LIGHTBLACK_EX,
    # Aliases
    "orange": Back.LIGHTYELLOW_EX,
    "purple": Back.MAGENTA,
    "pink": Back.LIGHTMAGENTA_EX,
    "gray": Back.LIGHTBLACK_EX,
    "grey": Back.LIGHTBLACK_EX,
}


def get_background_ansi(color: Union[str, Tuple[int, int, int]]) -> str:
    """Get ANSI background color code from various color formats.

    Args:
        color: Color in various formats:
            - Predefined color name (str): "red", "blue", etc.
            - Hex color (str): "#FF0000", "#f00"
            - RGB tuple: (255, 0, 0)

    Returns:
        ANSI background color code string

    Raises:
        ValueError: If color format is invalid or unsupported
    """
    if isinstance(color, str):
        # Check if it's a hex color
        if color.startswith("#"):
            if not validate_hex(color):
                raise ValueError(f"Invalid hex color format: {color}")
            r, g, b = hex_to_rgb(color)
            return f"\033[48;2;{r};{g};{b}m"

        # Check if it's a predefined color
        if color.lower() in BACKGROUND_COLORS:
            return BACKGROUND_COLORS[color.lower()]

        raise ValueError(f"Unknown background color: {color}")

    elif isinstance(color, tuple) and len(color) == 3:
        # RGB tuple
        r, g, b = color
        if not all(0 <= val <= 255 for val in [r, g, b]):
            raise ValueError(
                f"Invalid RGB values: ({r}, {g}, {b}). Values must be 0-255."
            )
        return f"\033[48;2;{r};{g};{b}m"

    else:
        raise ValueError(f"Unsupported background color format: {color}")
