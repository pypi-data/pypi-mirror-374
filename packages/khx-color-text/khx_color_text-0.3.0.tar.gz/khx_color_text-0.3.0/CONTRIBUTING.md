# Contributing to khx_color_text

Thank you for your interest in contributing to khx_color_text! This document provides guidelines and information for contributors.

## 🎯 Project Vision

khx_color_text aims to be the most user-friendly and comprehensive terminal coloring package for Python, while maintaining:
- **Simplicity**: Single API function for all features
- **Flexibility**: Support for multiple color formats and styling options
- **Reliability**: Cross-platform compatibility and robust error handling
- **Performance**: Efficient color processing with minimal overhead

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of terminal colors and ANSI escape codes

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/khx_color_text.git
   cd khx_color_text
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. **Verify Installation**
   ```bash
   python -c "from khx_color_text import cprint; cprint('Setup successful!', 'green')"
   ```

## 🏗️ Project Structure

```
khx_color_text/
├── src/khx_color_text/          # Main package
│   ├── __init__.py              # Package exports
│   ├── core.py                  # Main cprint function
│   ├── cli.py                   # Command-line interface
│   ├── colors/                  # Color management
│   │   ├── __init__.py
│   │   ├── predefined.py        # Predefined colors
│   │   ├── custom.py            # Hex/RGB support
│   │   └── utils.py             # Color utilities
│   ├── styles/                  # Text styling
│   │   ├── __init__.py
│   │   ├── text_styles.py       # Style definitions
│   │   └── background.py        # Background colors
│   └── examples/                # Usage examples
│       ├── __init__.py
│       ├── basic_examples.py
│       ├── advanced_examples.py
│       └── color_showcase.py
├── tests/                       # Test suite
│   ├── test_basic_functionality.py
│   ├── test_advanced_features.py
│   └── test_color_utilities.py
├── docs/                        # Documentation
│   ├── assets/                  # SVG previews
│   ├── index.md
│   └── examples.md
├── scripts/                     # Utility scripts
│   └── gen_assets.py           # SVG generation
└── .github/workflows/          # CI/CD
    ├── ci.yml
    └── assets.yml
```

## 🧪 Testing Guidelines

### Running Tests

We use simple `if __name__ == "__main__"` testing (no pytest):

```bash
# Run all tests
python tests/test_basic_functionality.py
python tests/test_advanced_features.py
python tests/test_color_utilities.py

# Run examples
python src/khx_color_text/examples/basic_examples.py
python src/khx_color_text/examples/advanced_examples.py
python src/khx_color_text/examples/color_showcase.py
```

### Test Requirements

- **No pytest**: Use simple `if __name__ == "__main__"` patterns
- **No type: ignore**: Clean type hints without ignoring type errors
- **Comprehensive coverage**: Test all color formats, styles, and combinations
- **Error handling**: Test invalid inputs and edge cases
- **Cross-platform**: Ensure tests work on Windows, macOS, Linux

### Writing Tests

```python
def test_new_feature():
    """Test description."""
    print("Testing new feature...")
    
    try:
        # Test code here
        result = some_function()
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    test_new_feature()
```

## 🎨 Code Style Guidelines

### Python Code Style

- **PEP 8**: Follow Python style guidelines
- **Type hints**: Use comprehensive type annotations
- **Docstrings**: Document all public functions and classes
- **Error handling**: Provide clear, helpful error messages
- **Imports**: Organize imports logically

### Example Function:

```python
def new_color_function(
    color: Union[str, Tuple[int, int, int]], 
    validate: bool = True
) -> str:
    """Convert color to ANSI escape sequence.
    
    Args:
        color: Color in various formats (predefined, hex, RGB)
        validate: Whether to validate color format
        
    Returns:
        ANSI escape sequence string
        
    Raises:
        ValueError: If color format is invalid
        
    Examples:
        >>> new_color_function("red")
        '\033[31m'
        >>> new_color_function("#FF0000")
        '\033[38;2;255;0;0m'
    """
    # Implementation here
    pass
```

### Architecture Principles

- **Single API**: Maintain the single `cprint()` function approach
- **Modular design**: Organize code into logical modules
- **Backward compatibility**: Don't break existing code
- **Performance**: Optimize for common use cases
- **Extensibility**: Design for future enhancements

## 📝 Documentation Guidelines

### Documentation Requirements

- **Clear examples**: Show practical usage
- **Visual previews**: Include SVG examples where helpful
- **API documentation**: Document all parameters and return values
- **Error scenarios**: Document error conditions and solutions

### Updating Documentation

1. **Update docstrings** in code
2. **Update README.md** for user-facing changes
3. **Update docs/** for detailed documentation
4. **Regenerate SVGs** if visual changes: `python scripts/gen_assets.py`
5. **Update CHANGELOG.md** for all changes

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** for similar problems
2. **Test with latest version** from PyPI or main branch
3. **Reproduce the issue** with minimal code example
4. **Check multiple platforms** if possible

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug.

**To Reproduce**
```python
from khx_color_text import cprint
cprint("test", "invalid_color")  # This fails
```

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: Windows 10 / macOS 12 / Ubuntu 20.04
- Python: 3.9.7
- khx_color_text: 0.2.0
- Terminal: Command Prompt / Terminal.app / GNOME Terminal

**Additional Context**
Any other relevant information.
```

## 💡 Feature Requests

### Before Requesting

1. **Check existing issues** and discussions
2. **Consider the project vision** and scope
3. **Think about backward compatibility**
4. **Consider implementation complexity**

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed API**
```python
# How would users interact with this feature?
cprint("text", "color", new_parameter="value")
```

**Implementation Ideas**
Any thoughts on how this could be implemented.

**Alternatives Considered**
Other ways to achieve the same goal.
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create an issue** for discussion (for major changes)
2. **Fork the repository** and create a feature branch
3. **Write tests** for your changes
4. **Update documentation** as needed
5. **Test thoroughly** on multiple platforms if possible

### Pull Request Guidelines

1. **Clear title**: Describe what the PR does
2. **Detailed description**: Explain the changes and reasoning
3. **Link issues**: Reference related issues with "Fixes #123"
4. **Test results**: Show that tests pass
5. **Breaking changes**: Clearly mark any breaking changes

### PR Template

```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested on multiple platforms (if applicable)

**Documentation**
- [ ] Updated docstrings
- [ ] Updated README.md (if needed)
- [ ] Updated CHANGELOG.md
- [ ] Regenerated SVG assets (if needed)

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] No type: ignore comments added
- [ ] Backward compatibility maintained
```

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with all changes
3. **Regenerate assets**: `python scripts/gen_assets.py`
4. **Run full test suite**
5. **Update documentation**
6. **Create release PR**
7. **Tag release** after merge
8. **Publish to PyPI** via GitHub Actions

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful**: Treat all contributors with respect
- **Be inclusive**: Welcome contributors of all backgrounds
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that everyone is learning

### Communication

- **GitHub Issues**: For bugs, features, and discussions
- **Pull Requests**: For code contributions
- **Email**: For private matters (abueltayef.khader@gmail.com)

## 🎖️ Recognition

Contributors are recognized in:
- **GitHub contributors** page
- **CHANGELOG.md** for significant contributions
- **README.md** for major features

## 📚 Resources

### Learning Resources

- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Terminal Colors Guide](https://misc.flogisoft.com/bash/tip_colors_and_formatting)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Colorama Documentation](https://pypi.org/project/colorama/)

### Development Tools

- **VS Code**: Recommended editor with Python extension
- **mypy**: Type checking (`pip install mypy`)
- **black**: Code formatting (`pip install black`)
- **Rich**: For SVG generation (`pip install rich`)

## ❓ Questions?

If you have questions about contributing:

1. **Check existing issues** and discussions
2. **Read the documentation** thoroughly
3. **Ask in a new issue** with the "question" label
4. **Email the maintainer** for private questions

Thank you for contributing to khx_color_text! 🎨✨