"""Advanced usage examples for khx_color_text."""

import sys
from pathlib import Path

# Add src to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from khx_color_text import cprint, TextStyle


def run_advanced_examples():
    """Demonstrate advanced cprint features."""
    print("=== Hex Color Examples ===")
    cprint("Custom red (#FF0000)", "#FF0000")
    cprint("Custom green (#00FF00)", "#00FF00")
    cprint("Custom blue (#0000FF)", "#0000FF")
    cprint("Orange (#FF6B35)", "#FF6B35")
    cprint("Purple (#8A2BE2)", "#8A2BE2")
    cprint("Short hex (#f0f)", "#f0f")

    print("\n=== RGB Color Examples ===")
    cprint("RGB Red (255, 0, 0)", (255, 0, 0))
    cprint("RGB Green (0, 255, 0)", (0, 255, 0))
    cprint("RGB Blue (0, 0, 255)", (0, 0, 255))
    cprint("Custom RGB (255, 107, 53)", (255, 107, 53))
    cprint("Dark gray (64, 64, 64)", (64, 64, 64))

    print("\n=== Text Styling Examples ===")
    cprint("Bold text", "red", style="bold")
    cprint("Italic text", "green", style="italic")
    cprint("Underlined text", "blue", style="underline")
    cprint("Strikethrough text", "yellow", style="strikethrough")
    cprint("Dim text", "cyan", style="dim")
    cprint("Bright text", "magenta", style="bright")

    print("\n=== Multiple Styles ===")
    cprint("Bold and underlined", "red", style=["bold", "underline"])
    cprint("Italic and bright", "green", style=["italic", "bright"])
    cprint("All styles combined", "blue", style=["bold", "italic", "underline"])

    print("\n=== Background Colors ===")
    cprint("White text on red background", "white", bg_color="red")
    cprint("Black text on yellow background", "black", bg_color="yellow")
    cprint("White text on hex background", "white", bg_color="#8A2BE2")
    cprint("Yellow text on RGB background", "yellow", bg_color=(50, 50, 50))

    print("\n=== Complex Combinations ===")
    cprint("Bold white on red", "white", bg_color="red", style="bold")
    cprint(
        "Italic hex color with hex background",
        "#00FF00",
        bg_color="#FF0000",
        style="italic",
    )
    cprint(
        "RGB text, RGB background, multiple styles",
        (255, 255, 0),
        bg_color=(128, 0, 128),
        style=["bold", "underline"],
    )

    print("\n=== Using TextStyle Enum ===")
    cprint("Using TextStyle.BOLD", "red", style=TextStyle.BOLD)
    cprint("Multiple TextStyle enums", "blue", style=[TextStyle.BOLD, TextStyle.ITALIC])


if __name__ == "__main__":
    run_advanced_examples()
