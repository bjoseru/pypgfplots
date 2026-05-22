# pypgfplots

[![Open in molab](https://molab.marimo.io/molab-shield.svg)](https://molab.marimo.io/notebooks/nb_zAMdaoX6YdspQ27p68YBuT)

Minimal Python wrapper that renders [pgfplots](https://pgfplots.sourceforge.net/) figures
as high-quality PNG inside [marimo](https://marimo.io/) notebooks.  Figures are identical
to what you would include in a LaTeX paper or slide deck — because they *are* LaTeX.

**Requires** a working LaTeX installation with `pdflatex` on `$PATH`, plus a PDF→PNG
converter — install one of:

```bash
brew install poppler       # provides pdftoppm (recommended)
brew install mupdf-tools   # provides mutool
brew install imagemagick   # provides convert
```

Ghostscript (`gs`) is also accepted if already on `$PATH`.

---

## Installation

### From GitHub with uv (recommended)

```bash
uv add git+https://github.com/bjoseru/pypgfplots
```

### Inside a marimo notebook

Add a cell at the top:

```python
import subprocess
subprocess.run(["uv", "pip", "install", "git+https://github.com/bjoseru/pypgfplots"])
```

Or use marimo's package manager sidebar (requires uv backend).

### Plain pip

```bash
pip install git+https://github.com/bjoseru/pypgfplots
```

---

## Quick start

```python
from pypgfplots import Axis

a = Axis(title="Parabola", xlabel=r"$x$", ylabel=r"$f(x)$")
a.addplot(r"x^2", color="red", domain="-2:2", samples=100)
a  # displays as PNG in marimo
```

Combine two axes side by side:

```python
a = Axis(title="Left")
a.addplot(r"sin(deg(x))", domain="0:6.28")

b = Axis(title="Right", axis_lines="left")
b.addplot(r"cos(deg(x))", domain="0:6.28")

a + b  # renders both in one tikzpicture
```

### Raw TikZ statements

`tikz(line)` appends a verbatim TikZ statement to the environment body — available on `TikzPicture`, `Axis`, and `Groupplot`.  On `Axis`/`Groupplot` the statement lands inside the axis environment, so pgfplots coordinate systems such as `(axis cs:…)` work as expected.

Pure geometric drawing with `TikzPicture`:

```python
from pypgfplots import TikzPicture

p = TikzPicture()
p.tikz(r"\fill[red]    (0,0) rectangle (2,2);")          # Bauhaus square
p.tikz(r"\fill[blue]   (3,1) circle (1);")               # Bauhaus disc
p.tikz(r"\fill[yellow] (5,0) -- (7,0) -- (6,1.732) -- cycle;")  # Bauhaus triangle
p
```

Annotating a plot with a dashed reference line and a label:

```python
a = Axis(xlabel=r"$x$", ylabel=r"$f(x)$")
a.addplot(r"x^2", domain="-2:2", color="blue")
a.tikz(r"\draw[dashed, gray] (axis cs:-2,1) -- (axis cs:2,1);")
a.tikz(r"\node[right] at (axis cs:2,1) {$y=1$};")
a
```

### Coordinate data

```python
coords = " ".join(f"({x},{x**2})" for x in range(6))
a = Axis()
a.addplot(coords, _type="coordinates", mark="*", color="blue")
a
```

### Table data

```python
a = Axis()
a.addplot("data.csv", _type="table", col_sep="comma", x="time", y="value")
a
```

### 3-D plots

```python
a = Axis()
a.addplot3(r"x^2 + y^2", domain="-2:2", samples=30)
a
```

### Grouped subplots

`Groupplot` produces a pgfplots `groupplot` environment.  Call `nextgroupplot()` before each subplot; all `addplot*`, `addlegendentry`, and `legend` methods work exactly as on `Axis`.

```python
from pypgfplots import Groupplot

gp = Groupplot(group_style="{columns=2, rows=1}", width="0.45\\textwidth")
gp.nextgroupplot(title="Sine")
gp.addplot(r"sin(deg(x))", domain="0:6.28", color="blue")
gp.addlegendentry("sin")

gp.nextgroupplot(title="Cosine")
gp.addplot(r"cos(deg(x))", domain="0:6.28", color="red")
gp.addlegendentry("cos")

gp  # displays as PNG in marimo
```

Options passed to `Groupplot(...)` become `\begin{groupplot}[...]` options; options passed to `nextgroupplot(...)` become per-subplot options.  The `\usepgfplotslibrary{groupplots}` line is added to the preamble automatically.

> **Note on nested key-value options:** pgfplots options whose values are themselves key-value lists (such as `group style`) must be wrapped in braces so the comma is not interpreted as an option separator: `group_style="{columns=2, rows=1}"`.  The same applies to any option like `legend style`, `axis background/.style`, etc.

### Legend images

`addlegendimage` inserts a phantom legend entry with a custom appearance — useful when the auto-generated swatch does not match what you want:

```python
a = Axis()
a.addplot(r"x^2", color="red")
a.addlegendimage(color="red", mark="*")
a.addlegendentry(r"$x^2$")
a
```

### Global settings

```python
from pypgfplots import pgfplotset, preamble, classoptions

pgfplotset(compat="1.18")
preamble(r"\usepackage{amsmath}")
classoptions("border=5pt")
```

---

## Export

```python
a.save_pdf("figure.pdf")   # compile and write PDF
a.save_tex("figure.tex")   # write LaTeX source (no compilation)
src = a.latex()             # full standalone source as string
log = a.compile_log()       # pdflatex output of last run
```

---

## Development

Clone the repo and install in editable mode:

```bash
git clone https://github.com/bjoseru/pypgfplots
cd pypgfplots
uv pip install -e .
```

Run the tests:

```bash
uv run --with pytest pytest
```

Tests that require `pdflatex` and a PDF→PNG converter are skipped automatically if those tools are not on `$PATH`.  To run only the pure-Python unit tests:

```bash
uv run --with pytest pytest tests/test_core.py tests/test_options.py
```

---

## Pipeline

```
Display:  Python API  →  .tex  →  pdflatex  →  PDF  →  pdftoppm  →  PNG  →  marimo
PDF:      Python API  →  .tex  →  pdflatex  →  PDF
```

The PNG is delivered via `_repr_html_()` and is therefore also usable in Jupyter.

---

## License

MIT — see [LICENSE](LICENSE).
