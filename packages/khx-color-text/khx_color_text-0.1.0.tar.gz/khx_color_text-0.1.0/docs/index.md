# khx_color_text

Welcome to **khx_color_text** - a minimal Python package for printing colored text in the terminal with exactly five basic colors.

## Quick Start

Install the package:

```bash
pip install khx_color_text
```

Use it in Python:

```python
from khx_color_text import cprint

cprint("Hello World!", "cyan")
```

Or from the command line:

```bash
khx-ct "Hello World!" --color cyan
```

## Features

- **Five Colors**: red, green, blue, yellow, cyan
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Simple API**: Just one function `cprint(text, color)`
- **CLI Tool**: `khx-ct` command for terminal use
- **Lightweight**: Minimal dependencies (only colorama)

## Next Steps

Check out the [Examples](examples.md) page to see all colors in action with visual previews.