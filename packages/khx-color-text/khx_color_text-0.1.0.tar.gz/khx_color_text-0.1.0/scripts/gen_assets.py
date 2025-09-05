"""Generate deterministic SVG previews for each color using Rich."""

import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Add the src directory to Python path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from khx_color_text.core import cprint
from khx_color_text.colors import ALLOWED_COLORS


def generate_svg_assets():
    """Generate SVG previews for each color."""
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
    }

    generated_files = []

    for color in sorted(ALLOWED_COLORS):
        # Create a Rich console with fixed width for deterministic output
        console = Console(record=True, width=60)

        # Use Rich's print directly with explicit hex color for pure colors
        from rich.text import Text

        text = Text(f"Hello from khx_color_text in {color}!", style=pure_colors[color])
        console.print(text)

        # Export to SVG
        svg_path = assets_dir / f"color_{color}.svg"
        svg_content = console.export_svg(title="khx_color_text")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        generated_files.append(svg_path)
        print(f"Generated: {svg_path}")

    print(f"\nSuccessfully generated {len(generated_files)} SVG files:")
    for file_path in generated_files:
        print(f"  - {file_path}")


if __name__ == "__main__":
    generate_svg_assets()
