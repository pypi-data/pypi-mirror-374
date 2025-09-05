"""Character definitions for different line types."""

# Basic ASCII characters
BASIC_CHARS = {
    "asterisk": "*",
    "dash": "-",
    "hyphen": "-",
    "plus": "+",
    "dot": ".",
    "period": ".",
    "underscore": "_",
    "equals": "=",
    "tilde": "~",
    "caret": "^",
    "pipe": "|",
    "forward_slash": "/",
    "backslash": "\\",
    "hash": "#",
    "pound": "#",
}

# Unicode box drawing characters
BOX_DRAWING_CHARS = {
    "horizontal": "─",
    "heavy_horizontal": "━",
    "double_horizontal": "═",
    "light_triple_dash": "┄",
    "heavy_triple_dash": "┅",
    "light_quadruple_dash": "┈",
    "heavy_quadruple_dash": "┉",
}

# Block characters
BLOCK_CHARS = {
    "full_block": "█",
    "dark_shade": "▓",
    "medium_shade": "▒",
    "light_shade": "░",
    "upper_half_block": "▀",
    "lower_half_block": "▄",
    "black_rectangle": "▬",
    "white_rectangle": "▭",
    "black_small_square": "▪",
    "white_small_square": "▫",
    "black_medium_square": "■",
    "white_medium_square": "□",
}

# Wave and curved characters
WAVE_CHARS = {
    "tilde": "~",
    "tilde_operator": "∼",
    "almost_equal": "≈",
    "triple_tilde": "≋",
    "wave_dash": "〜",
    "reversed_not": "⌐",
    "top_half_integral": "⌠",
    "bottom_half_integral": "⌡",
}

# Decorative characters
DECORATIVE_CHARS = {
    "black_diamond": "◆",
    "white_diamond": "◇",
    "black_circle": "●",
    "white_circle": "○",
    "black_star": "★",
    "white_star": "☆",
    "diamond_suit": "♦",
    "spade_suit": "♠",
    "club_suit": "♣",
    "heart_suit": "♥",
    "reference_mark": "※",
    "asterism": "⁂",
    "low_asterisk": "⁎",
    "four_balloon_asterisk": "⁕",
}

# Geometric patterns
GEOMETRIC_CHARS = {
    "black_up_triangle": "▲",
    "white_up_triangle": "△",
    "black_down_triangle": "▼",
    "white_down_triangle": "▽",
    "black_left_pointer": "◄",
    "black_right_pointer": "►",
    "black_left_triangle": "◀",
    "black_right_triangle": "▶",
}

# Mathematical symbols
MATH_CHARS = {
    "infinity": "∞",
    "integral": "∫",
    "summation": "∑",
    "product": "∏",
    "square_root": "√",
    "increment": "∆",
    "nabla": "∇",
    "partial_differential": "∂",
}

# All characters combined
ALL_CHARS = {
    **BASIC_CHARS,
    **BOX_DRAWING_CHARS,
    **BLOCK_CHARS,
    **WAVE_CHARS,
    **DECORATIVE_CHARS,
    **GEOMETRIC_CHARS,
    **MATH_CHARS,
}

# Character categories for easy access
CATEGORIES = {
    "basic": BASIC_CHARS,
    "box": BOX_DRAWING_CHARS,
    "block": BLOCK_CHARS,
    "wave": WAVE_CHARS,
    "decorative": DECORATIVE_CHARS,
    "geometric": GEOMETRIC_CHARS,
    "math": MATH_CHARS,
}


def get_char(name: str) -> str:
    """
    Get a character by name.

    Args:
        name (str): Name of the character.

    Returns:
        str: The character, or the input name if not found.

    Examples:
        >>> get_char('asterisk')
        '*'
        >>> get_char('full_block')
        '█'
        >>> get_char('wave_dash')
        '〜'
    """
    return ALL_CHARS.get(name.lower(), name)


def list_chars(category: str = None) -> dict:
    """
    List available characters, optionally filtered by category.

    Args:
        category (str, optional): Category to filter by.

    Returns:
        dict: Dictionary of character names and symbols.

    Examples:
        >>> list_chars('basic')
        {'asterisk': '*', 'dash': '-', ...}
        >>> list_chars()  # All characters
    """
    if category:
        return CATEGORIES.get(category.lower(), {})
    return ALL_CHARS
