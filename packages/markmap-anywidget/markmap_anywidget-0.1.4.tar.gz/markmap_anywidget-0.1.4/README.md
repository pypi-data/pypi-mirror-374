# markmap-anywidget

A simple [anywidget](https://github.com/manzt/anywidget) implementation of [markmap](https://markmap.js.org/) for Jupyter and marimo notebooks.

## Installation

```bash
# Using pip
pip install markmap-anywidget

# Using uv
uv add markmap-anywidget
```

## Usage with marimo

See the [`marimo` documentation](https://docs.marimo.io/api/inputs/anywidget/) for more information on using `anywidget`.

```python
import marimo as mo
from markmap_anywidget import MarkmapWidget

widget = mo.ui.anywidget(
    MarkmapWidget(
        markdown_content="""---
markmap:
  colorFreezeLevel: 2
  maxWidth: 300
---

# markmap

## Links
- [Website](https://markmap.js.org/)
- [GitHub](https://github.com/gera2ld/markmap)

## Features
- `inline code`
- **strong** and *italic*
- Katex: $x = {-b \pm \sqrt{b^2-4ac} \over 2a}$
"""
    )
)

# In a marimo cell, displaying the widget is enough
widget
```

## Development

This project uses [Nix](https://nixos.org/) with [nix-direnv](https://github.com/nix-community/nix-direnv) for a reproducible development environment.

```bash
# Clone the repository
git clone git@github.com:daniel-fahey/markmap-anywidget.git
cd markmap-anywidget

# Enter Nix development environment
direnv allow

# Install dependencies
uv sync
```

### Building

**Complete build (recommended):**
```bash
# Using make (includes clean, build, and quality checks)
make all
```

**Build only (faster for development):**
```bash
# Using make
make build
# or:
cd js && pnpm install && pnpm build
cd .. && uv build
```

**Development mode (watch for changes):**
```bash
# Using make
make dev

# Manual equivalent
cd js && pnpm dev
```

### Quality Checks

**Run all quality checks:**
```bash
# Using make (includes lint, type-check, and test)
make check
```

**Individual checks:**
```bash
# Linting
make lint
# or:
uv run ruff check src/ examples/ tests/

# Type checking
make type-check
# or:
uv run mypy src/

# Testing
make test
# or:
uv run pytest
```

### Available Commands

**Show all available Makefile targets:**
```bash
make
# or:
make help
```

### Examples

Run the marimo example:

```bash
uv run python -m marimo edit --watch examples/marimo.py
```