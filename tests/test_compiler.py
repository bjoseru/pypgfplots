"""Compiler tests – skipped when required external tools are not installed."""

import shutil
import pytest
from pypgfplots import Axis

pdflatex_available = shutil.which("pdflatex") is not None
png_converter_available = any(
    shutil.which(t) for t in ("pdftoppm", "gs", "mutool", "convert")
)
full_pipeline_available = pdflatex_available and png_converter_available

skip_no_pipeline = pytest.mark.skipif(
    not full_pipeline_available,
    reason="pdflatex and/or a PDF→PNG converter not found",
)
skip_no_pdflatex = pytest.mark.skipif(
    not pdflatex_available,
    reason="pdflatex not found",
)


@skip_no_pipeline
def test_repr_html_returns_img_tag():
    a = Axis()
    a.addplot("x^2", domain="-2:2", samples=50)
    html = a._repr_html_()
    assert "<img" in html
    assert "data:image/png;base64," in html


@skip_no_pipeline
def test_compile_log_populated():
    a = Axis()
    a.addplot("x")
    a._repr_html_()
    assert a.compile_log() != ""


@skip_no_pdflatex
def test_save_pdf(tmp_path):
    a = Axis()
    a.addplot("x", domain="0:1")
    out = tmp_path / "plot.pdf"
    a.save_pdf(out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_compile_error_raises(monkeypatch):
    """A broken LaTeX source must raise RuntimeError and populate the log."""
    from pypgfplots._compiler import CompileResult
    import pypgfplots._core as core_mod

    def fake_compile(src):
        return CompileResult(log="! Undefined control sequence.", success=False)

    monkeypatch.setattr(core_mod, "compile_to_pdf", fake_compile)
    a = Axis()
    with pytest.raises(RuntimeError):
        a._repr_html_()
    assert "Undefined control sequence" in a.compile_log()
