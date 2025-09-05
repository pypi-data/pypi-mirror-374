"""Core functionality for colored text printing."""

import sys
from typing import Literal
import colorama
from .colors import ALLOWED_COLORS, COLOR_MAP

# Initialize colorama for cross-platform support
colorama.init(autoreset=True)

def cprint(text: str, color: Literal["red", "green", "blue", "yellow", "cyan"]) -> None:
    """Print colored text to the terminal.
    
    Args:
        text: The text to print
        color: The color to use (red, green, blue, yellow, cyan)
        
    Raises:
        ValueError: If color is not one of the allowed colors
    """
    if color not in ALLOWED_COLORS:
        allowed = ", ".join(sorted(ALLOWED_COLORS))
        raise ValueError(f"Invalid color '{color}'. Allowed colors: {allowed}")
    
    # Print with color and reset
    ansi_code = COLOR_MAP[color]
    print(f"{ansi_code}{text}{colorama.Style.RESET_ALL}")