# Carlos Ferreyra CLI Business Card (Python)

A modern, interactive CLI business card showcasing Carlos Ferreyra's portfolio and contact
information with beautiful animations and rich terminal formatting.

Built with Python and optimized for `uvx` - the universal package runner.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![uvx](https://img.shields.io/badge/uvx-compatible-green.svg)

## Features

- 🎨 Beautiful terminal formatting with Rich
- 📧 Direct email contact
- 📥 Quick resume access
- 🌐 Portfolio website access
- 💻 Professional links (GitHub, LinkedIn, Twitter)
- ⚡ Fast and responsive interface
- 🖥️ Interactive CLI menu
- 🚀 ASCII art banner with animations
- 📦 Zero-install execution with uvx

## Quick Start

Run the business card directly with `uvx` (no installation required):

```bash
uvx carlosferreyra
```

## Alternative Installation Methods

### Using pip

```bash
pip install carlosferreyra
carlosferreyra
```

### Using uv

```bash
uv tool install carlosferreyra
carlosferreyra
```

## Development

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/carlosferreyra/carlosferreyra-cli-py.git
cd carlosferreyra-cli-py

# Install dependencies with uv
uv sync

# Run in development mode
uv run python -m carlosferreyra

# Or install in development mode
uv pip install -e .
carlosferreyra
```

### Building and Publishing

```bash
# Build the package
uv build

# Publish to PyPI (requires authentication)
uv publish
```

## Technologies Used

- **Python 3.13+** - Modern Python features
- **Rich** - Beautiful terminal formatting and animations
- **PyFiglet** - ASCII art text generation
- **Inquirer** - Interactive CLI prompts
- **Click** - Command line interface framework
- **Colorama** - Cross-platform colored terminal text

## Project Structure

```
src/carlosferreyra/
├── __init__.py          # Package initialization
├── __main__.py          # Main application entry point
├── config.py            # Personal information and configuration
├── utils.py             # Utility functions for animations
├── banner.py            # Welcome banner with ASCII art
├── card.py              # Business card display
├── menu.py              # Interactive menu system
└── actions.py           # Action handlers for menu options
```

## Customization

To customize this business card for yourself:

1. Update the personal information in `src/carlosferreyra/config.py`
2. Modify theme colors and animation speeds
3. Add or remove menu options in `src/carlosferreyra/menu.py`
4. Update action handlers in `src/carlosferreyra/actions.py`

## uvx vs npx Comparison

This Python CLI is designed to be the equivalent of the TypeScript version but optimized for Python
tooling:

| Feature          | TypeScript (npx)                | Python (uvx)                     |
| ---------------- | ------------------------------- | -------------------------------- |
| Runtime          | Node.js                         | Python                           |
| Package Manager  | npm                             | PyPI                             |
| Zero-install run | `npx carlosferreyra`            | `uvx carlosferreyra`             |
| Installation     | `npm install -g carlosferreyra` | `uv tool install carlosferreyra` |

## Connect with Carlos

- **GitHub**: [github.com/carlosferreyra](https://github.com/carlosferreyra)
- **LinkedIn**: [linkedin.com/in/eduferreyraok](https://linkedin.com/in/eduferreyraok)
- **Website**: [carlosferreyra.me](https://carlosferreyra.me)
- **Email**: [eduferreyraok@gmail.com](mailto:eduferreyraok@gmail.com)
- **Twitter**: [@eduferreyraok](https://twitter.com/eduferreyraok)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Tutorial: Creating Your Own uvx CLI

This project serves as a complete example of how to create a modern Python CLI that works with
`uvx`. Key learnings:

### 1. Project Structure

- Use `src/` layout for better packaging
- Include `py.typed` for type information
- Configure entry points in `pyproject.toml`

### 2. uvx Compatibility

- Ensure fast startup time
- Minimize dependencies
- Use standard library when possible
- Configure proper entry points

### 3. Rich Terminal Experience

- Use Rich for beautiful formatting
- Implement smooth animations
- Create interactive menus
- Handle terminal clearing and sizing

### 4. Cross-platform Compatibility

- Use `webbrowser` module for URL opening
- Handle keyboard interrupts gracefully
- Test on multiple platforms

This CLI demonstrates how to create engaging terminal applications that users can run instantly with
`uvx carlosferreyra`!
