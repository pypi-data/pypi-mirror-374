"""Command-line interface for khx_color_text."""

import argparse
from .core import cprint
from .colors import ALLOWED_COLORS

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Print colored text to the terminal",
        prog="khx-ct"
    )
    parser.add_argument("text", help="Text to print")
    parser.add_argument(
        "--color", 
        choices=list(ALLOWED_COLORS),
        default="cyan",
        help="Color to use (default: cyan)"
    )
    
    args = parser.parse_args()
    cprint(args.text, args.color)

if __name__ == "__main__":
    main()