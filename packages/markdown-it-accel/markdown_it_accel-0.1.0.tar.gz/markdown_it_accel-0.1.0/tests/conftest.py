"""Pytest configuration for markdown-it-accel tests."""

import pytest


@pytest.fixture(scope="session")
def rust_available():
    """Check if Rust extension is available for testing."""
    try:
        import markdown_it_accel._rust  # noqa: F401

        return True
    except ImportError:
        return False


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "requires_rust: mark test as requiring Rust extension"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests that require Rust when it's not available."""
    try:
        import markdown_it_accel._rust  # noqa: F401

        rust_available = True
    except ImportError:
        rust_available = False

    if not rust_available:
        skip_rust = pytest.mark.skip(reason="Rust extension not available")
        for item in items:
            if "requires_rust" in item.keywords:
                item.add_marker(skip_rust)
