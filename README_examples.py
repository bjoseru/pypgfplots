# /// script
# dependencies = [
#     "marimo",
#     "pypgfplots",
# ]
# requires-python = ">=3.10"
#
# [tool.uv.sources]
# pypgfplots = { git = "https://github.com/bjoseru/pypgfplots" }
# ///

import marimo

__generated_with = "0.23.7"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    from pypgfplots import Axis, Groupplot, TikzPicture
    return Axis, Groupplot, TikzPicture, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # pypgfplots — version check

        Minimal Python wrapper that renders [pgfplots](https://pgfplots.sourceforge.net/)
        figures as high-quality PNG images inside [marimo](https://marimo.io/) notebooks.
        Figures are identical to what you would include in a LaTeX paper — because they *are* LaTeX.

        **Requires** a working LaTeX installation with `pdflatex` on `$PATH`, plus one of:
        `pdftoppm` (poppler), `gs` (Ghostscript), `mutool` (mupdf), or `convert` (ImageMagick).
        """
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Quick start")


@app.cell
def _(Axis):
    a = Axis(title="Parabola", xlabel=r"$x$", ylabel=r"$f(x)$")
    a.addplot(r"x^2", color="red", domain="-2:2", samples=100)
    a
    return (a,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Combining two axes

        `a + b` merges both axes' options and `\\addplot` lines into a single axis environment.
        """
    )


@app.cell
def _(Axis):
    left = Axis(title="Left")
    left.addplot(r"sin(deg(x))", domain="0:6.28")

    right = Axis(title="Right", axis_lines="left")
    right.addplot(r"cos(deg(x))", domain="0:6.28")

    left + right


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Interactive plots

        marimo is reactive: change the slider and the plot re-renders instantly.
        """
    )


@app.cell
def _(mo):
    num_samples = mo.ui.slider(
        label="Number of samples", start=3, step=3, stop=100, value=30, debounce=True
    )
    num_samples
    return (num_samples,)


@app.cell
def _(Axis, num_samples):
    a_sine = Axis(
        title="Sine wave",
        xlabel=r"$x$",
        ylabel=r"$\sin(x)$",
        ymin=-1.5,
        ymax=1.5,
    )
    a_sine.addplot(
        r"sin(deg(x))",
        color="blue",
        thick=True,
        samples=num_samples.value,
        domain="-6.28:6.28",
        smooth=True,
    )
    a_sine.addlegendentry(r"$\sin(x)$")
    a_sine
    return (a_sine,)


@app.cell(hide_code=True)
def _(a_sine, mo):
    mo.md(
        rf"""
        LaTeX source for the plot above:

        ```latex
        {a_sine.latex()}
        ```
        """
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Coordinate data")


@app.cell
def _(Axis):
    coords = " ".join(f"({x},{x**2})" for x in range(6))
    a_coords = Axis()
    a_coords.addplot(coords, _type="coordinates", mark="*", color="blue")
    a_coords


@app.cell(hide_code=True)
def _(mo):
    mo.md("## 3-D plots")


@app.cell
def _(Axis):
    a_3d = Axis()
    a_3d.addplot3(r"x^2 + y^2", domain="-2:2", samples=30)
    a_3d


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Grouped subplots

        `Groupplot` wraps the pgfplots `groupplot` environment.
        Call `nextgroupplot()` before each subplot; all `addplot*`,
        `addlegendentry`, and `legend` methods work exactly as on `Axis`.

        > **Note:** options whose values are themselves key-value lists must be
        > wrapped in braces so the comma is not treated as an option separator,
        > e.g. `group_style="{columns=2, rows=1}"`.
        """
    )


@app.cell
def _(Groupplot):
    gp = Groupplot(group_style="{columns=2, rows=1}", width=r"0.45\textwidth")
    gp.nextgroupplot(title="Sine")
    gp.addplot(r"sin(deg(x))", domain="0:6.28", color="blue")
    gp.addlegendentry("sin")
    gp.nextgroupplot(title="Cosine")
    gp.addplot(r"cos(deg(x))", domain="0:6.28", color="red")
    gp.addlegendentry("cos")
    gp


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Raw TikZ statements

        `tikz(line)` appends a verbatim TikZ statement to the environment body.
        On `Axis`/`Groupplot` the statement lands *inside* the axis environment,
        so pgfplots coordinate systems such as `(axis cs:…)` work as expected.

        Pure geometric drawing with `TikzPicture` — the Bauhaus primary shapes:
        """
    )


@app.cell
def _(TikzPicture):
    p = TikzPicture()
    p.tikz(r"\fill[red]    (0,0) rectangle (2,2);")
    p.tikz(r"\fill[blue]   (3,1) circle (1);")
    p.tikz(r"\fill[yellow] (5,0) -- (7,0) -- (6,1.732) -- cycle;")
    p


@app.cell(hide_code=True)
def _(mo):
    mo.md("Annotating a plot with a dashed reference line and a label:")


@app.cell
def _(Axis):
    a_ann = Axis(xlabel=r"$x$", ylabel=r"$f(x)$")
    a_ann.addplot(r"x^2", domain="-2:2", color="blue")
    a_ann.tikz(r"\draw[dashed, gray] (axis cs:-2,1) -- (axis cs:2,1);")
    a_ann.tikz(r"\node[right] at (axis cs:2,1) {$y=1$};")
    a_ann


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Legend images

        `addlegendimage` inserts a phantom legend entry with a custom appearance —
        useful when the auto-generated swatch does not match what you want.
        """
    )


@app.cell
def _(Axis):
    a_leg = Axis()
    a_leg.addplot(r"x^2", color="red")
    a_leg.addlegendimage(color="red", mark="*")
    a_leg.addlegendentry(r"$x^2$")
    a_leg


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Global settings

        These functions affect all axis objects created afterwards in the session:

        ```python
        from pypgfplots import pgfplotset, preamble, classoptions

        pgfplotset(compat="1.18")            # passed to \pgfplotsset{...}
        preamble(r"\usepackage{amsmath}")    # added to the document preamble
        classoptions("border=5pt")           # added to \documentclass[...]{standalone}
        ```
        """
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Export

        ```python
        a.save_pdf("figure.pdf")   # compile and write PDF
        a.save_tex("figure.tex")   # write LaTeX source (no compilation)
        src = a.latex()             # full standalone source as a string
        log = a.compile_log()       # pdflatex output of the last run
        ```
        """
    )


if __name__ == "__main__":
    app.run()
