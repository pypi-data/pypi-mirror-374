"""Core functionality for colored text printing."""

import sys
from typing import Union, List, Tuple, Optional
import colorama
from .colors.utils import get_color_ansi
from .styles.text_styles import get_style_codes, TextStyle
from .styles.background import get_background_ansi

# Initialize colorama for cross-platform support
colorama.init(autoreset=True)


def cprint(
    text: str,
    color: Optional[Union[str, Tuple[int, int, int]]] = None,
    bg_color: Optional[Union[str, Tuple[int, int, int]]] = None,
    style: Optional[Union[str, List[str], TextStyle, List[TextStyle]]] = None,
    end: str = "\n",
    sep: str = " ",
    file=None,
) -> None:
    """Print colored and styled text to the terminal.

    This is the main API function that supports all customization features:
    - Multiple color formats: predefined names, hex codes, RGB tuples
    - Text styling: bold, italic, underline, strikethrough, dim, bright
    - Background colors in all supported formats
    - Standard print() parameters

    Args:
        text: The text to print
        color: Text color in various formats:
            - Predefined: "red", "blue", "bright_green", etc.
            - Hex: "#FF0000", "#f00"
            - RGB tuple: (255, 0, 0)
        bg_color: Background color (same formats as color)
        style: Text style(s):
            - Single: "bold", "italic", "underline", "strikethrough", "dim", "bright"
            - Multiple: ["bold", "underline"] or [TextStyle.BOLD, TextStyle.ITALIC]
        end: String appended after the text (default: newline)
        sep: String inserted between multiple text arguments (default: space)
        file: File object to write to (default: sys.stdout)

    Examples:
        # Basic usage
        cprint("Hello World", "red")

        # Hex colors
        cprint("Custom color", "#FF6B35")

        # RGB colors
        cprint("RGB color", (255, 107, 53))

        # With styling
        cprint("Bold red text", "red", style="bold")
        cprint("Multiple styles", "blue", style=["bold", "underline"])

        # With background
        cprint("Highlighted", "white", bg_color="red")

        # Complex example
        cprint("Fancy text", "#00FF00", bg_color=(50, 50, 50), style=["bold", "italic"])

    Raises:
        ValueError: If color format, style, or other parameters are invalid
    """
    if file is None:
        file = sys.stdout

    # Build the ANSI escape sequence
    ansi_codes = []

    # Add color
    if color is not None:
        ansi_codes.append(get_color_ansi(color))

    # Add background color
    if bg_color is not None:
        ansi_codes.append(get_background_ansi(bg_color))

    # Add styles
    if style is not None:
        ansi_codes.append(get_style_codes(style))

    # Combine all codes
    prefix = "".join(ansi_codes)

    # Print with formatting and reset
    formatted_text = f"{prefix}{text}{colorama.Style.RESET_ALL}"
    print(formatted_text, end=end, file=file)
