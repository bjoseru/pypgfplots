"""Core classes: TikzPicture and Axis."""

from __future__ import annotations

import pathlib

from . import _global as _glob
from ._compiler import compile_tex
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
    # Compilation
    # ------------------------------------------------------------------

    def _run_compile(self) -> str:
        """Compile to SVG, store log, return SVG string."""
        result = compile_tex(self.latex())
        self._compile_log = result.log
        if not result.success:
            raise RuntimeError(
                "Compilation failed. Call compile_log() for details."
            )
        return result.svg_string

    def _repr_html_(self) -> str:
        """Render as SVG for display in marimo and Jupyter."""
        return self._run_compile()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def save_pdf(self, filename: str | pathlib.Path) -> None:
        """Compile and write a PDF file to *filename*."""
        result = compile_tex(self.latex())
        self._compile_log = result.log
        if not result.pdf_bytes:
            raise RuntimeError(
                "PDF compilation failed. Call compile_log() for details."
            )
        pathlib.Path(filename).write_bytes(result.pdf_bytes)

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
        """Combine two pictures into a new TikzPicture (side by side in one tikzpicture)."""
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
