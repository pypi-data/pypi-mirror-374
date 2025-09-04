"""Shim to monkey-patch markdown-it-py with Rust acceleration."""

import os
from typing import Any, Dict, Optional

# Check if Rust acceleration should be used
_USE_RUST = os.environ.get("MARKDOWN_IT_ACCEL", "1").lower() in (
    "1",
    "true",
    "yes",
    "on",
)

try:
    if _USE_RUST:
        from . import _rust

        _HAS_RUST = True
    else:
        _HAS_RUST = False
except ImportError:
    _HAS_RUST = False


def use_rust_core(md: Any) -> None:
    """
    Monkey-patch a markdown-it-py instance to use Rust acceleration.

    Args:
        md: A markdown-it-py MarkdownIt instance

    This function will replace the render method with a Rust-accelerated version
    that falls back to the original implementation on errors or unsupported syntax.
    """
    if not _HAS_RUST:
        return

    # Store original render method
    _original_render = md.render

    def _accelerated_render(src: str, env: Optional[Dict[str, Any]] = None) -> str:
        """Rust-accelerated render with fallback."""
        try:
            # Check if the content is supported by our Rust implementation
            if _rust.is_supported(src):
                return _rust.render_html(src)
            else:
                # Fall back to original for unsupported features
                return _original_render(src, env)
        except Exception:
            # Fall back to original on any error
            return _original_render(src, env)

    # Replace the render method
    md.render = _accelerated_render
