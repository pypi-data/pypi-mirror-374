# Project Structure

This document provides an overview of the khx_color_text project structure and organization.

## 📁 Directory Structure

```
khx_color_text/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                     # MIT License
├── 📄 CHANGELOG.md                # Version history and changes
├── 📄 CONTRIBUTING.md             # Contribution guidelines
├── 📄 FEATURES.md                 # Comprehensive feature overview
├── 📄 PROJECT_STRUCTURE.md        # This file
├── ⚙️ pyproject.toml              # Project configuration and dependencies
├── ⚙️ mkdocs.yml                  # Documentation site configuration
├── 📁 .github/                    # GitHub-specific files
│   ├── 📁 workflows/              # GitHub Actions CI/CD
│   │   ├── ci.yml                 # Main CI pipeline
│   │   └── assets.yml             # Asset generation workflow
│   ├── 📁 ISSUE_TEMPLATE/         # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── pull_request_template.md   # PR template
├── 📁 src/                        # Source code
│   └── 📁 khx_color_text/         # Main package
│       ├── __init__.py            # Package exports
│       ├── core.py                # Main cprint function
│       ├── cli.py                 # Command-line interface
│       ├── 📁 colors/             # Color management
│       │   ├── __init__.py
│       │   ├── predefined.py      # Predefined colors
│       │   ├── custom.py          # Hex/RGB support
│       │   └── utils.py           # Color utilities
│       ├── 📁 styles/             # Text styling
│       │   ├── __init__.py
│       │   ├── text_styles.py     # Style definitions
│       │   └── background.py      # Background colors
│       └── 📁 examples/           # Usage examples
│           ├── __init__.py
│           ├── basic_examples.py
│           ├── advanced_examples.py
│           └── color_showcase.py
├── 📁 tests/                      # Test suite
│   ├── test_basic_functionality.py
│   ├── test_advanced_features.py
│   └── test_color_utilities.py
├── 📁 docs/                       # Documentation
│   ├── README.md                  # Documentation overview
│   ├── index.md                   # Main documentation page
│   ├── examples.md                # Comprehensive examples
│   ├── installation.md            # Installation guide
│   └── 📁 assets/                 # Visual assets (SVG previews)
│       ├── showcase.svg
│       ├── hex_examples.svg
│       ├── rgb_examples.svg
│       ├── combinations.svg
│       ├── color_*.svg            # Individual color previews
│       └── style_*.svg            # Individual style previews
├── 📁 scripts/                    # Utility scripts
│   └── gen_assets.py              # SVG generation script
└── 📁 dist/                       # Build artifacts (generated)
    ├── *.whl                      # Wheel distribution
    └── *.tar.gz                   # Source distribution
```

## 🏗️ Architecture Overview

### Core Components

#### 1. **Main API** (`src/khx_color_text/core.py`)
- **`cprint()` function**: Single entry point for all functionality
- **Parameter handling**: Flexible parameter processing
- **ANSI generation**: Converts colors/styles to ANSI codes
- **Error handling**: Comprehensive validation and error messages

#### 2. **Color Management** (`src/khx_color_text/colors/`)
- **`predefined.py`**: 21 predefined colors and aliases
- **`custom.py`**: Hex and RGB color processing
- **`utils.py`**: Unified color handling and validation

#### 3. **Style Management** (`src/khx_color_text/styles/`)
- **`text_styles.py`**: Text style definitions and processing
- **`background.py`**: Background color handling

#### 4. **CLI Interface** (`src/khx_color_text/cli.py`)
- **Argument parsing**: Comprehensive command-line options
- **Feature demonstration**: Built-in examples and showcases
- **Error handling**: User-friendly CLI error messages

### Design Principles

#### 1. **Single API Philosophy**
- One `cprint()` function handles all features
- Optional parameters for maximum flexibility
- Backward compatibility maintained across versions

#### 2. **Modular Architecture**
- Logical separation of concerns
- Easy to extend and maintain
- Clear dependency relationships

#### 3. **Type Safety**
- Comprehensive type hints throughout
- No `type: ignore` comments
- Full mypy compatibility

#### 4. **Error Handling**
- Clear, actionable error messages
- Helpful suggestions for fixes
- Graceful degradation where possible

## 🧪 Testing Strategy

### Test Organization

#### 1. **Basic Functionality** (`tests/test_basic_functionality.py`)
- Predefined color testing
- Basic error handling
- Core function validation

#### 2. **Advanced Features** (`tests/test_advanced_features.py`)
- Hex and RGB color support
- Text styling functionality
- Background color support
- Complex feature combinations

#### 3. **Color Utilities** (`tests/test_color_utilities.py`)
- Color conversion functions
- Validation logic
- Edge case handling

### Testing Philosophy

- **No pytest dependency**: Simple `if __name__ == "__main__"` patterns
- **Comprehensive coverage**: All features and edge cases
- **Cross-platform**: Tested on Windows, macOS, Linux
- **Real-world scenarios**: Practical usage examples

## 📚 Documentation Strategy

### Multi-Level Documentation

#### 1. **Quick Start** (README.md)
- Installation instructions
- Basic usage examples
- Key features overview

#### 2. **Comprehensive Guide** (docs/)
- Detailed feature documentation
- Visual examples with SVG assets
- API reference with all parameters

#### 3. **Developer Resources**
- Contributing guidelines
- Project structure documentation
- Development setup instructions

### Visual Documentation

#### SVG Asset Generation
- **Automated**: Generated via `scripts/gen_assets.py`
- **Consistent**: Uniform styling across all assets
- **Comprehensive**: 31+ visual examples
- **Version controlled**: Assets committed to repository

## 🚀 Build and Deployment

### Build System

#### **Hatchling-based** (`pyproject.toml`)
- Modern Python packaging
- PEP 621 compliant metadata
- Minimal configuration
- Fast builds

#### **Dependencies**
- **Runtime**: Only colorama (cross-platform colors)
- **Development**: Rich (SVG generation), MkDocs (documentation)
- **Optional**: Separate dependency groups for different use cases

### CI/CD Pipeline

#### **GitHub Actions** (`.github/workflows/`)
- **Multi-platform testing**: Windows, macOS, Linux
- **Multi-version testing**: Python 3.9-3.12
- **Comprehensive testing**: All test modules and examples
- **Asset generation**: Automatic SVG regeneration
- **Documentation deployment**: Automatic GitHub Pages updates

### Release Process

#### **Semantic Versioning**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### **Release Checklist**
1. Update version numbers
2. Update CHANGELOG.md
3. Regenerate assets
4. Run full test suite
5. Update documentation
6. Create release PR
7. Tag and publish

## 🔧 Development Workflow

### Local Development

#### **Setup**
```bash
git clone https://github.com/Khader-X/khx_color_text.git
cd khx_color_text
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev,docs]
```

#### **Testing**
```bash
# Run all tests
python tests/test_basic_functionality.py
python tests/test_advanced_features.py
python tests/test_color_utilities.py

# Test examples
python src/khx_color_text/examples/basic_examples.py
python src/khx_color_text/examples/advanced_examples.py
python src/khx_color_text/examples/color_showcase.py

# Test CLI
python -m khx_color_text.cli --examples
```

#### **Documentation**
```bash
# Generate SVG assets
python scripts/gen_assets.py

# Serve documentation locally
mkdocs serve
```

### Code Quality

#### **Standards**
- **PEP 8**: Python style guidelines
- **Type hints**: Comprehensive type annotations
- **Docstrings**: All public functions documented
- **Error handling**: Clear, helpful error messages

#### **Tools**
- **mypy**: Type checking
- **black**: Code formatting (optional)
- **Rich**: SVG generation for documentation

## 📊 Project Metrics

### Code Statistics

- **Lines of code**: ~1,500 (excluding tests and docs)
- **Functions**: ~25 public functions
- **Classes**: ~5 (mainly enums and utilities)
- **Modules**: ~10 organized modules

### Feature Coverage

- **Colors**: 21 predefined + unlimited custom (hex/RGB)
- **Styles**: 6 text styles with combination support
- **Formats**: 3 color formats (predefined, hex, RGB)
- **Platforms**: 3 operating systems (Windows, macOS, Linux)
- **Python versions**: 4 versions (3.9-3.12)

### Documentation Assets

- **SVG files**: 31+ generated visual examples
- **Documentation pages**: 5+ comprehensive guides
- **Code examples**: 50+ practical examples
- **Test cases**: 100+ test scenarios

## 🔮 Future Architecture

### Planned Improvements

#### **Performance Optimizations**
- Color lookup caching
- ANSI code optimization
- Reduced memory footprint

#### **Feature Extensions**
- Plugin system for custom colors/styles
- Configuration file support
- Theme system for color schemes

#### **Developer Experience**
- Enhanced IDE support
- Better error messages
- More comprehensive examples

### Scalability Considerations

- **Backward compatibility**: Maintain API stability
- **Modular design**: Easy to extend without breaking changes
- **Performance**: Optimize for common use cases
- **Documentation**: Keep docs synchronized with features

---

This project structure is designed to be:
- **Maintainable**: Clear organization and separation of concerns
- **Extensible**: Easy to add new features without breaking existing code
- **Testable**: Comprehensive test coverage with simple testing approach
- **Documented**: Multi-level documentation for different audiences
- **Professional**: Following Python packaging and development best practices