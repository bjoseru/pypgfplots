"""Core classes: TikzPicture and Axis."""

from __future__ import annotations

import base64
import pathlib

from . import _global as _glob
from ._compiler import compile_to_pdf, pdf_to_png
from ._options import dict_to_pgf, kwargs_to_pgf, merge_opts


class TikzPicture:
    """A standalone tikzpicture document.

    Holds raw tikz content that is wrapped in a tikzpicture environment and a
    standalone LaTeX document on demand.  Compile on first display (marimo) or
    explicit export call.
    """

    def __init__(self) -> None:
        self._tikz_content: str = ""
        self._instance_preamble: list[str] = []
        self._compile_log: str = ""
        self._cache_key: str | None = None  # latex() string of last successful compile
        self._cache_pdf: bytes | None = None
        self._cache_png: bytes | None = None

    # ------------------------------------------------------------------
    # Preamble extension
    # ------------------------------------------------------------------

    def preamble(self, text: str) -> None:
        """Append *text* to the preamble of this instance's document."""
        self._instance_preamble.append(text)

    # ------------------------------------------------------------------
    # Content hook (overridden by Axis)
    # ------------------------------------------------------------------

    def _get_tikz_content(self) -> str:
        return self._tikz_content

    # ------------------------------------------------------------------
    # Document assembly
    # ------------------------------------------------------------------

    def latex(self) -> str:
        """Return the complete standalone LaTeX source as a string."""
        user_classopts = _glob.get_classoptions()
        if user_classopts:
            classopts_str = "[" + ",".join(user_classopts) + "]"
        else:
            classopts_str = "[border=2pt]"

        preamble_lines = _glob.get_preamble() + self._instance_preamble
        preamble_block = "\n".join(preamble_lines)

        pgfset = {"compat": "newest", **_glob.get_pgfplotset()}
        pgfset_str = "\\pgfplotsset{" + kwargs_to_pgf(pgfset) + "}"

        tikz_content = self._get_tikz_content()

        return (
            f"\\documentclass{classopts_str}{{standalone}}\n"
            f"\\usepackage{{pgfplots}}\n"
            f"{pgfset_str}\n"
            + (preamble_block + "\n" if preamble_block else "")
            + "\\begin{document}\n"
            f"\\begin{{tikzpicture}}\n"
            f"{tikz_content}"
            f"\\end{{tikzpicture}}\n"
            f"\\end{{document}}\n"
        )

    # ------------------------------------------------------------------
    # Compilation (with PDF + PNG cache)
    # ------------------------------------------------------------------

    def _get_pdf(self) -> bytes:
        """Return compiled PDF bytes, reusing the cache when the source is unchanged."""
        src = self.latex()
        if src != self._cache_key:
            result = compile_to_pdf(src)
            self._compile_log = result.log
            if not result.success:
                raise RuntimeError(
                    "Compilation failed. Call compile_log() for details."
                )
            self._cache_key = src
            self._cache_pdf = result.pdf_bytes
            self._cache_png = None  # PDF changed, PNG cache is stale
        return self._cache_pdf

    def _repr_html_(self) -> str:
        """Render as a PNG image for display in marimo and Jupyter."""
        pdf = self._get_pdf()
        if self._cache_png is None:
            self._cache_png = pdf_to_png(pdf)
        b64 = base64.b64encode(self._cache_png).decode()
        return f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;" />'

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def save_pdf(self, filename: str | pathlib.Path) -> None:
        """Write a PDF to *filename*, reusing a cached compile when possible."""
        pathlib.Path(filename).write_bytes(self._get_pdf())

    def save_tex(self, filename: str | pathlib.Path) -> None:
        """Write the LaTeX source to *filename* (no compilation)."""
        pathlib.Path(filename).write_text(self.latex(), encoding="utf-8")

    def compile_log(self) -> str:
        """Return the log output of the most recent compilation attempt."""
        return self._compile_log

    # ------------------------------------------------------------------
    # Combination
    # ------------------------------------------------------------------

    def __add__(self, other: TikzPicture) -> TikzPicture:
        """Combine two pictures into a new TikzPicture."""
        result = TikzPicture()
        result._tikz_content = (
            self._get_tikz_content() + "\n" + other._get_tikz_content()
        )
        result._instance_preamble = (
            self._instance_preamble + other._instance_preamble
        )
        return result


class Axis(TikzPicture):
    r"""A pgfplots axis environment inside a tikzpicture.

    Options passed as keyword arguments become \begin{axis}[...] options.
    Keys with underscores are converted to spaces (axis_lines -> axis lines).
    Pass a dict as a positional argument for options whose keys contain '/'
    or other characters not valid in Python identifiers.

    The default option ``axis lines=center`` is applied unless *axis_lines* is
    explicitly overridden.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        # Collect raw string / dict positional args as extra option fragments
        raw_opts: list[str] = []
        for arg in args:
            if isinstance(arg, dict):
                raw_opts.append(dict_to_pgf(arg))
            elif isinstance(arg, str):
                raw_opts.append(arg)

        kwargs.setdefault("axis_lines", "center")
        self._axis_opts: str = merge_opts(kwargs_to_pgf(kwargs), *raw_opts)
        self._axis_body: str = ""

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    def _get_tikz_content(self) -> str:
        return (
            f"\\begin{{axis}}[{self._axis_opts}]\n"
            f"{self._axis_body}"
            f"\\end{{axis}}\n"
        )

    # ------------------------------------------------------------------
    # addplot helpers
    # ------------------------------------------------------------------

    def _addplot_impl(self, base_cmd: str, *args, **kwargs) -> None:
        _type = kwargs.pop("_type", "")

        plus = ""
        body_parts: list[str] = []
        extra_opts: list[str] = []

        arg_list = list(args)
        if arg_list and arg_list[0] == "+":
            plus = "+"
            arg_list = arg_list[1:]

        for arg in arg_list:
            if isinstance(arg, dict):
                extra_opts.append(dict_to_pgf(arg))
            else:
                body_parts.append(str(arg))

        opts = merge_opts(kwargs_to_pgf(kwargs), *extra_opts)
        opts_str = f"[{opts}]" if opts else ""
        type_str = f" {_type}" if _type else ""
        body = " ".join(body_parts)

        self._axis_body += f"{base_cmd}{plus}{opts_str}{type_str}{{{body}}};\n"

    def addplot(self, *args, **kwargs) -> None:
        r"""Append an \addplot command.

        Keyword arguments become [...] options (underscores→spaces).
        Positional string arguments are joined and placed in {...}.
        A positional dict is merged into options without key transformation.
        Pass _type='coordinates' (or 'table', etc.) to insert a type specifier.
        Pass '+' as the first positional argument (or use addplot_plus) for \addplot+.
        """
        self._addplot_impl("\\addplot", *args, **kwargs)

    def addplot_plus(self, *args, **kwargs) -> None:
        r"""Append an \addplot+ command (shorthand for addplot('+', ...))."""
        self._addplot_impl("\\addplot+", *args, **kwargs)

    def addplot3(self, *args, **kwargs) -> None:
        r"""Append an \addplot3 command (same interface as addplot)."""
        self._addplot_impl("\\addplot3", *args, **kwargs)

    def addlegendentry(self, text: str) -> None:
        r"""Append \addlegendentry{text} for the most recently added plot."""
        self._axis_body += f"\\addlegendentry{{{text}}}\n"

    def legend(self, *entries: str) -> None:
        r"""Append \legend{entry1, entry2, ...} to set all legend entries at once."""
        self._axis_body += f"\\legend{{{','.join(entries)}}}\n"

    def __add__(self, other: Axis) -> Axis:
        """Return a new Axis with the addplot lines of both merged into one axis.

        Both operands' axis options and instance preambles are concatenated.
        """
        result = Axis.__new__(Axis)
        TikzPicture.__init__(result)
        result._axis_opts = merge_opts(self._axis_opts, other._axis_opts)
        result._axis_body = self._axis_body + other._axis_body
        result._instance_preamble = self._instance_preamble + other._instance_preamble
        return result
