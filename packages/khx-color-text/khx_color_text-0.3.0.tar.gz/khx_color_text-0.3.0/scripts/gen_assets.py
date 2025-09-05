"""Generate comprehensive, large, and visually impressive SVG assets for documentation."""

import os
import sys
from pathlib import Path

# Add the src directory to Python path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.align import Align
from rich.theme import Theme
from khx_color_text.colors.predefined import PREDEFINED_COLORS


def create_large_font_console(width=200, height=80):
    """Create a Rich console with larger font size for better visibility."""
    return Console(record=True, width=width, height=height)

def export_large_font_svg(console, title, font_size=24):
    """Export SVG with much larger font size for maximum visibility."""
    svg_content = console.export_svg(title=title)
    
    # Increase font size in the SVG for maximum visibility
    svg_content = svg_content.replace('font-size="14"', f'font-size="{font_size}"')
    svg_content = svg_content.replace('font-size:14px', f'font-size:{font_size}px')
    svg_content = svg_content.replace('font-size="12"', f'font-size="{font_size}"')
    svg_content = svg_content.replace('font-size:12px', f'font-size:{font_size}px')
    svg_content = svg_content.replace('font-size="16"', f'font-size="{font_size}"')
    svg_content = svg_content.replace('font-size:16px', f'font-size:{font_size}px')
    
    # Also increase line height for better readability
    line_height = font_size * 1.3
    svg_content = svg_content.replace('dy="1.2em"', f'dy="{line_height/font_size:.1f}em"')
    
    return svg_content

def generate_svg_assets():
    """Generate large, comprehensive SVG previews for every feature and example."""
    # Create assets directory if it doesn't exist
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Define pure, vibrant colors for better visual impact
    pure_colors = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        "white": "#FFFFFF",
        "black": "#000000",
        "bright_red": "#FF5555",
        "bright_green": "#55FF55",
        "bright_blue": "#5555FF",
        "bright_yellow": "#FFFF55",
        "bright_cyan": "#55FFFF",
        "bright_magenta": "#FF55FF",
        "bright_white": "#FFFFFF",
        "bright_black": "#555555",
        "orange": "#FFA500",
        "purple": "#800080",
        "pink": "#FFC0CB",
        "gray": "#808080",
        "grey": "#808080",
    }

    generated_files = []

    # 1. EXTRA LARGE MAIN SHOWCASE
    print("🎨 Generating EXTRA LARGE main showcase...")
    console = create_large_font_console(width=200, height=80)

    # Title
    title = Text(
        "🎨 khx_color_text v0.2.0 - Comprehensive Terminal Styling",
        style="bold bright_blue",
    )
    console.print(Align.center(title))
    console.print()

    # Feature highlights
    console.print("✨ FEATURES:", style="bold bright_green")
    features = [
        "• 21+ Predefined Colors (basic, bright, aliases)",
        "• Hex Colors (#FF0000, #f00)",
        "• RGB Colors (255, 0, 0)",
        "• 6 Text Styles (bold, italic, underline, strikethrough, dim, bright)",
        "• Background Colors in all formats",
        "• Single cprint() API for everything",
    ]
    for feature in features:
        console.print(f"  {feature}", style="bright_white")
    console.print()

    # Color demonstration
    console.print("🌈 COLOR FORMATS:", style="bold bright_yellow")
    console.print("  Predefined: ", end="", style="bright_white")
    for color in ["red", "green", "blue", "yellow", "cyan", "magenta"]:
        console.print(f"{color} ", style=pure_colors[color], end="")
    console.print()

    console.print("  Hex Colors: ", end="", style="bright_white")
    hex_colors = ["#FF6B35", "#8A2BE2", "#FFD700", "#32CD32", "#FF1493"]
    for hex_color in hex_colors:
        console.print(f"{hex_color} ", style=hex_color, end="")
    console.print()

    console.print("  RGB Colors: ", end="", style="bright_white")
    rgb_colors = [
        (255, 107, 53),
        (138, 43, 226),
        (255, 215, 0),
        (50, 205, 50),
        (255, 20, 147),
    ]
    for i, (r, g, b) in enumerate(rgb_colors):
        hex_equiv = hex_colors[i]
        console.print(f"({r},{g},{b}) ", style=hex_equiv, end="")
    console.print()
    console.print()

    # Style demonstration
    console.print("✍️ TEXT STYLES:", style="bold bright_cyan")
    styles = [
        ("bold", "bold"),
        ("italic", "italic"),
        ("underline", "underline"),
        ("strikethrough", "strike"),
        ("dim", "dim"),
    ]
    for style_name, rich_style in styles:
        console.print(f"  {style_name}: ", end="", style="bright_white")
        console.print(f"This text is {style_name}", style=f"blue {rich_style}")
    # Handle bright separately
    console.print(f"  bright: ", end="", style="bright_white")
    console.print(f"This text is bright", style="bright_blue")
    console.print()

    # Background demonstration
    console.print("🌟 BACKGROUND COLORS:", style="bold bright_magenta")
    bg_examples = [
        ("white", "red"),
        ("black", "yellow"),
        ("white", "blue"),
        ("yellow", "purple"),
    ]
    for text_color, bg_color in bg_examples:
        console.print(f"  {text_color} on {bg_color}: ", end="", style="bright_white")
        console.print(f"Highlighted Text", style=f"{text_color} on {bg_color}")

    svg_path = assets_dir / "main_showcase.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Main Showcase", font_size=28)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 2. EXTRA LARGE COLOR PALETTE SHOWCASE
    print("🎨 Generating EXTRA LARGE color palette...")
    console = create_large_font_console(width=180, height=60)

    console.print("🎨 COMPLETE COLOR PALETTE", style="bold bright_blue")
    console.print("=" * 50, style="bright_blue")
    console.print()

    # Basic colors
    console.print("📌 BASIC COLORS:", style="bold bright_green")
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
        console.print(f"  cprint('Hello World!', '{color}')", style="dim")
        console.print(f"  → Hello World!", style=pure_colors[color])
        console.print()

    # Bright colors
    console.print("✨ BRIGHT COLORS:", style="bold bright_yellow")
    bright_colors = [
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_yellow",
        "bright_cyan",
        "bright_magenta",
    ]
    for color in bright_colors:
        console.print(f"  cprint('Bright Text!', '{color}')", style="dim")
        console.print(f"  → Bright Text!", style=pure_colors[color])
        console.print()

    # Aliases
    console.print("🎭 COLOR ALIASES:", style="bold bright_cyan")
    aliases = ["orange", "purple", "pink", "gray"]
    for alias in aliases:
        console.print(f"  cprint('Alias Color!', '{alias}')", style="dim")
        console.print(f"  → Alias Color!", style=pure_colors[alias])
        console.print()

    svg_path = assets_dir / "color_palette_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Color Palette", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 3. EXTRA LARGE HEX COLOR DEMONSTRATION
    print("🌈 Generating EXTRA LARGE hex color demo...")
    console = create_large_font_console(width=180, height=55)

    console.print("🌈 HEX COLOR SUPPORT", style="bold bright_blue")
    console.print("=" * 40, style="bright_blue")
    console.print()

    hex_examples = [
        ("#FF0000", "Pure Red", "Vibrant and bold"),
        ("#00FF00", "Pure Green", "Fresh and natural"),
        ("#0000FF", "Pure Blue", "Cool and calming"),
        ("#FF6B35", "Orange", "Warm and energetic"),
        ("#8A2BE2", "Blue Violet", "Creative and mysterious"),
        ("#FFD700", "Gold", "Luxurious and premium"),
        ("#32CD32", "Lime Green", "Bright and lively"),
        ("#FF1493", "Deep Pink", "Bold and passionate"),
        ("#FF0000", "Short Red", "Compact hex format"),
        ("#00FF00", "Short Green", "3-digit hex support"),
    ]

    for hex_color, name, description in hex_examples:
        console.print(f"  cprint('Custom {name}', '{hex_color}')", style="dim")
        console.print(f"  → Custom {name} - {description}", style=hex_color)
        console.print()

    svg_path = assets_dir / "hex_colors_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Hex Colors", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 4. EXTRA LARGE RGB COLOR DEMONSTRATION
    print("🎨 Generating EXTRA LARGE RGB color demo...")
    console = create_large_font_console(width=180, height=55)

    console.print("🎨 RGB COLOR SUPPORT", style="bold bright_blue")
    console.print("=" * 40, style="bright_blue")
    console.print()

    rgb_examples = [
        ((255, 0, 0), "#FF0000", "Pure Red", "Maximum red intensity"),
        ((0, 255, 0), "#00FF00", "Pure Green", "Maximum green intensity"),
        ((0, 0, 255), "#0000FF", "Pure Blue", "Maximum blue intensity"),
        ((255, 107, 53), "#FF6B35", "Orange", "Warm orange blend"),
        ((138, 43, 226), "#8A2BE2", "Blue Violet", "Purple-blue mix"),
        ((255, 215, 0), "#FFD700", "Gold", "Rich golden color"),
        ((50, 205, 50), "#32CD32", "Lime Green", "Bright lime shade"),
        ((255, 20, 147), "#FF1493", "Deep Pink", "Vibrant pink tone"),
        ((128, 128, 128), "#808080", "Gray", "Neutral gray tone"),
        ((64, 64, 64), "#404040", "Dark Gray", "Subtle dark shade"),
    ]

    for rgb, hex_equiv, name, description in rgb_examples:
        console.print(f"  cprint('RGB {name}', {rgb})", style="dim")
        console.print(f"  → RGB {name} - {description}", style=hex_equiv)
        console.print()

    svg_path = assets_dir / "rgb_colors_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text RGB Colors", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 5. EXTRA LARGE TEXT STYLES DEMONSTRATION
    print("✍️ Generating EXTRA LARGE text styles demo...")
    console = create_large_font_console(width=180, height=60)

    console.print("✍️ TEXT STYLING OPTIONS", style="bold bright_blue")
    console.print("=" * 45, style="bright_blue")
    console.print()

    styles_demo = [
        ("bold", "bold", "Make text stand out with bold formatting"),
        ("italic", "italic", "Add emphasis with elegant italic text"),
        ("underline", "underline", "Highlight important text with underlines"),
        ("strikethrough", "strike", "Show corrections or deletions"),
        ("dim", "dim", "Subtle text for secondary information"),
        ("bright", "bright", "Enhanced visibility for key content"),
    ]

    for style_name, rich_style, description in styles_demo:
        console.print(f"📝 {style_name.upper()} STYLE:", style="bold bright_green")
        console.print(
            f"  cprint('Styled text', 'blue', style='{style_name}')", style="dim"
        )
        if rich_style == "bright":
            console.print(f"  → Styled text - {description}", style="bright_blue")
        else:
            console.print(f"  → Styled text - {description}", style=f"blue {rich_style}")
        console.print()

    # Multiple styles
    console.print("🎪 MULTIPLE STYLES:", style="bold bright_yellow")
    multi_examples = [
        (["bold", "underline"], "bold underline", "Bold + Underline"),
        (["italic", "bright"], "italic bright", "Italic + Bright"),
        (["bold", "italic", "underline"], "bold italic underline", "All Combined"),
    ]

    for styles_list, rich_styles, description in multi_examples:
        console.print(
            f"  cprint('Multi-styled', 'green', style={styles_list})", style="dim"
        )
        # Handle bright style specially
        if "bright" in rich_styles:
            filtered_styles = rich_styles.replace("bright", "").strip()
            if filtered_styles:
                console.print(f"  → Multi-styled - {description}", style=f"bright_green {filtered_styles}")
            else:
                console.print(f"  → Multi-styled - {description}", style="bright_green")
        else:
            console.print(f"  → Multi-styled - {description}", style=f"green {rich_styles}")
        console.print()

    svg_path = assets_dir / "text_styles_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Text Styles", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 6. EXTRA LARGE BACKGROUND COLORS DEMONSTRATION
    print("🌟 Generating EXTRA LARGE background colors demo...")
    console = create_large_font_console(width=180, height=55)

    console.print("🌟 BACKGROUND COLOR SUPPORT", style="bold bright_blue")
    console.print("=" * 50, style="bright_blue")
    console.print()

    bg_examples = [
        ("white", "red", "High contrast for alerts"),
        ("black", "yellow", "Warning style combination"),
        ("white", "blue", "Professional information style"),
        ("black", "cyan", "Modern tech aesthetic"),
        ("yellow", "purple", "Creative and bold design"),
        ("white", "black", "Classic monochrome"),
        ("green", "black", "Terminal/matrix style"),
        ("white", "#FF6B35", "Custom hex background"),
        ("yellow", "#8A2BE2", "Hex purple background"),
        ("black", "#FFD700", "Golden highlight"),
    ]

    for text_color, bg_color, description in bg_examples:
        if bg_color.startswith("#"):
            console.print(
                f"  cprint('Highlighted', '{text_color}', bg_color='{bg_color}')",
                style="dim",
            )
        else:
            console.print(
                f"  cprint('Highlighted', '{text_color}', bg_color='{bg_color}')",
                style="dim",
            )
        console.print(
            f"  → Highlighted Text - {description}", style=f"{text_color} on {bg_color}"
        )
        console.print()

    svg_path = assets_dir / "background_colors_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Background Colors", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 7. EXTRA LARGE CLI DEMONSTRATION
    print("⚡ Generating EXTRA LARGE CLI demo...")
    console = create_large_font_console(width=180, height=65)

    console.print("⚡ COMMAND-LINE INTERFACE", style="bold bright_blue")
    console.print("=" * 45, style="bright_blue")
    console.print()

    cli_examples = [
        ("Basic Colors", "khx-ct 'Hello World!' -c red", "red"),
        ("Hex Colors", "khx-ct 'Custom Color' --hex '#FF6B35'", "#FF6B35"),
        ("RGB Colors", "khx-ct 'RGB Color' --rgb '255,0,0'", "#FF0000"),
        ("With Styling", "khx-ct 'Bold Text' -c blue -s bold", "blue"),
        ("Multiple Styles", "khx-ct 'Fancy' -c green -s bold,underline", "green"),
        ("Background", "khx-ct 'Highlighted' -c white --bg red", "white"),
        (
            "Complex",
            "khx-ct 'Ultimate' --hex '#00FF00' --bg-rgb '50,50,50' -s bold",
            "#00FF00",
        ),
    ]

    for category, command, color_style in cli_examples:
        console.print(f"📝 {category}:", style="bold bright_green")
        console.print(f"  $ {command}", style="dim")
        if category == "With Styling":
            console.print(f"  → Bold Text", style=f"{color_style} bold")
        elif category == "Multiple Styles":
            console.print(f"  → Fancy", style=f"{color_style} bold underline")
        elif category == "Background":
            console.print(f"  → Highlighted", style=f"{color_style} on red")
        elif category == "Complex":
            console.print(f"  → Ultimate", style=f"{color_style} bold on #323232")
        else:
            console.print(f"  → Output Text", style=color_style)
        console.print()

    # Built-in examples
    console.print("🎯 BUILT-IN EXAMPLES:", style="bold bright_yellow")
    builtin_commands = [
        "khx-ct --examples          # Show basic examples",
        "khx-ct --advanced-examples # Show advanced features",
        "khx-ct --showcase          # Complete feature demo",
        "khx-ct --list-colors       # List all colors",
    ]
    for cmd in builtin_commands:
        console.print(f"  $ {cmd}", style="bright_cyan")

    svg_path = assets_dir / "cli_demo_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text CLI Demo", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 8. EXTRA LARGE API EXAMPLES
    print("🔧 Generating EXTRA LARGE API examples...")
    console = create_large_font_console(width=180, height=70)

    console.print("🔧 PYTHON API EXAMPLES", style="bold bright_blue")
    console.print("=" * 40, style="bright_blue")
    console.print()

    console.print("📝 BASIC USAGE:", style="bold bright_green")
    console.print("from khx_color_text import cprint", style="dim")
    console.print()
    basic_examples = [
        ("cprint('Hello World!', 'red')", "red", "Hello World!"),
        ("cprint('Success!', 'green')", "green", "Success!"),
        ("cprint('Information', 'blue')", "blue", "Information"),
        ("cprint('Warning', 'yellow')", "yellow", "Warning"),
    ]
    for code, color, output in basic_examples:
        console.print(f"  {code}", style="dim")
        console.print(f"  → {output}", style=color)
        console.print()

    console.print("🌈 CUSTOM COLORS:", style="bold bright_yellow")
    custom_examples = [
        ("cprint('Orange', '#FF6B35')", "#FF6B35", "Orange"),
        ("cprint('Purple', (138, 43, 226))", "#8A2BE2", "Purple"),
        ("cprint('Gold', '#FFD700')", "#FFD700", "Gold"),
    ]
    for code, color, output in custom_examples:
        console.print(f"  {code}", style="dim")
        console.print(f"  → {output}", style=color)
        console.print()

    console.print("✍️ WITH STYLING:", style="bold bright_cyan")
    style_examples = [
        ("cprint('Bold', 'red', style='bold')", "red bold", "Bold"),
        ("cprint('Italic', 'green', style='italic')", "green italic", "Italic"),
        (
            "cprint('Multi', 'blue', style=['bold', 'underline'])",
            "blue bold underline",
            "Multi",
        ),
    ]
    for code, style, output in style_examples:
        console.print(f"  {code}", style="dim")
        console.print(f"  → {output}", style=style)
        console.print()

    console.print("🌟 WITH BACKGROUNDS:", style="bold bright_magenta")
    bg_examples = [
        ("cprint('Alert', 'white', bg_color='red')", "white on red", "Alert"),
        ("cprint('Warning', 'black', bg_color='yellow')", "black on yellow", "Warning"),
        ("cprint('Info', 'white', bg_color='blue')", "white on blue", "Info"),
    ]
    for code, style, output in bg_examples:
        console.print(f"  {code}", style="dim")
        console.print(f"  → {output}", style=style)
        console.print()

    svg_path = assets_dir / "api_examples_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text API Examples", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 9. EXTRA LARGE FEATURE COMPARISON
    print("📊 Generating EXTRA LARGE feature comparison...")
    console = create_large_font_console(width=180, height=55)

    console.print("📊 FEATURE COMPARISON: v0.1.0 → v0.2.0", style="bold bright_blue")
    console.print("=" * 60, style="bright_blue")
    console.print()

    # Create comparison table
    table = Table(show_header=True, header_style="bold bright_green")
    table.add_column("Feature", style="bright_white", width=25)
    table.add_column("v0.1.0", style="red", width=20)
    table.add_column("v0.2.0", style="bright_green", width=30)
    table.add_column("Improvement", style="bright_yellow", width=35)

    comparisons = [
        ("Colors", "5 basic", "21+ (basic, bright, aliases)", "4x more colors"),
        (
            "Color Formats",
            "Predefined only",
            "Predefined, Hex, RGB",
            "3 formats supported",
        ),
        ("Text Styles", "None", "6 styles + combinations", "Complete styling system"),
        ("Backgrounds", "None", "All color formats", "Full background support"),
        ("CLI Options", "3 basic", "15+ comprehensive", "5x more options"),
        ("Examples", "Basic", "3 comprehensive modules", "Rich example suite"),
        ("Documentation", "Minimal", "Enterprise-level", "Professional docs"),
        ("Testing", "Basic", "Cross-platform CI/CD", "Automated quality"),
    ]

    for feature, old, new, improvement in comparisons:
        table.add_row(feature, old, new, improvement)

    console.print(table)
    console.print()
    console.print(
        "🚀 Result: From simple 5-color tool to comprehensive terminal styling solution!",
        style="bold bright_green",
    )

    svg_path = assets_dir / "feature_comparison_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Feature Comparison", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # 10. EXTRA LARGE INSTALLATION DEMO
    print("📦 Generating EXTRA LARGE installation demo...")
    console = Console(record=True, width=180, height=50)

    console.print("📦 INSTALLATION & QUICK START", style="bold bright_blue")
    console.print("=" * 50, style="bright_blue")
    console.print()

    console.print("💻 INSTALLATION:", style="bold bright_green")
    console.print("  $ pip install khx_color_text", style="bright_cyan")
    console.print()

    console.print("⚡ QUICK TEST:", style="bold bright_yellow")
    console.print("  $ khx-ct 'Hello World!' -c red", style="dim")
    console.print("  → Hello World!", style="red")
    console.print()

    console.print("🐍 PYTHON USAGE:", style="bold bright_magenta")
    console.print("  from khx_color_text import cprint", style="dim")
    console.print("  cprint('Success!', 'green')", style="dim")
    console.print("  → Success!", style="green")
    console.print()

    console.print("🎯 ADVANCED FEATURES:", style="bold bright_cyan")
    console.print("  cprint('Custom', '#FF6B35', style='bold')", style="dim")
    console.print("  → Custom", style="#FF6B35 bold")
    console.print()

    console.print("📚 LEARN MORE:", style="bold bright_white")
    console.print("  $ khx-ct --showcase    # See all features", style="bright_green")
    console.print("  $ khx-ct --help        # Get help", style="bright_green")

    svg_path = assets_dir / "installation_demo_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Installation", font_size=26)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(svg_path)
    print(f"Generated: {svg_path}")

    # Generate individual large color previews
    print("\n🎨 Generating individual EXTRA LARGE color previews...")
    for color in sorted(PREDEFINED_COLORS.keys()):
        console = Console(record=True, width=150, height=25)

        hex_color = pure_colors.get(color, "#FFFFFF")

        console.print(f"🎨 COLOR: {color.upper()}", style="bold bright_blue")
        console.print("=" * 30, style="bright_blue")
        console.print()
        console.print(f"cprint('Example text', '{color}')", style="dim")
        console.print(f"→ Example text in {color}", style=hex_color)
        console.print()
        console.print(f"Hex equivalent: {hex_color}", style="bright_white")
        console.print(f"Usage: Perfect for {color} themed content", style="dim")

        svg_path = assets_dir / f"color_{color}_large.svg"
        svg_content = export_large_font_svg(console, f"khx_color_text {color}", font_size=24)

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        generated_files.append(svg_path)
        print(f"Generated: {svg_path}")

    # 11. EXTRA LARGE COMPREHENSIVE EXAMPLES SHOWCASE
    print("� GSenerating EXTRA LARGE comprehensive examples...")
    console = Console(record=True, width=200, height=100)
    
    console.print("🎯 COMPREHENSIVE USAGE EXAMPLES", style="bold bright_blue")
    console.print("=" * 80, style="bright_blue")
    console.print()
    
    # Basic usage section
    console.print("📝 BASIC USAGE PATTERNS:", style="bold bright_green")
    basic_examples = [
        ("Success message", "green", None, None),
        ("Error message", "red", None, None),
        ("Warning message", "yellow", None, None),
        ("Info message", "blue", None, None),
        ("Debug message", "cyan", None, None),
    ]
    
    for text, color, style, bg in basic_examples:
        console.print(f"  cprint('{text}', '{color}')", style="dim")
        console.print(f"  → {text}", style=color)
        console.print()
    
    # Advanced patterns
    console.print("🚀 ADVANCED PATTERNS:", style="bold bright_yellow")
    advanced_examples = [
        ("Bold Success", "green", "bold", None),
        ("Italic Warning", "yellow", "italic", None),
        ("Underlined Error", "red", "underline", None),
        ("Highlighted Alert", "white", None, "red"),
        ("Custom Hex Color", "#FF6B35", "bold", None),
        ("RGB Color", (138, 43, 226), "italic", None),
    ]
    
    for text, color, style, bg in advanced_examples:
        if isinstance(color, tuple):
            color_str = f"({color[0]}, {color[1]}, {color[2]})"
        else:
            color_str = f"'{color}'"
        
        style_str = f", style='{style}'" if style else ""
        bg_str = f", bg_color='{bg}'" if bg else ""
        
        console.print(f"  cprint('{text}', {color_str}{style_str}{bg_str})", style="dim")
        
        # Display the actual styled text
        if isinstance(color, tuple):
            # For RGB, we'll use a hex approximation for display
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            display_style = hex_color
        else:
            display_style = color
            
        if style:
            display_style = f"{display_style} {style}"
        if bg:
            display_style = f"{display_style} on {bg}"
            
        console.print(f"  → {text}", style=display_style)
        console.print()
    
    svg_path = assets_dir / "comprehensive_examples_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Comprehensive Examples", font_size=30)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")
    
    # 12. EXTRA LARGE STYLE COMBINATIONS SHOWCASE
    print("🎪 Generating EXTRA LARGE style combinations...")
    console = Console(record=True, width=200, height=80)
    
    console.print("🎪 STYLE COMBINATIONS SHOWCASE", style="bold bright_blue")
    console.print("=" * 80, style="bright_blue")
    console.print()
    
    # All possible style combinations
    styles = ["bold", "italic", "underline", "strikethrough", "dim", "bright"]
    colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
    
    console.print("🎨 SINGLE STYLES:", style="bold bright_green")
    for i, style in enumerate(styles):
        color = colors[i % len(colors)]
        console.print(f"  cprint('Text with {style}', '{color}', style='{style}')", style="dim")
        # Handle style name mapping for Rich
        rich_style = style
        if style == "strikethrough":
            rich_style = "strike"
        elif style == "bright":
            console.print(f"  → Text with {style}", style=f"bright_{color}")
            continue
        
        console.print(f"  → Text with {style}", style=f"{color} {rich_style}")
        console.print()
    
    console.print("🌟 DOUBLE COMBINATIONS:", style="bold bright_yellow")
    combinations = [
        (["bold", "italic"], "red"),
        (["bold", "underline"], "green"),
        (["italic", "underline"], "blue"),
        (["bold", "bright"], "yellow"),
        (["italic", "dim"], "cyan"),
        (["underline", "strikethrough"], "magenta"),
    ]
    
    for style_combo, color in combinations:
        style_str = ", ".join([f"'{s}'" for s in style_combo])
        console.print(f"  cprint('Combined styles', '{color}', style=[{style_str}])", style="dim")
        # Handle style name mapping for Rich
        rich_styles = []
        for s in style_combo:
            if s == "strikethrough":
                rich_styles.append("strike")
            elif s == "bright":
                # Skip bright in combinations, handle separately
                continue
            else:
                rich_styles.append(s)
        
        if "bright" in style_combo:
            combined_style = f"bright_{color} {' '.join(rich_styles)}"
        else:
            combined_style = f"{color} {' '.join(rich_styles)}"
        console.print(f"  → Combined styles", style=combined_style)
        console.print()
    
    svg_path = assets_dir / "style_combinations_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Style Combinations", font_size=30)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")
    
    # 13. EXTRA LARGE ERROR HANDLING SHOWCASE
    print("⚠️ Generating EXTRA LARGE error handling demo...")
    console = Console(record=True, width=180, height=60)
    
    console.print("⚠️ ERROR HANDLING & VALIDATION", style="bold bright_blue")
    console.print("=" * 70, style="bright_blue")
    console.print()
    
    console.print("✅ VALID INPUTS:", style="bold bright_green")
    valid_examples = [
        "cprint('Valid color', 'red')",
        "cprint('Valid hex', '#FF0000')",
        "cprint('Valid RGB', (255, 0, 0))",
        "cprint('Valid style', 'blue', style='bold')",
        "cprint('Valid background', 'white', bg_color='red')",
    ]
    
    for example in valid_examples:
        console.print(f"  {example}", style="bright_green")
        console.print(f"  → ✓ Works perfectly", style="green")
        console.print()
    
    console.print("❌ INVALID INPUTS (will raise ValueError):", style="bold bright_red")
    invalid_examples = [
        "cprint('Invalid color', 'notacolor')",
        "cprint('Invalid hex', '#GGGGGG')",
        "cprint('Invalid RGB', (300, 0, 0))",
        "cprint('Invalid style', 'blue', style='notastyle')",
    ]
    
    for example in invalid_examples:
        console.print(f"  {example}", style="bright_red")
        console.print(f"  → ❌ ValueError: Invalid input", style="red")
        console.print()
    
    svg_path = assets_dir / "error_handling_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Error Handling", font_size=28)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")
    
    # 14. EXTRA LARGE REAL-WORLD USE CASES
    print("🌍 Generating EXTRA LARGE real-world use cases...")
    console = Console(record=True, width=200, height=90)
    
    console.print("🌍 REAL-WORLD USE CASES", style="bold bright_blue")
    console.print("=" * 60, style="bright_blue")
    console.print()
    
    console.print("🔧 LOGGING & DEBUGGING:", style="bold bright_green")
    logging_examples = [
        ("INFO: Application started", "blue", None),
        ("SUCCESS: Database connected", "green", "bold"),
        ("WARNING: Low disk space", "yellow", None),
        ("ERROR: Connection failed", "red", "bold"),
        ("DEBUG: Processing user data", "cyan", "dim"),
        ("CRITICAL: System shutdown", "white", "bold", "red"),
    ]
    
    for text, color, style, *bg in logging_examples:
        bg_color = bg[0] if bg else None
        style_str = f", style='{style}'" if style else ""
        bg_str = f", bg_color='{bg_color}'" if bg_color else ""
        
        console.print(f"  cprint('{text}', '{color}'{style_str}{bg_str})", style="dim")
        
        display_style = color
        if style:
            if style == "bright":
                display_style = f"bright_{color}"
            else:
                display_style = f"{display_style} {style}"
        if bg_color:
            display_style = f"{display_style} on {bg_color}"
            
        console.print(f"  → {text}", style=display_style)
        console.print()
    
    console.print("🎮 USER INTERFACE ELEMENTS:", style="bold bright_yellow")
    ui_examples = [
        ("[ OK ]", "green", "bold"),
        ("[FAIL]", "red", "bold"),
        ("[SKIP]", "yellow", None),
        ("Loading...", "cyan", "dim"),
        ("Progress: 75%", "blue", "bold"),
        (">>> Input required", "magenta", "bright"),
    ]
    
    for text, color, style in ui_examples:
        style_str = f", style='{style}'" if style else ""
        console.print(f"  cprint('{text}', '{color}'{style_str})", style="dim")
        
        if style == "bright":
            display_style = f"bright_{color}"
        else:
            display_style = f"{color} {style}" if style else color
        console.print(f"  → {text}", style=display_style)
        console.print()
    
    console.print("📊 DATA VISUALIZATION:", style="bold bright_cyan")
    data_examples = [
        ("█████████░ 90%", "green", "bold"),
        ("████░░░░░░ 40%", "yellow", None),
        ("██░░░░░░░░ 20%", "red", None),
        ("▲ +15.3% Growth", "green", "bright"),
        ("▼ -5.2% Decline", "red", "bright"),
        ("● Status: Online", "green", "bold"),
    ]
    
    for text, color, style in data_examples:
        style_str = f", style='{style}'" if style else ""
        console.print(f"  cprint('{text}', '{color}'{style_str})", style="dim")
        
        if style == "bright":
            display_style = f"bright_{color}"
        else:
            display_style = f"{color} {style}" if style else color
        console.print(f"  → {text}", style=display_style)
        console.print()
    
    svg_path = assets_dir / "real_world_use_cases_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Real-World Use Cases", font_size=30)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")

    # 15. EXTRA LARGE ADVANCED CLI SHOWCASE
    print("🚀 Generating EXTRA LARGE advanced CLI showcase...")
    console = Console(record=True, width=200, height=100)
    
    console.print("🚀 ADVANCED CLI FEATURES", style="bold bright_blue")
    console.print("=" * 70, style="bright_blue")
    console.print()
    
    console.print("🎯 COMPLEX COMMAND EXAMPLES:", style="bold bright_green")
    cli_examples = [
        "khx-ct 'Success!' -c green -s bold",
        "khx-ct 'Warning!' --hex '#FFA500' -s italic,underline",
        "khx-ct 'Error!' --rgb '255,0,0' -s bold --bg black",
        "khx-ct 'Custom' --hex '#8A2BE2' --bg-hex '#FFD700' -s bright",
        "khx-ct 'Ultimate' --rgb '0,255,0' --bg-rgb '50,50,50' -s bold,italic,underline",
    ]
    
    for cmd in cli_examples:
        console.print(f"  $ {cmd}", style="bright_cyan")
        # Extract the text and show a preview
        text = cmd.split("'")[1]
        console.print(f"  → {text}", style="bright_white")
        console.print()
    
    console.print("📋 BUILT-IN HELP COMMANDS:", style="bold bright_yellow")
    help_commands = [
        ("khx-ct --help", "Show complete help information"),
        ("khx-ct --examples", "Display basic usage examples"),
        ("khx-ct --advanced-examples", "Show advanced feature examples"),
        ("khx-ct --showcase", "Complete feature demonstration"),
        ("khx-ct --list-colors", "List all available colors"),
        ("khx-ct --version", "Show version information"),
    ]
    
    for cmd, desc in help_commands:
        console.print(f"  $ {cmd}", style="bright_cyan")
        console.print(f"    {desc}", style="dim")
        console.print()
    
    console.print("⚡ PERFORMANCE FEATURES:", style="bold bright_magenta")
    perf_features = [
        "✓ Fast ANSI code generation",
        "✓ Efficient color validation",
        "✓ Minimal memory footprint",
        "✓ Cross-platform compatibility",
        "✓ No external dependencies",
        "✓ Optimized for high-frequency logging",
    ]
    
    for feature in perf_features:
        console.print(f"  {feature}", style="bright_green")
    
    svg_path = assets_dir / "advanced_cli_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Advanced CLI", font_size=30)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")
    
    # 16. EXTRA LARGE INTEGRATION EXAMPLES
    print("🔗 Generating EXTRA LARGE integration examples...")
    console = Console(record=True, width=200, height=100)
    
    console.print("🔗 INTEGRATION EXAMPLES", style="bold bright_blue")
    console.print("=" * 60, style="bright_blue")
    console.print()
    
    console.print("🐍 PYTHON FRAMEWORKS:", style="bold bright_green")
    framework_examples = [
        ("Flask Web App", "from khx_color_text import cprint\n@app.route('/')\ndef home():\n    cprint('Server started!', 'green', style='bold')", "green"),
        ("Django Management", "from khx_color_text import cprint\nclass Command(BaseCommand):\n    def handle(self, *args, **options):\n        cprint('Migration complete!', 'blue')", "blue"),
        ("FastAPI Logging", "from khx_color_text import cprint\n@app.on_event('startup')\nasync def startup():\n    cprint('API ready!', 'cyan', style='bright')", "cyan"),
    ]
    
    for title, code, color in framework_examples:
        console.print(f"📦 {title}:", style=f"bold {color}")
        for line in code.split('\n'):
            console.print(f"  {line}", style="dim")
        console.print()
    
    console.print("🛠️ DEVELOPMENT TOOLS:", style="bold bright_yellow")
    tool_examples = [
        ("Testing Framework", "import pytest\nfrom khx_color_text import cprint\n\ndef test_feature():\n    cprint('Test passed!', 'green')", "green"),
        ("Build Scripts", "#!/usr/bin/env python3\nfrom khx_color_text import cprint\n\ncprint('Build started...', 'blue')\n# build logic here\ncprint('Build complete!', 'green', style='bold')", "blue"),
        ("CI/CD Pipeline", "from khx_color_text import cprint\n\ndef deploy():\n    cprint('Deploying...', 'yellow')\n    # deployment logic\n    cprint('Deployed successfully!', 'green')", "yellow"),
    ]
    
    for title, code, color in tool_examples:
        console.print(f"⚙️ {title}:", style=f"bold {color}")
        for line in code.split('\n'):
            console.print(f"  {line}", style="dim")
        console.print()
    
    console.print("📊 MONITORING & ANALYTICS:", style="bold bright_cyan")
    monitoring_examples = [
        ("System Monitoring", "from khx_color_text import cprint\n\ndef check_system():\n    cpu = get_cpu_usage()\n    if cpu > 80:\n        cprint(f'High CPU: {cpu}%', 'red', style='bold')\n    else:\n        cprint(f'CPU OK: {cpu}%', 'green')", "red"),
        ("Log Analysis", "from khx_color_text import cprint\n\ndef analyze_logs():\n    errors = count_errors()\n    if errors > 0:\n        cprint(f'Found {errors} errors', 'red')\n    else:\n        cprint('No errors found', 'green')", "green"),
    ]
    
    for title, code, color in monitoring_examples:
        console.print(f"📈 {title}:", style=f"bold {color}")
        for line in code.split('\n'):
            console.print(f"  {line}", style="dim")
        console.print()
    
    svg_path = assets_dir / "integration_examples_extra_large.svg"
    svg_content = export_large_font_svg(console, "khx_color_text Integration Examples", font_size=30)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    generated_files.append(str(svg_path))
    print(f"Generated: {svg_path}")

    print(
        f"\n🎉 Successfully generated {len(generated_files)} EXTRA LARGE, impressive SVG files!"
    )
    print("📊 Asset Statistics:")
    print(f"  • Total files: {len(generated_files)}")
    print(f"  • EXTRA LARGE showcases: 16")
    print(f"  • Individual colors: {len(PREDEFINED_COLORS)}")
    print(f"  • All assets are EXTRA BIG and visually spectacular! 🎨")

    for file_path in generated_files:
        print(f"  - {file_path}")


if __name__ == "__main__":
    generate_svg_assets()
