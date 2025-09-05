# Documentation

This directory contains the documentation for khx_color_text.

## 📁 Structure

```
docs/
├── README.md           # This file
├── index.md           # Main documentation page
├── examples.md        # Comprehensive examples
├── installation.md    # Installation guide
└── assets/           # Visual assets (SVG previews)
    ├── showcase.svg
    ├── hex_examples.svg
    ├── rgb_examples.svg
    ├── combinations.svg
    ├── color_*.svg     # Individual color previews
    └── style_*.svg     # Individual style previews
```

## 🌐 Online Documentation

The documentation is automatically deployed to GitHub Pages:
- **Live Site**: https://khader-x.github.io/khx_color_text/
- **Source**: This `docs/` directory
- **Build**: Automatic via GitHub Actions

## 🎨 Visual Assets

### SVG Generation

All SVG assets are generated automatically using the `scripts/gen_assets.py` script:

```bash
python scripts/gen_assets.py
```

This generates:
- **31+ SVG files** showing colors and styles
- **Consistent styling** across all previews
- **High quality** vector graphics for documentation

### Asset Types

1. **Individual Colors** (`color_*.svg`)
   - One SVG per predefined color
   - Shows color name and example text
   - Consistent sizing and formatting

2. **Individual Styles** (`style_*.svg`)
   - One SVG per text style
   - Demonstrates style effect
   - Blue text for consistency

3. **Example Collections**
   - `hex_examples.svg` - Hex color examples
   - `rgb_examples.svg` - RGB color examples
   - `combinations.svg` - Style combinations
   - `showcase.svg` - Overall feature showcase

## 📝 Documentation Guidelines

### Writing Style

- **Clear and concise**: Easy to understand examples
- **Comprehensive**: Cover all features and use cases
- **Visual**: Include SVG previews where helpful
- **Practical**: Focus on real-world usage scenarios

### Code Examples

All code examples should:
- Be **runnable** as-is
- Include **imports** when needed
- Show **expected output** when helpful
- Cover **error cases** where relevant

### Visual Examples

- Use **SVG assets** for consistent appearance
- Include **alt text** for accessibility
- Size appropriately for the context
- Update when features change

## 🔄 Updating Documentation

### When to Update

Update documentation when:
- Adding new features
- Changing existing functionality
- Fixing bugs that affect usage
- Improving examples or explanations

### Update Process

1. **Update content** in markdown files
2. **Regenerate SVGs** if visual changes: `python scripts/gen_assets.py`
3. **Test locally** with MkDocs: `mkdocs serve`
4. **Commit changes** and push to trigger deployment

### Local Development

To work on documentation locally:

```bash
# Install documentation dependencies
pip install -e .[docs]

# Serve documentation locally
mkdocs serve

# Open browser to http://127.0.0.1:8000
```

## 🚀 Deployment

Documentation is automatically deployed via GitHub Actions:

1. **Trigger**: Push to `main` branch
2. **Build**: MkDocs generates static site
3. **Deploy**: GitHub Pages serves the site
4. **URL**: https://khader-x.github.io/khx_color_text/

### Manual Deployment

If needed, deploy manually:

```bash
# Build and deploy to gh-pages branch
mkdocs gh-deploy
```

## 📊 Documentation Metrics

### Coverage

- ✅ **Installation**: Complete guide
- ✅ **Quick Start**: Basic usage examples
- ✅ **API Reference**: Full function documentation
- ✅ **Examples**: Comprehensive feature examples
- ✅ **CLI Usage**: Command-line interface guide
- ✅ **Error Handling**: Common issues and solutions

### Visual Assets

- **31+ SVG files** generated automatically
- **Consistent styling** across all assets
- **High quality** vector graphics
- **Accessible** with proper alt text

### Maintenance

- **Automated updates** via GitHub Actions
- **Version controlled** with git
- **Consistent formatting** with MkDocs
- **Cross-referenced** between sections

## 🎯 Future Improvements

### Planned Enhancements

- **Interactive examples**: Live code playground
- **Video tutorials**: Screen recordings of usage
- **API browser**: Searchable function reference
- **Theme customization**: Dark/light mode support

### Content Additions

- **Best practices**: Recommended usage patterns
- **Performance guide**: Optimization tips
- **Integration examples**: Using with other libraries
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing to Documentation

### Guidelines

- Follow the existing style and structure
- Include visual examples where helpful
- Test all code examples before submitting
- Update SVG assets when needed

### Process

1. **Fork** the repository
2. **Create branch** for documentation changes
3. **Make changes** to markdown files
4. **Test locally** with `mkdocs serve`
5. **Submit PR** with clear description

### Review Criteria

- **Accuracy**: All information is correct
- **Completeness**: Covers the intended topic thoroughly
- **Clarity**: Easy to understand for target audience
- **Consistency**: Matches existing documentation style

---

For questions about documentation, please:
- **Check existing issues** for similar questions
- **Create new issue** with "documentation" label
- **Contact maintainer** for major changes