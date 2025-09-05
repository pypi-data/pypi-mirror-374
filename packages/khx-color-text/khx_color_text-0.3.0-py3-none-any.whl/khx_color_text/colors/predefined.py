"""Predefined color definitions for khx_color_text."""

from colorama import Fore

# Extended set of predefined colors
PREDEFINED_COLORS = {
    # Basic colors
    "red": Fore.RED,
    "green": Fore.GREEN,
    "blue": Fore.BLUE,
    "yellow": Fore.YELLOW,
    "cyan": Fore.CYAN,
    "magenta": Fore.MAGENTA,
    "white": Fore.WHITE,
    "black": Fore.BLACK,
    # Bright colors
    "bright_red": Fore.LIGHTRED_EX,
    "bright_green": Fore.LIGHTGREEN_EX,
    "bright_blue": Fore.LIGHTBLUE_EX,
    "bright_yellow": Fore.LIGHTYELLOW_EX,
    "bright_cyan": Fore.LIGHTCYAN_EX,
    "bright_magenta": Fore.LIGHTMAGENTA_EX,
    "bright_white": Fore.LIGHTWHITE_EX,
    "bright_black": Fore.LIGHTBLACK_EX,
    # Aliases for convenience
    "orange": Fore.LIGHTYELLOW_EX,
    "purple": Fore.MAGENTA,
    "pink": Fore.LIGHTMAGENTA_EX,
    "gray": Fore.LIGHTBLACK_EX,
    "grey": Fore.LIGHTBLACK_EX,
}


def get_predefined_color(color_name: str) -> str:
    """Get ANSI code for a predefined color.

    Args:
        color_name: Name of the predefined color

    Returns:
        ANSI color code

    Raises:
        ValueError: If color name is not found
    """
    if color_name not in PREDEFINED_COLORS:
        available = ", ".join(sorted(PREDEFINED_COLORS.keys()))
        raise ValueError(
            f"Unknown predefined color '{color_name}'. Available: {available}"
        )

    return PREDEFINED_COLORS[color_name]
