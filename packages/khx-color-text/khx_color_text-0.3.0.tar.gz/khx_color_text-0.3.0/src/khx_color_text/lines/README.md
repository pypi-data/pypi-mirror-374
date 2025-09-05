# Lines Module

The lines module provides functionality for creating decorative terminal lines with various characters, colors, and styles.

## Main Function: `cline`

The primary function `cline` creates decorative lines with automatic terminal width detection.

### Parameters

- `char` (Union[str, CharacterName]): Character to use for the line or character name. Can be a direct character like "*" or a descriptive name like "asterisk". Default is "-".
- `width` (Optional[int]): Width of the line. If None, uses terminal width or 50.
- `color` (Optional[str]): Text color (hex, rgb, or color name).
- `bg_color` (Optional[str]): Background color (hex, rgb, or color name).
- `style` (Optional[Union[str, list]]): Text style(s) like 'bold', 'italic', etc.
- `fill_terminal` (bool): If True and width is None, fills entire terminal width.

### Examples

```python
from khx_color_text import cline

# Basic line filling terminal width
cline()

# Using direct characters
cline("*", color="#FF0000")
cline("=", width=30, color="blue", style="bold")

# Using character names (with IDE autocomplete support)
cline("asterisk", color="#FF0000")  # Same as "*"
cline("full_block", color="#FFFFFF", bg_color="#FF0000")  # Same as "█"
cline("wave_dash", color="#00FFFF")  # Unicode wave character
cline("black_diamond", width=40, color="#FF00FF")  # Diamond pattern
cline("infinity", color="#9370DB")  # Mathematical infinity symbol
```

## Predefined Line Functions

- `solid_line()` - Creates a solid line using full block character
- `dashed_line()` - Creates a dashed line
- `dotted_line()` - Creates a dotted line
- `wave_line()` - Creates a wavy line
- `double_line()` - Creates a double line using box drawing character
- `star_line()` - Creates a decorative star line

## Character Categories

### Basic ASCII
- `*` (asterisk), `-` (dash), `+` (plus), `.` (dot), `_` (underscore), `=` (equals), etc.

### Unicode Box Drawing
- `─` (horizontal line), `━` (heavy horizontal), `═` (double horizontal), etc.

### Block Characters
- `█` (full block), `▓` (dark shade), `▒` (medium shade), `░` (light shade), etc.

### Wave Characters
- `~` (tilde), `∼` (tilde operator), `≈` (almost equal), `≋` (triple tilde), etc.

### Decorative Characters
- `◆` (black diamond), `●` (black circle), `★` (black star), `♦` (diamond suit), etc.

### Geometric Patterns
- `▲` (up triangle), `▼` (down triangle), `◄` (left pointer), `►` (right pointer), etc.

### Mathematical Symbols
- `∞` (infinity), `∑` (summation), `√` (square root), `∫` (integral), etc.

## Character Lookup

Use the character lookup functions to access characters by name:

```python
from khx_color_text.lines.characters import get_char, list_chars

# Get character by name
char = get_char("full_block")  # Returns '█'

# List characters by category
basic_chars = list_chars("basic")
decorative_chars = list_chars("decorative")
```

## Features

- **Automatic terminal width detection** - Lines fill the entire terminal by default
- **Extensive character library** - Over 50 different line characters
- **IDE autocomplete support** - Use descriptive character names with full IDE support
- **Dual input modes** - Accept both direct characters ("*") and names ("asterisk")
- **Full color support** - Hex, RGB, and named colors
- **Style support** - Bold, italic, underline, and more
- **Easy-to-use API** - Single function handles all line creation needs
- **Character lookup** - Access characters by descriptive names

## Character Names with IDE Support

The `cline` function now supports both direct characters and descriptive names with full IDE autocomplete:

```python
# These are equivalent:
cline("*")           # Direct character
cline("asterisk")    # Character name

# IDE will suggest all available names:
cline("full_block")     # █
cline("wave_dash")      # 〜
cline("infinity")       # ∞
cline("black_star")     # ★
cline("heart_suit")     # ♥
```