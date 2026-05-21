"""Compiler tests – skipped when pdflatex/dvisvgm are not installed."""

import shutil
import pytest
from pypgfplots import Axis

pdflatex_available = shutil.which("pdflatex") is not None
dvisvgm_available = shutil.which("dvisvgm") is not None
latex_available = pdflatex_available and dvisvgm_available

skip_no_latex = pytest.mark.skipif(
    not latex_available,
    reason="pdflatex and/or dvisvgm not found",
)


@skip_no_latex
def test_compile_simple_axis():
    a = Axis()
    a.addplot("x^2", domain="-2:2", samples=50)
    svg = a._run_compile()
    assert "<svg" in svg


@skip_no_latex
def test_compile_log_populated():
    a = Axis()
    a.addplot("x")
    a._run_compile()
    assert a.compile_log() != ""


@skip_no_latex
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

    monkeypatch.setattr(core_mod, "compile_tex", fake_compile)
    a = Axis()
    with pytest.raises(RuntimeError):
        a._run_compile()
    assert "Undefined control sequence" in a.compile_log()
