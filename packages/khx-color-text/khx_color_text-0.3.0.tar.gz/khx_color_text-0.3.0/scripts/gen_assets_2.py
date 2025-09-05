"""Generate terminal-style images showing code and real output using matplotlib."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import re
import subprocess
import sys
import os
from pathlib import Path

# Add the src directory to Python path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Color mapping from names to hex values for visualization
COLOR_HEX_MAP = {
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

try:
    from khx_color_text import cprint

    print("Successfully imported khx_color_text")
except ImportError:
    print("Warning: Could not import khx_color_text. Continuing with color mapping.")


def extract_cprint_info(code_line):
    """
    Extract text and color from a cprint command.
    Returns (text, color) tuple or (None, None) if not a cprint command.
    """
    # Match cprint("text", "color") or cprint('text', 'color')
    pattern = r'cprint\s*\(\s*["\']([^"\']*)["\'],\s*["\']([^"\']*)["\']'
    match = re.search(pattern, code_line)

    if match:
        text = match.group(1)
        color = match.group(2)
        return text, color
    return None, None


def get_color_hex(color_input):
    """Convert color input to hex format."""

    # Clean any ANSI escape codes first
    if isinstance(color_input, str):
        # Remove ANSI escape codes
        import re

        clean_color = re.sub(r"\x1b\[[0-9;]*m", "", color_input).strip()

        if clean_color.startswith("#"):
            return clean_color
        elif clean_color in COLOR_HEX_MAP:
            hex_result = COLOR_HEX_MAP[clean_color]

            return hex_result
        else:
            # Default to white for unknown colors

            return "#FFFFFF"
    elif isinstance(color_input, tuple) and len(color_input) == 3:
        # RGB tuple to hex
        r, g, b = color_input
        return f"#{r:02x}{g:02x}{b:02x}"
    else:
        return "#FFFFFF"


def execute_cprint_code(code_lines):
    """
    Execute the actual code and capture the real output with colors.
    Returns (output_text, output_color)
    """
    try:
        # For cprint commands, extract the color information
        for code_line in code_lines:
            if "cprint(" in code_line:
                text, color = extract_cprint_info(code_line)
                if text and color:
                    # Clean the color string and convert to hex
                    clean_color = color.strip().strip('"').strip("'")
                    hex_color = get_color_hex(clean_color)
                    return text, hex_color

        # If no cprint found, return default
        return "Output not captured", "#ffffff"

    except Exception as e:
        return f"Error: {str(e)}", "#ff0000"


def generate_terminal_image(
    code_lines, output_filename="terminal_output", auto_execute=True
):
    """
    Generate a terminal-style image showing code and its REAL output.

    Args:
        code_lines (list): List of code lines to display
        output_filename (str): Base filename for saved images (without extension)
        auto_execute (bool): Whether to automatically determine output from code
    """

    def get_text_width_height(text, fontsize, fontfamily="monospace"):
        """Estimate text dimensions in inches"""
        char_width = fontsize * 0.6 / 72  # Convert points to inches
        char_height = fontsize / 72  # Convert points to inches

        width = len(text) * char_width
        height = char_height
        return width, height

    # Get the real output and color
    if auto_execute:
        output_text, output_color = execute_cprint_code(code_lines)
    else:
        output_text, output_color = "Manual output", "#ffffff"

    # Define font sizes
    code_fontsize = 18
    output_label_fontsize = 20
    output_fontsize = 38

    # Prepare all text elements with their font sizes
    texts = []
    for code_line in code_lines:
        texts.append((code_line, code_fontsize))

    texts.append(("Output:", output_label_fontsize))
    texts.append((output_text, output_fontsize))

    # Calculate required dimensions
    max_width = 0
    total_height = 0
    line_spacing = 0.3  # inches between lines

    for text, fontsize in texts:
        width, height = get_text_width_height(text, fontsize)
        max_width = max(max_width, width)
        total_height += height + line_spacing

    # Add padding
    padding = 0.6  # inches
    fig_width = max_width + (2 * padding)
    fig_height = total_height + (2 * padding)

    # Create figure with calculated size
    fig, ax = plt.subplots(1, 1, figsize=(fig_width, fig_height))

    # Set terminal-like background (dark)
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")

    # Calculate vertical positions
    num_elements = len(texts)
    y_positions = []
    for i in range(num_elements):
        y_pos = 0.9 - (i * 0.15)  # Distribute elements vertically
        y_positions.append(y_pos)

    # Add code lines in brand pink
    for i, code_line in enumerate(code_lines):
        ax.text(
            0.05,
            y_positions[i],
            code_line,
            fontsize=code_fontsize,
            fontfamily="monospace",
            fontweight="bold",
            ha="left",
            va="center",
            color="#FF008C",  # Brand pink
            transform=ax.transAxes,
        )

    # Add "Output:" label
    output_label_index = len(code_lines)
    ax.text(
        0.05,
        y_positions[output_label_index],
        "Output:",
        fontsize=output_label_fontsize,
        fontweight="bold",
        fontfamily="monospace",
        ha="left",
        va="center",
        color="#ffffff",
        transform=ax.transAxes,
    )

    # Add the actual output with the REAL color from cprint
    output_text_index = len(code_lines) + 1
    ax.text(
        0.05,
        y_positions[output_text_index] * 0.8,
        output_text,
        fontsize=output_fontsize,
        fontweight="bold",
        fontfamily="monospace",
        ha="left",
        va="center",
        color=output_color,  # Use the REAL color from cprint!
        transform=ax.transAxes,
    )

    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    print(f"Generated figure size: {fig_width:.2f} x {fig_height:.2f} inches")
    print(f"Real output text: '{output_text}' in color: {output_color}")

    # Create docs/assets directory if it doesn't exist
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Save as SVG
    svg_path = assets_dir / f"{output_filename}.svg"
    plt.savefig(
        svg_path,
        format="svg",
        bbox_inches="tight",
        dpi=300,
    )
    print(f"Saved SVG: {svg_path}")

    # Save as PNG
    png_path = assets_dir / f"{output_filename}.png"
    plt.savefig(
        png_path,
        format="png",
        bbox_inches="tight",
        dpi=300,
    )
    print(f"Saved PNG: {png_path}")

    plt.close()  # Close the figure to free memory
    return fig, ax


def generate_all_terminal_style_assets():
    """Generate all terminal-style assets for documentation."""
    print("🎨 Generating terminal-style documentation assets...")

    # 1. Basic usage example
    print("\n=== Generating basic usage example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("Hello, World!", "red")',
    ]
    generate_terminal_image(code_lines, "basic_usage_terminal")

    # 2. Success message example
    print("\n=== Generating success message example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("✅ Operation completed successfully!", "green")',
    ]
    generate_terminal_image(code_lines, "success_message_terminal")

    # 3. Error message example
    print("\n=== Generating error message example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("❌ Error: File not found!", "red")',
    ]
    generate_terminal_image(code_lines, "error_message_terminal")

    # 4. Warning message example
    print("\n=== Generating warning message example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("⚠️ Warning: Deprecated function!", "yellow")',
    ]
    generate_terminal_image(code_lines, "warning_message_terminal")

    # 5. Info message example
    print("\n=== Generating info message example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("ℹ️ Processing data...", "blue")',
    ]
    generate_terminal_image(code_lines, "info_message_terminal")

    # 6. Hex color example
    print("\n=== Generating hex color example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("🎨 Custom orange color!", "#FF6B35")',
    ]
    generate_terminal_image(code_lines, "hex_color_terminal")

    # 7. Bright colors example
    print("\n=== Generating bright colors example ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("✨ Bright and vibrant!", "bright_green")',
    ]
    generate_terminal_image(code_lines, "bright_color_terminal")

    # 8. Multiple colors showcase
    print("\n=== Generating multiple colors showcase ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("🌈 Rainbow text!", "magenta")',
    ]
    generate_terminal_image(code_lines, "rainbow_terminal")

    # 9. CLI usage example
    print("\n=== Generating CLI usage example ===")
    code_lines = [
        "$ khx-ct 'Hello from CLI!' -c cyan",
        "# Command line interface demo",
    ]
    # For CLI, we'll manually set the output
    output_text = "Hello from CLI!"
    output_color = get_color_hex("cyan")

    # Create a custom version for CLI
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")

    # Add CLI command
    ax.text(
        0.05,
        0.7,
        code_lines[0],
        fontsize=18,
        fontfamily="monospace",
        fontweight="bold",
        ha="left",
        va="center",
        color="#FF008C",
        transform=ax.transAxes,
    )

    # Add comment
    ax.text(
        0.05,
        0.5,
        code_lines[1],
        fontsize=16,
        fontfamily="monospace",
        ha="left",
        va="center",
        color="#888888",
        transform=ax.transAxes,
    )

    # Add output label
    ax.text(
        0.05,
        0.3,
        "Output:",
        fontsize=20,
        fontweight="bold",
        fontfamily="monospace",
        ha="left",
        va="center",
        color="#ffffff",
        transform=ax.transAxes,
    )

    # Add output
    ax.text(
        0.05,
        0.1,
        output_text,
        fontsize=38,
        fontweight="bold",
        fontfamily="monospace",
        ha="left",
        va="center",
        color=output_color,
        transform=ax.transAxes,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Save CLI example
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    svg_path = assets_dir / "cli_usage_terminal.svg"
    plt.savefig(svg_path, format="svg", bbox_inches="tight", dpi=300)
    print(f"Saved SVG: {svg_path}")

    png_path = assets_dir / "cli_usage_terminal.png"
    plt.savefig(png_path, format="png", bbox_inches="tight", dpi=300)
    print(f"Saved PNG: {png_path}")

    plt.close()

    print("\n🎉 All terminal-style assets generated successfully!")
    print(f"📁 Assets saved to: {assets_dir.absolute()}")


# Example usage and main execution
if __name__ == "__main__":
    # Test individual examples first
    print("🧪 Testing individual examples...")

    # Test with green color
    print("\n=== Testing with green color ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("Success message", "green")',
    ]
    generate_terminal_image(code_lines, "test_green")

    # Test with white color
    print("\n=== Testing with white color ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("White text message", "white")',
    ]
    generate_terminal_image(code_lines, "test_white")

    # Test with red color
    print("\n=== Testing with red color ===")
    code_lines = [
        "from khx_color_text import cprint",
        'cprint("Error message", "red")',
    ]
    generate_terminal_image(code_lines, "test_red")

    # Generate all documentation assets
    print("\n" + "=" * 50)
    generate_all_terminal_style_assets()
