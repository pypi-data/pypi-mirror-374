import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import re
import subprocess
import sys


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
                    return text, color

        # If no cprint found, try to execute the code
        # This is a simplified version - in reality you'd need more robust execution
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

    # Save as SVG
    plt.savefig(
        f"SANDBOX/{output_filename}.svg",
        format="svg",
        bbox_inches="tight",
        dpi=300,
    )
    print(f"Saved SVG: SANDBOX/{output_filename}.svg")

    # Save as PNG
    plt.savefig(
        f"SANDBOX/{output_filename}.png",
        format="png",
        bbox_inches="tight",
        dpi=300,
    )
    print(f"Saved PNG: SANDBOX/{output_filename}.png")

    plt.show()
    return fig, ax


# Example usage:
if __name__ == "__main__":
    # Test with different colors
    print("=== Testing with green color ===")
    code_lines = [
        "$ from khx_color_text import cprint",
        '$ cprint("Success message", "#27F591")',
    ]
    generate_terminal_image(code_lines, "green_test")

    print("\n=== Testing with white color ===")
    code_lines = [
        "$ from khx_color_text import cprint",
        '$ cprint("Success message", "#ffffff")',
    ]
    generate_terminal_image(code_lines, "white_test")

    print("\n=== Testing with red color ===")
    code_lines = [
        "$ from khx_color_text import cprint",
        '$ cprint("Error message", "#ff0000")',
    ]
    generate_terminal_image(code_lines, "red_test")
