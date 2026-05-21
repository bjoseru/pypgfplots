"""Module-level global state for pypgfplots."""

from __future__ import annotations

_preamble_lines: list[str] = []
_pgfplotset_opts: dict[str, str] = {}
_classoptions_list: list[str] = []


def preamble(text: str) -> None:
    """Append *text* to the global LaTeX preamble."""
    _preamble_lines.append(text)


def pgfplotset(**kwargs) -> None:
    r"""Set global \pgfplotsset options (e.g. pgfplotset(compat="1.18"))."""
    _pgfplotset_opts.update(kwargs)


def classoptions(opts: str) -> None:
    r"""Append *opts* to the \documentclass options of the standalone class."""
    _classoptions_list.append(opts)


# --- accessors (internal use) ------------------------------------------------

def get_preamble() -> list[str]:
    return _preamble_lines


def get_pgfplotset() -> dict[str, str]:
    return _pgfplotset_opts


def get_classoptions() -> list[str]:
    return _classoptions_list


def _reset() -> None:
    """Reset all global state (intended for use in tests)."""
    _preamble_lines.clear()
    _pgfplotset_opts.clear()
    _classoptions_list.clear()
