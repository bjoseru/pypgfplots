"""LaTeX → PDF → SVG compilation pipeline.

The public entry point is :func:`compile_tex`.  It is intentionally kept as a
standalone function so the backend can later be swapped (e.g. latexmk, tectonic,
cached subprocess pools) without touching the core classes.
"""

from __future__ import annotations

import pathlib
import subprocess
import tempfile
from dataclasses import dataclass, field


@dataclass
class CompileResult:
    pdf_bytes: bytes = field(default=b"")
    svg_string: str = field(default="")
    log: str = field(default="")
    success: bool = field(default=False)


def compile_tex(tex_source: str) -> CompileResult:
    """Compile *tex_source* through pdflatex and dvisvgm.

    Returns a :class:`CompileResult`.  ``success`` is True only when both
    pdflatex and dvisvgm exit cleanly and the SVG file is readable.
    """
    result = CompileResult()

    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "plot.tex").write_text(tex_source, encoding="utf-8")

        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "plot.tex"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        result.log = proc.stdout + proc.stderr

        pdf_path = p / "plot.pdf"
        if proc.returncode != 0 or not pdf_path.exists():
            return result

        result.pdf_bytes = pdf_path.read_bytes()

        proc2 = subprocess.run(
            ["dvisvgm", "--pdf", "plot.pdf", "-o", "plot.svg"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        result.log += proc2.stdout + proc2.stderr

        svg_path = p / "plot.svg"
        if proc2.returncode != 0 or not svg_path.exists():
            return result

        result.svg_string = svg_path.read_text(encoding="utf-8")
        result.success = True

    return result
