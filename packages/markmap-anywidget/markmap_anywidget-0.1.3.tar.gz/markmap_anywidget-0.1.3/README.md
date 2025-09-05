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
        markdown_content="""
---
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

# Build JavaScript assets (see Makefile for more targets)
make build
```

To watch for changes and automatically rebuild:

```bash
make dev
```

Run the marimo example:

```bash
uv run python -m marimo edit --watch examples/marimo.py
```