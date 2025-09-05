# khx_color_text

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI Status](https://img.shields.io/badge/CI-passing-green.svg)](https://github.com/Khader-X/khx_color_text/actions)

A minimal Python package for printing colored text in the terminal with exactly five basic colors.

## Installation

```bash
pip install khx_color_text
```

## Usage

### Python API

```python
from khx_color_text import cprint

# Print text in different colors
cprint("Hello World!", "red")
cprint("Success message", "green")
cprint("Information", "blue")
cprint("Warning", "yellow")
cprint("Highlight", "cyan")
```

### Command Line Interface

```bash
# Basic usage
khx-ct "Hello World!" --color red

# Default color is cyan
khx-ct "Hello World!"

# All available colors
khx-ct "Red text" --color red
khx-ct "Green text" --color green
khx-ct "Blue text" --color blue
khx-ct "Yellow text" --color yellow
khx-ct "Cyan text" --color cyan
```

## Examples

### Red
```python
cprint("Hello from khx_color_text in red!", "red")
```
<img src="docs/assets/color_red.svg" alt="Red example" width="520">

### Green
```python
cprint("Hello from khx_color_text in green!", "green")
```
<img src="docs/assets/color_green.svg" alt="Green example" width="520">

### Blue
```python
cprint("Hello from khx_color_text in blue!", "blue")
```
<img src="docs/assets/color_blue.svg" alt="Blue example" width="520">

### Yellow
```python
cprint("Hello from khx_color_text in yellow!", "yellow")
```
<img src="docs/assets/color_yellow.svg" alt="Yellow example" width="520">

### Cyan
```python
cprint("Hello from khx_color_text in cyan!", "cyan")
```
<img src="docs/assets/color_cyan.svg" alt="Cyan example" width="520">

## How Previews Are Generated

The SVG previews above are generated deterministically using the `scripts/gen_assets.py` script. This script uses Rich Console with a fixed width (60 characters) to capture the colored output and export it as SVG files. The previews are automatically regenerated on each push to the main branch via GitHub Actions.

To regenerate the previews locally:

```bash
pip install -e .[docs]
python scripts/gen_assets.py
```

## Supported Colors

The package supports exactly five colors:
- `red`
- `green` 
- `blue`
- `yellow`
- `cyan`

## Cross-Platform Support

This package uses `colorama` to ensure colored output works correctly on Windows, macOS, and Linux terminals.

## License

MIT License - see LICENSE file for details.

## Author

**ABUELTAYEF Khader**
- Email: abueltayef.khader@gmail.com
- GitHub Personal: [@Khader20](https://github.com/Khader20)
- GitHub Organization: [@Khader-X](https://github.com/Khader-X)
- PyPI: [Khader20](https://pypi.org/user/Khader20/)