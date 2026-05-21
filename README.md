# pypgfplots

Minimal Python wrapper that renders [pgfplots](https://pgfplots.sourceforge.net/) figures
as high-quality SVG inside [marimo](https://marimo.io/) notebooks.  Figures are identical
to what you would include in a LaTeX paper or slide deck — because they *are* LaTeX.

**Requires a working LaTeX installation** with `pdflatex` and `dvisvgm` on `$PATH`.

---

## Installation

### From GitHub with uv (recommended)

```bash
uv add git+https://github.com/brueffer/pypgfplots
```

### Inside a marimo notebook

Add a cell at the top:

```python
import subprocess
subprocess.run(["uv", "pip", "install", "git+https://github.com/brueffer/pypgfplots"])
```

Or use marimo's package manager sidebar (requires uv backend).

### Plain pip

```bash
pip install git+https://github.com/brueffer/pypgfplots
```

---

## Quick start

```python
from pypgfplots import Axis

a = Axis(title="Parabola", xlabel=r"$x$", ylabel=r"$f(x)$")
a.addplot(r"x^2", color="red", domain="-2:2", samples=100)
a  # displays as SVG in marimo
```

Combine two axes side by side:

```python
a = Axis(title="Left")
a.addplot(r"sin(deg(x))", domain="0:6.28")

b = Axis(title="Right", axis_lines="left")
b.addplot(r"cos(deg(x))", domain="0:6.28")

a + b  # renders both in one tikzpicture
```

### Coordinate data

```python
coords = " ".join(f"({x},{x**2})" for x in range(6))
a = Axis()
a.addplot(_type="coordinates", coords, mark="*", color="blue")
a
```

### Table data

```python
a = Axis()
a.addplot(_type="table", "data.csv", col_sep="comma", x="time", y="value")
a
```

### 3-D plots

```python
a = Axis()
a.addplot3(r"x^2 + y^2", domain="-2:2", samples=30)
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
log = a.compile_log()       # pdflatex + dvisvgm output of last run
```

---

## Pipeline

```
Python API  →  .tex (standalone + pgfplots)  →  pdflatex  →  dvisvgm  →  SVG  →  marimo
```

The SVG is delivered via `_repr_html_()` and is therefore also usable in Jupyter.

---

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
