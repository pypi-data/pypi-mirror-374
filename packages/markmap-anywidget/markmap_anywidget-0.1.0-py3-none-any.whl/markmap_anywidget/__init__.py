from pathlib import Path
import anywidget
import traitlets


class MarkmapWidget(anywidget.AnyWidget):
    bundler_output_dir = Path(__file__).parent / "static"
    _esm = bundler_output_dir / "widget.js"
    _css = """
    .markmap-widget {
      width: 100%;
      height: 100%;
      background: transparent;
    }
    """

    markdown_content = traitlets.Unicode("").tag(sync=True)
