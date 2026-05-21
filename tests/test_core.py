import pytest
from pypgfplots import Axis, TikzPicture, classoptions, pgfplotset, preamble


# ---------------------------------------------------------------------------
# Axis option defaults and overrides
# ---------------------------------------------------------------------------

def test_axis_default_axis_lines():
    a = Axis()
    assert "axis lines=center" in a.latex()


def test_axis_override_axis_lines():
    a = Axis(axis_lines="left")
    assert "axis lines=left" in a.latex()
    assert "axis lines=center" not in a.latex()


def test_axis_kwargs_become_options():
    a = Axis(title="My Plot", xlabel="$x$")
    tex = a.latex()
    assert "title=My Plot" in tex
    assert "xlabel=$x$" in tex


def test_axis_dict_arg_no_transform():
    a = Axis({"/tikz/font": "\\small"})
    assert "/tikz/font=\\small" in a.latex()


def test_axis_string_arg_raw():
    a = Axis("scale=1.5")
    assert "scale=1.5" in a.latex()


# ---------------------------------------------------------------------------
# addplot variants
# ---------------------------------------------------------------------------

def test_addplot_expression():
    a = Axis()
    a.addplot("x^2")
    assert "\\addplot{x^2};" in a.latex()


def test_addplot_with_opts():
    a = Axis()
    a.addplot("x^2", color="red", domain="-2:2")
    tex = a.latex()
    assert "\\addplot[" in tex
    assert "color=red" in tex
    assert "domain=-2:2" in tex
    assert "{x^2};" in tex


def test_addplot_type():
    a = Axis()
    a.addplot("(0,0) (1,1)", _type="coordinates")
    assert "\\addplot coordinates{(0,0) (1,1)};" in a.latex()


def test_addplot_plus_via_arg():
    a = Axis()
    a.addplot("+", "x^2")
    assert "\\addplot+{x^2};" in a.latex()


def test_addplot_plus_method():
    a = Axis()
    a.addplot_plus("x^2")
    assert "\\addplot+{x^2};" in a.latex()


def test_addplot3():
    a = Axis()
    a.addplot3("x^2+y^2")
    assert "\\addplot3{x^2+y^2};" in a.latex()


def test_addplot_dict_opts():
    a = Axis()
    a.addplot({"/tikz/color": "blue"}, "x")
    tex = a.latex()
    assert "/tikz/color=blue" in tex


# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------

def test_addlegendentry():
    a = Axis()
    a.addplot("x^2")
    a.addlegendentry(r"$x^2$")
    assert "\\addlegendentry{$x^2$}" in a.latex()


def test_legend():
    a = Axis()
    a.addplot("x")
    a.addplot("x^2")
    a.legend("linear", "quadratic")
    assert "\\legend{linear,quadratic}" in a.latex()


# ---------------------------------------------------------------------------
# Addition
# ---------------------------------------------------------------------------

def test_axis_add_returns_axis():
    a = Axis()
    b = Axis(axis_lines="left")
    result = a + b
    assert isinstance(result, Axis)


def test_axis_add_merges_plots_into_single_axis():
    a = Axis(title="A")
    b = Axis(title="B")
    a.addplot("x")
    b.addplot("x^2")
    combined = a + b
    tex = combined.latex()
    # both options present, only one axis environment
    assert tex.count("\\begin{axis}") == 1
    assert "title=A" in tex
    assert "title=B" in tex
    assert "\\addplot{x};" in tex
    assert "\\addplot{x^2};" in tex


def test_axis_add_preambles_merged():
    a = Axis()
    a.preamble("\\usepackage{amsmath}")
    b = Axis()
    b.preamble("\\usepackage{xcolor}")
    tex = (a + b).latex()
    assert "\\usepackage{amsmath}" in tex
    assert "\\usepackage{xcolor}" in tex


# ---------------------------------------------------------------------------
# Instance preamble
# ---------------------------------------------------------------------------

def test_instance_preamble():
    a = Axis()
    a.preamble("\\usepackage{amsmath}")
    assert "\\usepackage{amsmath}" in a.latex()


# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

def test_global_preamble():
    preamble("\\usepackage{amsmath}")
    a = Axis()
    assert "\\usepackage{amsmath}" in a.latex()


def test_pgfplotset_compat():
    pgfplotset(compat="1.18")
    a = Axis()
    assert "compat=1.18" in a.latex()


def test_classoptions():
    classoptions("tikz")
    a = Axis()
    assert "[tikz]" in a.latex()


# ---------------------------------------------------------------------------
# latex() structure
# ---------------------------------------------------------------------------

def test_latex_standalone_structure():
    a = Axis()
    tex = a.latex()
    assert "\\documentclass" in tex
    assert "\\usepackage{pgfplots}" in tex
    assert "\\begin{document}" in tex
    assert "\\begin{tikzpicture}" in tex
    assert "\\begin{axis}" in tex
    assert "\\end{axis}" in tex
    assert "\\end{tikzpicture}" in tex
    assert "\\end{document}" in tex


# ---------------------------------------------------------------------------
# save_tex
# ---------------------------------------------------------------------------

def test_save_tex(tmp_path):
    a = Axis()
    a.addplot("x^2")
    out = tmp_path / "plot.tex"
    a.save_tex(out)
    content = out.read_text()
    assert "\\addplot{x^2};" in content
