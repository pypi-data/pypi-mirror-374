"""khx_color_text - A comprehensive package for printing colored and styled text in the terminal."""

from .core import cprint
from .colors.predefined import PREDEFINED_COLORS
from .styles.text_styles import TextStyle
from .lines import cline

__version__ = "0.3.0"
__all__ = ["cprint", "PREDEFINED_COLORS", "TextStyle", "cline"]
