"""LaTeX → PDF / PNG compilation pipeline.

Display:   pdflatex → PDF → pdf_to_png → PNG (base64 in _repr_html_)
Export:    pdflatex → PDF

pdf_to_png tries converters in order:
  pdftoppm   (brew install poppler)   ← preferred
  gs         (Ghostscript, often already on PATH with TeX Live or standalone)
  mutool     (brew install mupdf-tools)
  convert    (brew install imagemagick)
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field


@dataclass
class CompileResult:
    pdf_bytes: bytes = field(default=b"")
    log: str = field(default="")
    success: bool = field(default=False)


def _run(cmd: list[str], cwd: str) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def compile_to_pdf(tex_source: str) -> CompileResult:
    """pdflatex → PDF bytes."""
    result = CompileResult()

    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "plot.tex").write_text(tex_source, encoding="utf-8")

        rc, log = _run(["pdflatex", "-interaction=nonstopmode", "plot.tex"], cwd=tmp)
        result.log = log

        pdf = p / "plot.pdf"
        if rc != 0 or not pdf.exists():
            return result

        result.pdf_bytes = pdf.read_bytes()
        result.success = True

    return result


def pdf_to_png(pdf_bytes: bytes, dpi: int = 150) -> bytes:
    """Convert the first page of *pdf_bytes* to PNG bytes.

    Tries pdftoppm, gs, mutool, convert — raises RuntimeError if none found.
    """
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        pdf = p / "input.pdf"
        pdf.write_bytes(pdf_bytes)

        if shutil.which("pdftoppm"):
            rc, _ = _run(
                ["pdftoppm", "-png", f"-r{dpi}", "-f", "1", "-l", "1",
                 "input.pdf", "page"],
                cwd=tmp,
            )
            candidates = sorted(p.glob("page*.png"))
            if rc == 0 and candidates:
                return candidates[0].read_bytes()

        if shutil.which("gs"):
            rc, _ = _run(
                ["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pngalpha",
                 f"-r{dpi}", "-sOutputFile=output.png", "input.pdf"],
                cwd=tmp,
            )
            out = p / "output.png"
            if rc == 0 and out.exists():
                return out.read_bytes()

        if shutil.which("mutool"):
            rc, _ = _run(
                ["mutool", "draw", "-F", "png", f"-r{dpi}", "-o", "output.png",
                 "input.pdf"],
                cwd=tmp,
            )
            out = p / "output.png"
            if rc == 0 and out.exists():
                return out.read_bytes()

        if shutil.which("convert"):
            rc, _ = _run(
                ["convert", "-density", str(dpi), "input.pdf[0]", "output.png"],
                cwd=tmp,
            )
            out = p / "output.png"
            if rc == 0 and out.exists():
                return out.read_bytes()

    raise RuntimeError(
        "No PDF→PNG converter found. Install one of:\n"
        "  brew install poppler       # pdftoppm\n"
        "  brew install mupdf-tools   # mutool\n"
        "  brew install imagemagick   # convert\n"
        "Or install Ghostscript (gs)."
    )
