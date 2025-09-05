# Installation Guide

## 📦 From PyPI (Recommended)

**khx_color_text** is available on the Python Package Index (PyPI). Install it using pip:

```bash
pip install khx_color_text
```

This will install the latest stable version (v0.2.0) along with its dependencies.

### Alternative Installation Methods

```bash
# Install specific version
pip install khx_color_text==0.2.0

# Install with all optional dependencies
pip install khx_color_text[docs]

# Install from GitHub (latest development)
pip install git+https://github.com/Khader-X/khx_color_text.git
```

## ✅ Verify Installation

After installation, verify that everything works correctly:

### Test the CLI Tool
```bash
# Basic color test
khx-ct "Hello World!" -c red

# Test hex colors
khx-ct "Custom color" --hex "#FF6B35"

# Test RGB colors
khx-ct "RGB color" --rgb "255,0,0"

# Test styling
khx-ct "Bold text" -c blue -s bold

# Show built-in examples
khx-ct --examples
```

### Test Python API
```python
# Basic functionality test
from khx_color_text import cprint, TextStyle

# Test basic colors
cprint("Success! Basic colors work.", "green")

# Test hex colors
cprint("Hex colors work!", "#FF6B35")

# Test RGB colors
cprint("RGB colors work!", (138, 43, 226))

# Test styling
cprint("Styling works!", "blue", style="bold")

# Test combinations
cprint("Everything works!", "#00FF00", bg_color="black", style=TextStyle.BOLD)
```

## 🖥️ System Requirements

### Python Version
- **Python 3.9** or higher
- Tested on Python 3.9, 3.10, 3.11, 3.12

### Operating Systems
- **Windows** 10/11 (Command Prompt, PowerShell, Windows Terminal)
- **macOS** 10.15+ (Terminal.app, iTerm2)
- **Linux** (GNOME Terminal, KDE Konsole, tmux, screen)

### Terminal Compatibility
- **Full support**: Modern terminals with ANSI color support
- **Partial support**: Basic terminals (colors may be limited)
- **Fallback**: Plain text on unsupported terminals

## 📋 Dependencies

The package has minimal runtime dependencies:

### Required
- **`colorama>=0.4.6`** - Cross-platform colored terminal output

### Optional (Development)
- **`rich>=13`** - SVG asset generation
- **`mkdocs>=1.6`** - Documentation building
- **`mkdocs-material>=9.6`** - Documentation theme

## 🛠️ Development Installation

If you want to contribute to the project or modify the package:

### 1. Clone the Repository
```bash
git clone https://github.com/Khader-X/khx_color_text.git
cd khx_color_text
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install in Development Mode
```bash
# Install with all development dependencies
pip install -e .[docs]

# Or install minimal development setup
pip install -e .
```

### 4. Verify Development Setup
```bash
# Run tests
python tests/test_basic_functionality.py
python tests/test_advanced_features.py
python tests/test_color_utilities.py

# Run examples
python src/khx_color_text/examples/basic_examples.py

# Test CLI
python -m khx_color_text.cli --showcase

# Generate documentation assets
python scripts/gen_assets.py
```

## 🔄 Upgrading

### Check Current Version
```bash
pip show khx_color_text
```

### Upgrade to Latest Version
```bash
pip install --upgrade khx_color_text
```

### Upgrade from Specific Version
```bash
# If upgrading from v0.1.0 to v0.2.0
pip install --upgrade khx_color_text

# Verify new features work
khx-ct "New features!" --hex "#FF6B35" -s bold
```

## 🗑️ Uninstalling

To completely remove the package:

```bash
pip uninstall khx_color_text
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Import Error**
```bash
ImportError: No module named 'khx_color_text'
```
**Solution**: Ensure the package is installed in the correct Python environment:
```bash
pip list | grep khx-color-text
python -c "import khx_color_text; print('OK')"
```

#### 2. **CLI Command Not Found**
```bash
khx-ct: command not found
```
**Solution**: Use the module form or check your PATH:
```bash
python -m khx_color_text.cli "test" -c red
```

#### 3. **Colors Not Showing**
If colors don't appear in your terminal:
- **Windows**: Use Windows Terminal or enable ANSI support
- **SSH**: Ensure terminal supports colors (`echo $TERM`)
- **tmux/screen**: Check color configuration

#### 4. **Permission Errors**
```bash
PermissionError: [Errno 13] Permission denied
```
**Solution**: Use user installation:
```bash
pip install --user khx_color_text
```

### Platform-Specific Notes

#### Windows
- **Windows Terminal**: Best color support
- **Command Prompt**: Basic color support via colorama
- **PowerShell**: Good color support
- **Git Bash**: Unix-like color behavior

#### macOS
- **Terminal.app**: Full color support
- **iTerm2**: Enhanced color features
- **VS Code terminal**: Integrated support

#### Linux
- **GNOME Terminal**: Full color support
- **KDE Konsole**: Enhanced features
- **SSH sessions**: Depends on client terminal

## 📊 Installation Statistics

### Package Information
- **PyPI Package**: https://pypi.org/project/khx-color-text/
- **Downloads**: [![Downloads](https://pepy.tech/badge/khx-color-text)](https://pepy.tech/project/khx-color-text)
- **Version**: [![PyPI version](https://badge.fury.io/py/khx-color-text.svg)](https://badge.fury.io/py/khx-color-text)

### Supported Environments
- **Python versions**: 4 (3.9-3.12)
- **Operating systems**: 3 (Windows, macOS, Linux)
- **Terminal types**: 10+ (Command Prompt, PowerShell, Terminal.app, etc.)

## 🆘 Getting Help

If you encounter issues during installation:

1. **Check the troubleshooting section** above
2. **Search existing issues**: https://github.com/Khader-X/khx_color_text/issues
3. **Create a new issue** with:
   - Your operating system and version
   - Python version (`python --version`)
   - Installation method used
   - Complete error message
   - Steps to reproduce

4. **Contact the maintainer**: abueltayef.khader@gmail.com

## 🎯 Next Steps

After successful installation:

1. **Read the examples**: [examples.md](examples.md)
2. **Explore the CLI**: `khx-ct --help`
3. **Try the showcase**: `khx-ct --showcase`
4. **Check the API reference**: [index.md](index.md)
5. **Join the community**: Star the project on GitHub!