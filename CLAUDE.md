# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in editable mode (development)
uv pip install -e ".[dev]"
# or without dev extras:
uv pip install -e .

# Run all tests
pytest

# Run a single test file
pytest tests/test_core.py

# Run a single test
pytest tests/test_core.py::test_addplot_expression

# Compiler tests require pdflatex + dvisvgm on PATH; they are auto-skipped otherwise
pytest tests/test_compiler.py -v
```

## Architecture

```
pypgfplots/
├── _global.py    module-level mutable state (pgfplotset opts, preamble lines, classoptions)
├── _options.py   pure functions: Python kwargs/dicts → pgfplots option strings
├── _compiler.py  subprocess pipeline: LaTeX source → CompileResult (pdf_bytes, svg_string, log)
├── _core.py      TikzPicture and Axis classes
└── __init__.py   public re-exports: Axis, TikzPicture, pgfplotset, preamble, classoptions
```

### Key design decisions

**Lazy compilation.** No LaTeX is run at construction time. `_repr_html_()` triggers compilation when the object is displayed in marimo. `save_pdf()` and `save_tex()` are explicit export paths.

**String accumulation.** `Axis._axis_body` is a raw string that grows with each `addplot*` call. `TikzPicture._tikz_content` holds the full tikzpicture body. `_get_tikz_content()` is the polymorphic hook that wraps the axis body in `\begin{axis}...\end{axis}` for Axis instances. Both are assembled into the full standalone document only in `latex()`.

**Axis addition.** `TikzPicture.__add__` calls `_get_tikz_content()` on both operands (picking up overridden versions in subclasses) and stores the concatenated result in a plain `TikzPicture._tikz_content`. The result is always a `TikzPicture`, not an `Axis`.

**Options translation.** `_options.py` contains three pure functions:
- `kwargs_to_pgf`: replaces `_` with space in keys (Python identifier → pgfplots key)
- `dict_to_pgf`: no key transformation (for keys containing `/` or other special chars)
- `merge_opts`: joins non-empty option strings with commas

**Global state and testing.** `_global.py` holds three module-level lists/dicts. `_reset()` clears all of them. `tests/conftest.py` calls `_reset()` via an `autouse` fixture before and after every test.

**Compiler modularity.** `_compiler.py` exports a single function `compile_tex(tex_source: str) -> CompileResult`. Swapping the backend (e.g. latexmk, tectonic, caching) requires only replacing this function without touching the core classes. The `_core.py` import is:
```python
from ._compiler import compile_tex
```

**addplot dispatch.** All three addplot methods (`addplot`, `addplot_plus`, `addplot3`) delegate to `_addplot_impl(base_cmd, *args, **kwargs)`.  The `+` variant can be reached via the `base_cmd` (`\addplot+`) or by passing `'+'` as the first positional arg to `addplot`.  `_type=` is a reserved kwarg that inserts a type specifier between the command and the body.

## Current status

Initial implementation. API is functional but not yet battle-tested against real pgfplots usage. The compiler tests are integration tests and require a LaTeX installation.
