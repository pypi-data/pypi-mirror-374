"""Command-line interface for khx_color_text."""

import argparse
import sys
from .core import cprint
from .colors.predefined import PREDEFINED_COLORS
from .examples import run_basic_examples, run_advanced_examples, run_color_showcase


def parse_rgb(rgb_str):
    """Parse RGB string like '255,0,0' to tuple."""
    try:
        parts = rgb_str.split(",")
        if len(parts) != 3:
            raise ValueError("RGB must have exactly 3 values")
        return tuple(int(x.strip()) for x in parts)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid RGB format: {rgb_str}. Use format: '255,0,0'"
        )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Print colored and styled text to the terminal",
        prog="khx-ct",
        epilog="""
Examples:
  khx-ct "Hello World" -c red
  khx-ct "Custom color" --hex "#FF6B35"
  khx-ct "RGB color" --rgb "255,107,53"
  khx-ct "Bold text" -c blue -s bold
  khx-ct "Multiple styles" -c green -s bold,underline
  khx-ct "With background" -c white --bg red
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("text", nargs="?", help="Text to print")

    # Color options (mutually exclusive)
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "-c", "--color", help="Predefined color name (e.g., red, blue, bright_green)"
    )
    color_group.add_argument("--hex", help="Hex color code (e.g., #FF0000, #f00)")
    color_group.add_argument(
        "--rgb", type=parse_rgb, help="RGB color values (e.g., '255,0,0')"
    )

    # Background color options
    bg_group = parser.add_mutually_exclusive_group()
    bg_group.add_argument("--bg", help="Background color (predefined name)")
    bg_group.add_argument("--bg-hex", help="Background hex color (e.g., #FF0000)")
    bg_group.add_argument(
        "--bg-rgb", type=parse_rgb, help="Background RGB values (e.g., '255,0,0')"
    )

    parser.add_argument(
        "-s",
        "--style",
        help="Text style(s): bold, italic, underline, strikethrough, dim, bright. Multiple styles: 'bold,underline'",
    )

    # Example commands
    parser.add_argument(
        "--examples", action="store_true", help="Show basic usage examples"
    )

    parser.add_argument(
        "--advanced-examples", action="store_true", help="Show advanced usage examples"
    )

    parser.add_argument(
        "--showcase", action="store_true", help="Show all available colors and styles"
    )

    parser.add_argument(
        "--list-colors", action="store_true", help="List all predefined color names"
    )

    parser.add_argument("--version", action="version", version="khx_color_text 0.2.0")

    args = parser.parse_args()

    # Handle example commands
    if args.examples:
        run_basic_examples()
        return

    if args.advanced_examples:
        run_advanced_examples()
        return

    if args.showcase:
        run_color_showcase()
        return

    if args.list_colors:
        print("Available predefined colors:")
        for color in sorted(PREDEFINED_COLORS.keys()):
            cprint(f"  {color}", color)
        return

    # Require text if not running examples
    if not args.text:
        parser.error(
            "Text argument is required unless using --examples, --advanced-examples, or --showcase"
        )

    try:
        # Determine color
        color = None
        if args.color:
            color = args.color
        elif args.hex:
            color = args.hex
        elif args.rgb:
            color = args.rgb

        # Determine background color
        bg_color = None
        if args.bg:
            bg_color = args.bg
        elif args.bg_hex:
            bg_color = args.bg_hex
        elif args.bg_rgb:
            bg_color = args.bg_rgb

        # Parse styles
        styles = None
        if args.style:
            styles = [s.strip() for s in args.style.split(",")]

        # Print with all options
        cprint(args.text, color=color, bg_color=bg_color, style=styles)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
