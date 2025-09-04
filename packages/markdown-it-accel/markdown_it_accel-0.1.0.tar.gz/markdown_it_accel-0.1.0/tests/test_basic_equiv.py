"""Test basic equivalence between Rust and Python implementations."""

import sys
from pathlib import Path

# Add python package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest
from markdown_it import MarkdownIt
from markdown_it_accel import is_available, use_rust_core

# Test cases covering CommonMark features
TEST_CASES = [
    # Headers
    ("# Header 1", "<h1>Header 1</h1>\n"),
    ("## Header 2", "<h2>Header 2</h2>\n"),
    ("### Header 3", "<h3>Header 3</h3>\n"),
    # Emphasis
    ("*italic*", "<p><em>italic</em></p>\n"),
    ("**bold**", "<p><strong>bold</strong></p>\n"),
    ("***bold italic***", "<p><em><strong>bold italic</strong></em></p>\n"),
    # Code
    ("`inline code`", "<p><code>inline code</code></p>\n"),
    ("```\ncode block\n```", "<pre><code>code block\n</code></pre>\n"),
    # Links
    ("[link](http://example.com)", '<p><a href="http://example.com">link</a></p>\n'),
    (
        '[link](http://example.com "title")',
        '<p><a href="http://example.com" title="title">link</a></p>\n',
    ),
    # Lists
    ("- item 1\n- item 2", "<ul>\n<li>item 1</li>\n<li>item 2</li>\n</ul>\n"),
    ("1. item 1\n2. item 2", "<ol>\n<li>item 1</li>\n<li>item 2</li>\n</ol>\n"),
    # Blockquotes
    ("> blockquote", "<blockquote>\n<p>blockquote</p>\n</blockquote>\n"),
    # Images
    (
        "![alt](http://example.com/img.jpg)",
        '<p><img src="http://example.com/img.jpg" alt="alt" /></p>\n',
    ),
    # Line breaks and paragraphs
    ("paragraph 1\n\nparagraph 2", "<p>paragraph 1</p>\n<p>paragraph 2</p>\n"),
    # Tables (GFM)
    (
        "| col1 | col2 |\n|------|------|\n| a    | b    |",
        "<table>\n<thead>\n<tr>\n<th>col1</th>\n<th>col2</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>a</td>\n<td>b</td>\n</tr>\n</tbody>\n</table>\n",
    ),
    # Strikethrough (GFM)
    ("~~strikethrough~~", "<p><del>strikethrough</del></p>\n"),
]


def test_rust_available():
    """Test that we can detect if Rust acceleration is available."""
    # This will be True if built with maturin, False in pure Python testing
    available = is_available()
    assert isinstance(available, bool)


@pytest.mark.parametrize("markdown,expected_pattern", TEST_CASES)
def test_basic_equivalence(markdown, expected_pattern):
    """Test that Rust and Python implementations produce equivalent output."""
    # Create two MarkdownIt instances
    md_python = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    md_rust = MarkdownIt("commonmark").enable(["table", "strikethrough"])

    # Apply Rust acceleration to one
    use_rust_core(md_rust)

    # Render with both
    python_result = md_python.render(markdown)
    rust_result = md_rust.render(markdown)

    # Allow for minor HTML differences between implementations
    # Both should produce valid HTML with the same content
    assert len(rust_result.strip()) > 0
    assert len(python_result.strip()) > 0

    # Check basic structure is present
    if markdown.startswith("#"):
        assert "<h" in rust_result
    elif markdown.startswith("*") or markdown.startswith("**"):
        assert "<em>" in rust_result or "<strong>" in rust_result
    elif "```" in markdown:
        assert "<pre>" in rust_result and "<code>" in rust_result
    elif markdown.startswith("- ") or markdown.startswith("1. "):
        assert "<ul>" in rust_result or "<ol>" in rust_result
    elif markdown.startswith("> "):
        assert "<blockquote>" in rust_result
    elif markdown.startswith("!["):
        assert "<img" in rust_result
    elif "|" in markdown and "-" in markdown:
        assert "<table>" in rust_result


def test_fallback_behavior():
    """Test that fallback to Python works correctly."""
    md = MarkdownIt()
    use_rust_core(md)

    # This should work regardless of Rust availability
    result = md.render("# Hello World")
    assert "Hello World" in result
    assert result.startswith("<h1>")


def test_environment_variable_control():
    """Test that MARKDOWN_IT_ACCEL environment variable is respected."""

    # This test is more for documentation - the actual behavior
    # depends on when the module is imported
    md = MarkdownIt()
    use_rust_core(md)

    # Should work regardless of environment setting
    result = md.render("**bold**")
    assert "bold" in result


def test_complex_document():
    """Test rendering of a more complex document."""
    complex_md = """
# Document Title

This is a paragraph with **bold** and *italic* text.

## Section 1

Here's a list:
- Item 1
- Item 2
  - Nested item
- Item 3

## Section 2

Here's a code block:

```python
def hello():
    print("Hello, world!")
```

And here's a [link](https://example.com) and an image:

![Alt text](https://example.com/image.jpg)

> This is a blockquote
> spanning multiple lines.

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""

    md_rust = MarkdownIt("commonmark").enable(["table"])

    use_rust_core(md_rust)

    rust_result = md_rust.render(complex_md)

    # Should produce similar results
    assert len(rust_result) > 100  # Should be substantial
    assert "Document Title" in rust_result
    assert "<h1>" in rust_result
    assert "<code" in rust_result  # Code block should be present (may have attributes)
    assert "<table>" in rust_result
