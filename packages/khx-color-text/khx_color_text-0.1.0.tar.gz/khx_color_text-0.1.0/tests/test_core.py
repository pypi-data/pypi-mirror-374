"""Tests for khx_color_text core functionality."""

import pytest
from io import StringIO
import sys
from contextlib import redirect_stdout
from khx_color_text.core import cprint
from khx_color_text.colors import ALLOWED_COLORS, COLOR_MAP


@pytest.mark.parametrize("color", ALLOWED_COLORS)
def test_cprint_valid_colors(color):
    """Test that cprint works with all valid colors."""
    # Capture stdout
    captured_output = StringIO()

    with redirect_stdout(captured_output):
        cprint("Hello", color)

    output = captured_output.getvalue()

    # Check that the text appears in output
    assert "Hello" in output
    # Check that the ANSI color code is present
    expected_ansi = COLOR_MAP[color]
    assert expected_ansi in output


def test_cprint_invalid_color():
    """Test that cprint raises ValueError for invalid colors."""
    with pytest.raises(ValueError) as exc_info:
        cprint("Hello", "purple")

    error_message = str(exc_info.value)
    assert "Invalid color 'purple'" in error_message
    assert "Allowed colors:" in error_message

    # Check that all allowed colors are mentioned in the error
    for color in ALLOWED_COLORS:
        assert color in error_message


def test_allowed_colors_count():
    """Test that we have exactly 5 allowed colors."""
    assert len(ALLOWED_COLORS) == 5
    expected_colors = {"red", "green", "blue", "yellow", "cyan"}
    assert ALLOWED_COLORS == expected_colors
