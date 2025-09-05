"""khx_color_text - A minimal package for printing colored text in the terminal."""

from .core import cprint
from .colors import ALLOWED_COLORS

__version__ = "0.1.0"
__all__ = ["cprint", "ALLOWED_COLORS"]