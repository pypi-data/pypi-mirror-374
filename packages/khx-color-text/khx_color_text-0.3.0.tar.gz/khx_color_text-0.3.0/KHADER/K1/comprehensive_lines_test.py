"""Comprehensive test showcasing all cline functionality with character names."""

from khx_color_text import cline


def test_character_names_showcase():
    """Showcase the new character names functionality."""
    print("🎨 COMPREHENSIVE CLINE SHOWCASE 🎨\n")

    # Header
    cline("double_horizontal", color="#FFD700", style="bold")
    print("   CHARACTER NAMES WITH IDE AUTOCOMPLETE SUPPORT")
    cline("double_horizontal", color="#FFD700", style="bold")

    print("\n1️⃣  BASIC CHARACTERS:")
    cline("asterisk", width=40, color="#FF0000")
    cline("equals", width=40, color="#00FF00")
    cline("dash", width=40, color="#0000FF")
    cline("underscore", width=40, color="#FF00FF")

    print("\n2️⃣  BLOCK CHARACTERS:")
    cline("full_block", width=40, color="#FFFFFF", bg_color="#FF0000")
    cline("dark_shade", width=40, color="#FFD700")
    cline("medium_shade", width=40, color="#00FFFF")
    cline("light_shade", width=40, color="#FF69B4")

    print("\n3️⃣  UNICODE BOX DRAWING:")
    cline("horizontal", width=40, color="#32CD32")
    cline("heavy_horizontal", width=40, color="#FF4500")
    cline("double_horizontal", width=40, color="#9370DB")
    cline("light_triple_dash", width=40, color="#20B2AA")

    print("\n4️⃣  WAVE PATTERNS:")
    cline("tilde", width=40, color="#FF1493")
    cline("wave_dash", width=40, color="#00CED1")
    cline("almost_equal", width=40, color="#FFB6C1")
    cline("triple_tilde", width=40, color="#98FB98")

    print("\n5️⃣  DECORATIVE CHARACTERS:")
    cline("black_star", width=40, color="#FFD700", style="bold")
    cline("black_diamond", width=40, color="#FF6347")
    cline("heart_suit", width=40, color="#FF1493", style="italic")
    cline("diamond_suit", width=40, color="#FF8C00")

    print("\n6️⃣  GEOMETRIC PATTERNS:")
    cline("black_up_triangle", width=40, color="#32CD32")
    cline("black_down_triangle", width=40, color="#4169E1")
    cline("black_left_pointer", width=20, color="#FF69B4")
    cline("black_right_pointer", width=20, color="#FF69B4")

    print("\n7️⃣  MATHEMATICAL SYMBOLS:")
    cline("infinity", width=40, color="#9370DB", style="bold")
    cline("summation", width=40, color="#32CD32")
    cline("integral", width=40, color="#FF4500")
    cline("square_root", width=40, color="#20B2AA")

    print("\n8️⃣  COMPARISON - DIRECT vs NAMES:")
    print("Direct chars: ", end="")
    cline("*", width=15, color="#FF0000")
    print("Named chars:  ", end="")
    cline("asterisk", width=15, color="#FF0000")

    print("Direct chars: ", end="")
    cline("█", width=15, color="#00FF00")
    print("Named chars:  ", end="")
    cline("full_block", width=15, color="#00FF00")

    print("\n9️⃣  ADVANCED STYLING:")
    cline(
        "black_star",
        width=50,
        color="#FFD700",
        bg_color="#000080",
        style=["bold", "underline"],
    )
    cline("wave_dash", width=50, color="#FFFFFF", bg_color="#FF0000", style=["italic"])
    cline(
        "infinity",
        width=50,
        color="#00FFFF",
        bg_color="#800080",
        style=["bold", "italic"],
    )

    print("\n🔟 TERMINAL WIDTH FILLING:")
    print("These lines automatically fill your terminal width:")
    cline("horizontal", color="#FF0000")
    cline("black_diamond", color="#00FF00")
    cline("wave_dash", color="#0000FF")

    # Footer
    print()
    cline("double_horizontal", color="#FFD700", style="bold")
    print("   ✨ ALL FEATURES DEMONSTRATED ✨")
    cline("double_horizontal", color="#FFD700", style="bold")

    print("\n💡 TIP: Your IDE should provide autocomplete for all character names!")
    print('   Try typing: cline("black_" and see the suggestions!')


if __name__ == "__main__":
    test_character_names_showcase()
