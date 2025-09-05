"""Advanced features tests for khx_color_text."""

import sys
from io import StringIO
from contextlib import redirect_stdout

# Add src to path for testing
sys.path.insert(0, "src")

from khx_color_text import cprint, TextStyle


def test_hex_colors():
    """Test hex color support."""
    print("Testing hex colors...")

    hex_colors = [
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FF6B35",  # Orange
        "#8A2BE2",  # Blue violet
        "#f00",  # Short red
        "#0f0",  # Short green
        "#00f",  # Short blue
    ]

    for hex_color in hex_colors:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing hex color {hex_color}", hex_color)

            result = output.getvalue()
            assert len(result) > 0, f"No output for hex color {hex_color}"
            print(f"✓ {hex_color} works correctly")
        except Exception as e:
            print(f"✗ {hex_color} failed: {e}")


def test_rgb_colors():
    """Test RGB color support."""
    print("\nTesting RGB colors...")

    rgb_colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 107, 53),  # Orange
        (138, 43, 226),  # Blue violet
        (128, 128, 128),  # Gray
    ]

    for rgb_color in rgb_colors:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing RGB color {rgb_color}", rgb_color)

            result = output.getvalue()
            assert len(result) > 0, f"No output for RGB color {rgb_color}"
            print(f"✓ {rgb_color} works correctly")
        except Exception as e:
            print(f"✗ {rgb_color} failed: {e}")


def test_text_styles():
    """Test text styling options."""
    print("\nTesting text styles...")

    styles = ["bold", "italic", "underline", "strikethrough", "dim", "bright"]

    for style in styles:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing {style} style", "blue", style=style)

            result = output.getvalue()
            assert len(result) > 0, f"No output for style {style}"
            print(f"✓ {style} works correctly")
        except Exception as e:
            print(f"✗ {style} failed: {e}")


def test_multiple_styles():
    """Test multiple text styles."""
    print("\nTesting multiple styles...")

    style_combinations = [
        ["bold", "underline"],
        ["italic", "bright"],
        ["bold", "italic", "underline"],
        [TextStyle.BOLD, TextStyle.ITALIC],
    ]

    for styles in style_combinations:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(f"Testing styles {styles}", "green", style=styles)

            result = output.getvalue()
            assert len(result) > 0, f"No output for styles {styles}"
            print(f"✓ {styles} works correctly")
        except Exception as e:
            print(f"✗ {styles} failed: {e}")


def test_background_colors():
    """Test background color support."""
    print("\nTesting background colors...")

    bg_tests = [
        ("white", "red"),
        ("black", "yellow"),
        ("white", "#8A2BE2"),
        ("yellow", (50, 50, 50)),
    ]

    for text_color, bg_color in bg_tests:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(
                    f"Text: {text_color}, BG: {bg_color}", text_color, bg_color=bg_color
                )

            result = output.getvalue()
            assert len(result) > 0, f"No output for text={text_color}, bg={bg_color}"
            print(f"✓ Text: {text_color}, BG: {bg_color} works correctly")
        except Exception as e:
            print(f"✗ Text: {text_color}, BG: {bg_color} failed: {e}")


def test_complex_combinations():
    """Test complex feature combinations."""
    print("\nTesting complex combinations...")

    combinations = [
        {
            "text": "Bold white on red",
            "color": "white",
            "bg_color": "red",
            "style": "bold",
        },
        {
            "text": "Italic hex with hex background",
            "color": "#00FF00",
            "bg_color": "#FF0000",
            "style": "italic",
        },
        {
            "text": "RGB text, RGB bg, multiple styles",
            "color": (255, 255, 0),
            "bg_color": (128, 0, 128),
            "style": ["bold", "underline"],
        },
    ]

    for combo in combinations:
        try:
            output = StringIO()
            with redirect_stdout(output):
                cprint(
                    combo["text"],
                    combo["color"],
                    bg_color=combo.get("bg_color"),
                    style=combo.get("style"),
                )

            result = output.getvalue()
            assert len(result) > 0, f"No output for combination {combo['text']}"
            print(f"✓ {combo['text']} works correctly")
        except Exception as e:
            print(f"✗ {combo['text']} failed: {e}")


def test_invalid_inputs():
    """Test invalid input handling."""
    print("\nTesting invalid inputs...")

    invalid_tests = [
        ("Invalid hex", "#GGGGGG"),
        ("Invalid RGB", (256, 0, 0)),
        ("Invalid style", "invalid_style"),
        ("Invalid bg hex", "#ZZZZZZ"),
    ]

    for test_name, invalid_input in invalid_tests:
        try:
            if test_name == "Invalid hex":
                cprint("Test", invalid_input)
            elif test_name == "Invalid RGB":
                cprint("Test", invalid_input)
            elif test_name == "Invalid style":
                cprint("Test", "red", style=invalid_input)
            elif test_name == "Invalid bg hex":
                cprint("Test", "white", bg_color=invalid_input)

            print(f"✗ {test_name} should have raised ValueError")
        except ValueError:
            print(f"✓ {test_name} correctly raised ValueError")
        except Exception as e:
            print(f"✗ {test_name} raised unexpected exception: {e}")


if __name__ == "__main__":
    print("=== Advanced Features Tests ===")
    test_hex_colors()
    test_rgb_colors()
    test_text_styles()
    test_multiple_styles()
    test_background_colors()
    test_complex_combinations()
    test_invalid_inputs()
    print("\n=== All Advanced Tests Completed ===")
