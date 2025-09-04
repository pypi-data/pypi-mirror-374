"""Type hints for the Rust module."""

def render_html(text: str) -> str:
    """
    Render markdown text to HTML using pulldown-cmark.

    Args:
        text: The markdown text to render

    Returns:
        The rendered HTML string

    Raises:
        Exception: If rendering fails
    """
    ...

def is_supported(text: str) -> bool:
    """
    Check if a markdown string contains features that may not be supported.

    Args:
        text: The markdown text to check

    Returns:
        True if the content is supported, False otherwise
    """
    ...

def version() -> str:
    """
    Get version information for the Rust module.

    Returns:
        Version string
    """
    ...
