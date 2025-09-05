"""Color definitions and mappings for khx_color_text."""

from colorama import Fore

# Exactly five supported colors
ALLOWED_COLORS = {"red", "green", "blue", "yellow", "cyan"}

# Mapping from color name to ANSI code
COLOR_MAP = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "blue": Fore.BLUE,
    "yellow": Fore.YELLOW,
    "cyan": Fore.CYAN,
}