"""pypgfplots – minimal pgfplots wrapper for marimo notebooks."""

from ._core import Axis, Groupplot, TikzPicture
from ._global import classoptions, pgfplotset, preamble

__all__ = [
    "Axis",
    "Groupplot",
    "TikzPicture",
    "classoptions",
    "pgfplotset",
    "preamble",
]
