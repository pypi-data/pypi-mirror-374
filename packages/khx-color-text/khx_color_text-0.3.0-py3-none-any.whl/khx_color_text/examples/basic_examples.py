"""Basic usage examples for khx_color_text."""

import sys
from pathlib import Path

# Add src to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from khx_color_text import cprint


def run_basic_examples():
    """Demonstrate basic cprint usage."""
    print("=== Basic Color Examples ===")

    # Basic predefined colors
    cprint("Red text", "red")
    cprint("Green text", "green")
    cprint("Blue text", "blue")
    cprint("Yellow text", "yellow")
    cprint("Cyan text", "cyan")
    cprint("Magenta text", "magenta")

    print("\n=== Bright Colors ===")
    cprint("Bright red", "bright_red")
    cprint("Bright green", "bright_green")
    cprint("Bright blue", "bright_blue")

    print("\n=== Color Aliases ===")
    cprint("Orange text", "orange")
    cprint("Purple text", "purple")
    cprint("Pink text", "pink")
    cprint("Gray text", "gray")


if __name__ == "__main__":
    run_basic_examples()
