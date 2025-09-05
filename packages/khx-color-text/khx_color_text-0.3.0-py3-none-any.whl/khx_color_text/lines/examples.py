"""Examples demonstrating the lines module functionality."""

from .core import (
    cline,
    solid_line,
    dashed_line,
    dotted_line,
    wave_line,
    double_line,
    star_line,
)
from .characters import get_char, list_chars


def demo_basic_lines():
    """Demonstrate basic line functionality."""
    print("=== Basic Lines Demo ===\n")

    print("1. Default line (fills terminal):")
    cline()

    print("\n2. Custom width:")
    cline(width=50)

    print("\n3. Different characters:")
    cline("*")
    cline("=")
    cline("~")
    cline("█")

    print("\n4. With colors:")
    cline("*", color="#FF0000")
    cline("=", color="blue", bg_color="yellow")
    cline("█", color="#FFFFFF", bg_color="#FF0000")


def demo_predefined_styles():
    """Demonstrate predefined line styles."""
    print("\n=== Predefined Styles Demo ===\n")

    print("1. Solid line:")
    solid_line(color="#FF0000")

    print("\n2. Dashed line:")
    dashed_line(color="#00FF00")

    print("\n3. Dotted line:")
    dotted_line(color="#0000FF")

    print("\n4. Wave line:")
    wave_line(color="#FF00FF")

    print("\n5. Double line:")
    double_line(color="#FFFF00")

    print("\n6. Star line:")
    star_line(color="#00FFFF")


def demo_character_lookup():
    """Demonstrate character lookup functionality."""
    print("\n=== Character Lookup Demo ===\n")

    print("1. Using character names directly in cline:")
    cline("full_block", width=30, color="#FF0000")
    cline("wave_dash", width=30, color="#00FF00")
    cline("black_diamond", width=30, color="#0000FF")

    print("\n2. Comparing direct chars vs names:")
    print("   Direct: ", end="")
    cline("*", width=20, color="#FF0000")
    print("   Named:  ", end="")
    cline("asterisk", width=20, color="#FF0000")

    print("\n3. Available basic characters:")
    basic_chars = list_chars("basic")
    for name, char in list(basic_chars.items())[:5]:  # Show first 5
        print(f"   {name}: {char}")

    print("\n4. Available decorative characters:")
    decorative_chars = list_chars("decorative")
    for name, char in list(decorative_chars.items())[:5]:  # Show first 5
        print(f"   {name}: {char}")

    print("\n5. Mathematical symbols by name:")
    cline("infinity", width=25, color="#9370DB")
    cline("summation", width=25, color="#32CD32")
    cline("integral", width=25, color="#FF69B4")


def demo_character_names():
    """Demonstrate using character names with IDE autocomplete support."""
    print("\n=== Character Names Demo ===\n")

    print("1. Basic characters by name:")
    cline("asterisk", width=30, color="#FF0000")
    cline("equals", width=30, color="#00FF00")
    cline("underscore", width=30, color="#0000FF")

    print("\n2. Block characters:")
    cline("full_block", width=30, color="#FF00FF")
    cline("dark_shade", width=30, color="#FFFF00")
    cline("light_shade", width=30, color="#00FFFF")

    print("\n3. Unicode box drawing:")
    cline("horizontal", width=30, color="#FF8000")
    cline("heavy_horizontal", width=30, color="#8000FF")
    cline("double_horizontal", width=30, color="#FF0080")

    print("\n4. Decorative characters:")
    cline("black_star", width=30, color="#FFD700")
    cline("heart_suit", width=30, color="#FF1493")
    cline("diamond_suit", width=30, color="#FF6347")


def demo_advanced_styling():
    """Demonstrate advanced styling options."""
    print("\n=== Advanced Styling Demo ===\n")

    print("1. Bold and underlined:")
    cline("equals", width=40, color="#FF0000", style=["bold", "underline"])

    print("\n2. Italic with background:")
    cline("tilde", width=40, color="#FFFFFF", bg_color="#0000FF", style="italic")

    print("\n3. Multiple styles:")
    cline(
        "black_star", width=40, color="#FFD700", style=["bold", "italic", "underline"]
    )


def run_all_demos():
    """Run all demonstration functions."""
    demo_basic_lines()
    demo_predefined_styles()
    demo_character_lookup()
    demo_character_names()
    demo_advanced_styling()

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    run_all_demos()
