import pytest
import pypgfplots._global as _glob


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset module-level global state before every test."""
    _glob._reset()
    yield
    _glob._reset()
