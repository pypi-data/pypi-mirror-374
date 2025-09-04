from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pptxvars")
except PackageNotFoundError:  # local dev, not installed
    __version__ = "0.0.0"

from .replacer import apply_vars, load_vars, format_outpath  # re-export
from .image_swap import swap_frames_from_imgs
from .pipeline import render_presentation

__all__ = [
    "__version__",
    "apply_vars",
    "load_vars",
    "format_outpath",
    "swap_frames_from_imgs",
    "render_presentation"
]
