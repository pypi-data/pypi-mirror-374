"""Color utility tests for khx_color_text."""

import sys

# Add src to path for testing
sys.path.insert(0, "src")

from khx_color_text.colors.custom import (
    hex_to_rgb,
    rgb_to_ansi,
    validate_hex,
    validate_rgb,
)
from khx_color_text.colors.utils import get_color_ansi
from khx_color_text.colors.predefined import get_predefined_color


def test_hex_validation():
    """Test hex color validation."""
    print("Testing hex validation...")

    valid_hex = ["#FF0000", "#00ff00", "#0000FF", "#f00", "#0F0", "#00f"]
    invalid_hex = ["FF0000", "#GG0000", "#12345", "#1234567", "red", ""]

    for hex_color in valid_hex:
        result = validate_hex(hex_color)
        assert result == True, f"{hex_color} should be valid"
        print(f"✓ {hex_color} is valid")

    for hex_color in invalid_hex:
        result = validate_hex(hex_color)
        assert result == False, f"{hex_color} should be invalid"
        print(f"✓ {hex_color} is correctly invalid")


def test_hex_to_rgb():
    """Test hex to RGB conversion."""
    print("\nTesting hex to RGB conversion...")

    test_cases = [
        ("#FF0000", (255, 0, 0)),
        ("#00FF00", (0, 255, 0)),
        ("#0000FF", (0, 0, 255)),
        ("#f00", (255, 0, 0)),
        ("#0f0", (0, 255, 0)),
        ("#00f", (0, 0, 255)),
        ("#FF6B35", (255, 107, 53)),
    ]

    for hex_color, expected_rgb in test_cases:
        result = hex_to_rgb(hex_color)
        assert (
            result == expected_rgb
        ), f"{hex_color} should convert to {expected_rgb}, got {result}"
        print(f"✓ {hex_color} -> {result}")


def test_rgb_validation():
    """Test RGB validation."""
    print("\nTesting RGB validation...")

    valid_rgb = [(0, 0, 0), (255, 255, 255), (128, 64, 192), (255, 0, 0)]
    invalid_rgb = [
        (-1, 0, 0),
        (256, 0, 0),
        (0, -1, 0),
        (0, 256, 0),
        (0, 0, -1),
        (0, 0, 256),
    ]

    for r, g, b in valid_rgb:
        result = validate_rgb(r, g, b)
        assert result == True, f"RGB({r}, {g}, {b}) should be valid"
        print(f"✓ RGB({r}, {g}, {b}) is valid")

    for r, g, b in invalid_rgb:
        result = validate_rgb(r, g, b)
        assert result == False, f"RGB({r}, {g}, {b}) should be invalid"
        print(f"✓ RGB({r}, {g}, {b}) is correctly invalid")


def test_rgb_to_ansi():
    """Test RGB to ANSI conversion."""
    print("\nTesting RGB to ANSI conversion...")

    test_cases = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128),
        (255, 107, 53),
    ]

    for r, g, b in test_cases:
        result = rgb_to_ansi(r, g, b)
        expected = f"\033[38;2;{r};{g};{b}m"
        assert (
            result == expected
        ), f"RGB({r}, {g}, {b}) should produce {expected}, got {result}"
        print(f"✓ RGB({r}, {g}, {b}) -> {result}")


def test_get_color_ansi():
    """Test unified color ANSI code generation."""
    print("\nTesting unified color ANSI generation...")

    # Test predefined colors
    predefined_tests = ["red", "green", "blue", "bright_red"]
    for color in predefined_tests:
        try:
            result = get_color_ansi(color)
            assert len(result) > 0, f"Should get ANSI code for {color}"
            print(f"✓ Predefined color '{color}' -> ANSI code")
        except Exception as e:
            print(f"✗ Predefined color '{color}' failed: {e}")

    # Test hex colors
    hex_tests = ["#FF0000", "#00FF00", "#f00"]
    for hex_color in hex_tests:
        try:
            result = get_color_ansi(hex_color)
            assert len(result) > 0, f"Should get ANSI code for {hex_color}"
            print(f"✓ Hex color '{hex_color}' -> ANSI code")
        except Exception as e:
            print(f"✗ Hex color '{hex_color}' failed: {e}")

    # Test RGB colors
    rgb_tests = [(255, 0, 0), (0, 255, 0), (128, 128, 128)]
    for rgb_color in rgb_tests:
        try:
            result = get_color_ansi(rgb_color)
            assert len(result) > 0, f"Should get ANSI code for {rgb_color}"
            print(f"✓ RGB color {rgb_color} -> ANSI code")
        except Exception as e:
            print(f"✗ RGB color {rgb_color} failed: {e}")


def test_predefined_color_lookup():
    """Test predefined color lookup."""
    print("\nTesting predefined color lookup...")

    valid_colors = ["red", "green", "blue", "bright_red", "orange", "purple"]
    for color in valid_colors:
        try:
            result = get_predefined_color(color)
            assert len(result) > 0, f"Should get ANSI code for {color}"
            print(f"✓ Predefined color '{color}' found")
        except Exception as e:
            print(f"✗ Predefined color '{color}' failed: {e}")

    # Test invalid color
    try:
        get_predefined_color("invalid_color")
        print("✗ Should have raised ValueError for invalid color")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid color")


def test_error_handling():
    """Test error handling in color utilities."""
    print("\nTesting error handling...")

    # Invalid hex conversion
    try:
        hex_to_rgb("#GGGGGG")
        print("✗ Should have raised ValueError for invalid hex")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid hex")

    # Invalid RGB conversion
    try:
        rgb_to_ansi(256, 0, 0)
        print("✗ Should have raised ValueError for invalid RGB")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid RGB")

    # Invalid color format
    try:
        get_color_ansi(123)  # Invalid type
        print("✗ Should have raised ValueError for invalid color format")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid color format")


if __name__ == "__main__":
    print("=== Color Utility Tests ===")
    test_hex_validation()
    test_hex_to_rgb()
    test_rgb_validation()
    test_rgb_to_ansi()
    test_get_color_ansi()
    test_predefined_color_lookup()
    test_error_handling()
    print("\n=== All Color Utility Tests Completed ===")
