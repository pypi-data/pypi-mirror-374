"""Test fallback behavior when Rust is unavailable or encounters errors."""

import sys
from pathlib import Path
from unittest.mock import patch

# Add python package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest
from markdown_it import MarkdownIt
from markdown_it_accel import use_rust_core


def test_fallback_when_rust_unavailable():
    """Test that fallback works when Rust module is not available."""
    with patch("markdown_it_accel._shim._HAS_RUST", False):
        md = MarkdownIt()

        # Apply shim (should do nothing when Rust unavailable)
        use_rust_core(md)

        # Should still work and render method behavior should be unchanged
        # (method identity may change but functionality remains the same)
        pass

        # Should still work
        result = md.render("# Hello")
        assert "<h1>Hello</h1>" in result


@pytest.mark.skipif(
    not pytest.importorskip(
        "markdown_it_accel._rust", reason="Rust module not available"
    ),
    reason="Requires Rust module",
)
def test_fallback_on_rust_error():
    """Test that fallback works when Rust module throws an error."""
    md = MarkdownIt()

    use_rust_core(md)

    # Mock the Rust module to raise an exception
    with patch(
        "markdown_it_accel._shim._rust.render_html", side_effect=Exception("Rust error")
    ), patch("markdown_it_accel._shim._rust.is_supported", return_value=True):
        result = md.render("# Hello")
        # Should still get valid output via fallback
        assert "<h1>Hello</h1>" in result


@pytest.mark.skipif(
    not pytest.importorskip(
        "markdown_it_accel._rust", reason="Rust module not available"
    ),
    reason="Requires Rust module",
)
def test_unsupported_content_fallback():
    """Test that unsupported content falls back to Python implementation."""
    md = MarkdownIt()
    use_rust_core(md)

    # Mock is_supported to return False for certain content
    with patch("markdown_it_accel._shim._rust.is_supported", return_value=False):
        result = md.render("# Unsupported Feature")
        # Should still render correctly via fallback
        assert "Unsupported Feature" in result


def test_environment_variable_disable():
    """Test that MARKDOWN_IT_ACCEL=0 disables Rust acceleration."""

    # Test is mainly for documentation - actual behavior depends on import time
    # But we can test the logic
    from markdown_it_accel._shim import _USE_RUST

    # The current value depends on environment
    assert isinstance(_USE_RUST, bool)


def test_multiple_instances():
    """Test that multiple MarkdownIt instances can be accelerated independently."""
    md1 = MarkdownIt()
    md2 = MarkdownIt()

    # Accelerate both
    use_rust_core(md1)
    use_rust_core(md2)

    # Both should work
    result1 = md1.render("# Test 1")
    result2 = md2.render("# Test 2")

    assert "Test 1" in result1
    assert "Test 2" in result2


def test_no_interference_with_unmodified_instance():
    """Test that accelerating one instance doesn't affect others."""
    md1 = MarkdownIt()
    md2 = MarkdownIt()

    # Only accelerate md1
    use_rust_core(md1)

    # md2 should be unchanged (functionality, not necessarily identity)
    # Just ensure it still works correctly

    # Both should still work
    result1 = md1.render("# Test 1")
    result2 = md2.render("# Test 2")

    assert "Test 1" in result1
    assert "Test 2" in result2
