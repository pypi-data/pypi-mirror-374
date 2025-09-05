"""Basic functionality tests for khx_color_text."""

import sys
from io import StringIO
from contextlib import redirect_stdout

# Add src to path for testing
sys.path.insert(0, "src")

from khx_color_text import cprint, PREDEFINED_COLORS


def test_basic_colors():
    """Test basic predefined colors."""
    print("Testing basic predefined colors...")

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

    for color in basic_colors:
        if color in PREDEFINED_COLORS:
            # Capture output to verify no exceptions
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing {color}", color)

            result = output.getvalue()
            assert len(result) > 0, f"No output for color {color}"
            print(f"✓ {color} works correctly")
        else:
            print(f"✗ {color} not in PREDEFINED_COLORS")


def test_bright_colors():
    """Test bright color variants."""
    print("\nTesting bright colors...")

    bright_colors = [
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_yellow",
        "bright_cyan",
        "bright_magenta",
    ]

    for color in bright_colors:
        if color in PREDEFINED_COLORS:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing {color}", color)

            result = output.getvalue()
            assert len(result) > 0, f"No output for color {color}"
            print(f"✓ {color} works correctly")


def test_color_aliases():
    """Test color aliases."""
    print("\nTesting color aliases...")

    aliases = ["orange", "purple", "pink", "gray", "grey"]

    for alias in aliases:
        if alias in PREDEFINED_COLORS:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing {alias}", alias)

            result = output.getvalue()
            assert len(result) > 0, f"No output for alias {alias}"
            print(f"✓ {alias} works correctly")


def test_invalid_color():
    """Test invalid color handling."""
    print("\nTesting invalid color handling...")

    try:
        cprint("This should fail", "invalid_color")
        print("✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")


if __name__ == "__main__":
    print("=== Basic Functionality Tests ===")
    test_basic_colors()
    test_bright_colors()
    test_color_aliases()
    test_invalid_color()
    print("\n=== All Basic Tests Completed ===")
