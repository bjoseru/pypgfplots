"""Conversion of Python kwargs/dicts to pgfplots option strings."""

from __future__ import annotations


def kwargs_to_pgf(kwargs: dict) -> str:
    """Convert Python keyword arguments to a pgfplots option string.

    Underscores in keys are replaced with spaces, e.g. axis_lines -> axis lines.
    True values become bare keys; False values are omitted.
    """
    parts = []
    for k, v in kwargs.items():
        key = k.replace("_", " ")
        if v is True:
            parts.append(key)
        elif v is False:
            pass
        else:
            parts.append(f"{key}={v}")
    return ",".join(parts)


def dict_to_pgf(d: dict) -> str:
    """Convert a raw dict to a pgfplots option string without key transformation.

    Use this for options whose keys contain characters like '/' that cannot
    appear in Python identifiers.
    """
    parts = []
    for k, v in d.items():
        if v is True:
            parts.append(str(k))
        elif v is False:
            pass
        else:
            parts.append(f"{k}={v}")
    return ",".join(parts)


def merge_opts(*opt_strings: str) -> str:
    """Join non-empty option strings with commas."""
    return ",".join(s for s in opt_strings if s)
