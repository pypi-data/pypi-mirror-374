"""markdown-it-accel: Rust-accelerated backend for markdown-it-py."""

from ._shim import use_rust_core

__version__ = "0.1.0"
__all__ = ["use_rust_core", "is_available"]


def is_available() -> bool:
    """Check if the Rust acceleration is available."""
    try:
        from . import _rust  # noqa: F401

        return True
    except ImportError:
        return False


def get_version() -> str:
    """Get version information."""
    if is_available():
        from . import _rust

        return f"markdown-it-accel {__version__} (rust: {_rust.version()})"
    else:
        return f"markdown-it-accel {__version__} (rust: unavailable)"
