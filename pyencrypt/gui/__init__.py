try:
    import tkinter  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "GUI requires tkinter, but it is not available in the current "
        "Python environment."
    ) from exc

from pyencrypt.gui.app import run

__all__ = ["run"]
