"""Color showcase examples for khx_color_text."""

import sys
from pathlib import Path

# Add src to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from khx_color_text import cprint, PREDEFINED_COLORS


def run_color_showcase():
    """Show all available predefined colors."""
    print("=== All Predefined Colors Showcase ===")

    # Group colors by category
    basic_colors = [
        "red",
        "green",
        "blue",
        "yellow",
        "cyan",
        "magenta",
        "white",
        "black",
    ]
    bright_colors = [
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_yellow",
        "bright_cyan",
        "bright_magenta",
        "bright_white",
        "bright_black",
    ]
    aliases = ["orange", "purple", "pink", "gray", "grey"]

    print("\n--- Basic Colors ---")
    for color in basic_colors:
        if color in PREDEFINED_COLORS:
            cprint(f"This is {color} text", color)

    print("\n--- Bright Colors ---")
    for color in bright_colors:
        if color in PREDEFINED_COLORS:
            cprint(f"This is {color} text", color)

    print("\n--- Color Aliases ---")
    for color in aliases:
        if color in PREDEFINED_COLORS:
            cprint(f"This is {color} text", color)

    print("\n=== Style Showcase ===")
    styles = ["bold", "italic", "underline", "strikethrough", "dim", "bright"]
    for style in styles:
        cprint(f"This text is {style}", "blue", style=style)

    print("\n=== Background Showcase ===")
    bg_demos = [
        ("white", "red"),
        ("black", "yellow"),
        ("white", "blue"),
        ("black", "cyan"),
        ("yellow", "purple"),
        ("white", "black"),
    ]

    for text_color, bg_color in bg_demos:
        cprint(f"{text_color} on {bg_color}", text_color, bg_color=bg_color)

    print("\n=== Hex and RGB Demo ===")
    hex_colors = ["#FF0000", "#00FF00", "#0000FF", "#FF6B35", "#8A2BE2", "#FFD700"]
    rgb_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 107, 53),
        (138, 43, 226),
        (255, 215, 0),
    ]

    print("Hex colors:")
    for hex_color in hex_colors:
        cprint(f"Color {hex_color}", hex_color)

    print("\nRGB colors:")
    for rgb_color in rgb_colors:
        cprint(f"Color {rgb_color}", rgb_color)


if __name__ == "__main__":
    run_color_showcase()
