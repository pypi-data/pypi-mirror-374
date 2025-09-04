# markdown-it-accel

**Rust-accelerated backend for markdown-it-py**

[![CI](https://github.com/ChungNYCU/markdown-it-accel/actions/workflows/ci.yml/badge.svg)](https://github.com/ChungNYCU/markdown-it-accel/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/markdown-it-accel.svg)](https://badge.fury.io/py/markdown-it-accel)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

`markdown-it-accel` provides a drop-in Rust-accelerated backend for [markdown-it-py](https://github.com/executablebooks/markdown-it-py), offering significant performance improvements for markdown rendering while maintaining full compatibility with the original Python implementation.

## Features

- **Blazing fast performance**: Up to 80x speedup on typical documents, 200x+ on large documents
- **Drop-in acceleration**: Simply import and apply to existing markdown-it-py instances
- **Automatic fallback**: Gracefully falls back to Python implementation when needed
- **Full CommonMark support**: Powered by [pulldown-cmark](https://github.com/raphlinus/pulldown-cmark)
- **Cross-platform**: Pre-built wheels for Linux, macOS, and Windows
- **Python 3.8+ support**: Compatible with modern Python versions

## Installation

Install from PyPI:

```bash
pip install markdown-it-accel
```

For development or building from source:

```bash
# Clone the repository
git clone https://github.com/ChungNYCU/markdown-it-accel.git
cd markdown-it-accel

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install in development mode
pip install maturin
maturin develop
```

## Quick Start

```python
from markdown_it import MarkdownIt
from markdown_it_accel import use_rust_core

# Create a markdown-it-py instance
md = MarkdownIt()

# Apply Rust acceleration
use_rust_core(md)

# Use as normal - now with Rust speed!
html = md.render("# Hello, *World*!")
print(html)  # <h1>Hello, <em>World</em>!</h1>
```

## Performance

Based on comprehensive benchmarking, `markdown-it-accel` delivers significant performance improvements:

### Performance Results

**Overall Speedup: 67x faster on average**

| Document Type | Size | Python Time | Rust Time | Speedup |
|---------------|------|-------------|-----------|---------|
| BIG.md | 8.0KB | 5.69ms | 71.3μs | **79.88x** |
| CODE_HEAVY.md | 8.7KB | 1.28ms | 27.6μs | **46.56x** |
| HUGE.md | 434KB | 230.80ms | 3.57ms | **64.68x** |
| TABLE_HEAVY.md | 2.1KB | 3.55ms | 46.5μs | **76.36x** |

### Library Comparison

Compared to other Python markdown libraries:

| Library | Time | Throughput | Relative Performance |
|---------|------|------------|---------------------|
| **markdown-it-accel (Rust)** | 80.1μs | 100.5M chars/sec | **Fastest** |
| markdown-it-py (Python) | 5.72ms | 1.4M chars/sec | 71x slower |
| python-markdown | 25.00ms | 322K chars/sec | 312x slower |

### Scaling Performance

Performance scales excellently with document size:
- **1x size**: 38x speedup
- **10x size**: 132x speedup  
- **50x size**: 201x speedup

Run benchmarks on your system:

```bash
# Comprehensive benchmark suite
python bench/scripts/benchmark.py

# Library comparison
python bench/scripts/compare_libraries.py
```

## Configuration

### Environment Variables

- `MARKDOWN_IT_ACCEL=0`: Disable Rust acceleration (fallback to Python)
- `MARKDOWN_IT_ACCEL=1`: Enable Rust acceleration (default)

```bash
# Disable Rust acceleration
MARKDOWN_IT_ACCEL=0 python your_script.py

# Enable Rust acceleration (default behavior)  
MARKDOWN_IT_ACCEL=1 python your_script.py
```

### Checking Availability

```python
from markdown_it_accel import is_available, get_version

print(f"Rust acceleration available: {is_available()}")
print(get_version())
```

## Compatibility

### Supported Features

- Headers (`#`, `##`, etc.)
- Emphasis (`*italic*`, `**bold**`)
- Links (`[text](url)`)
- Images (`![alt](src)`)
- Lists (ordered and unordered)
- Code blocks (fenced and indented)
- Blockquotes (`>`)
- Tables (GFM extension)
- Strikethrough (`~~text~~`) 
- Line breaks and paragraphs

### Fallback Behavior

The library automatically falls back to the Python implementation when:

- Rust extension is not available (installation without binary wheels)
- Unsupported syntax is detected
- Rust renderer encounters an error

This ensures your code continues to work regardless of the environment.

### Limitations

Currently, some advanced markdown-it-py features may trigger fallback:

- Custom plugins and renderers
- Complex HTML blocks
- Math expressions (`$$...$$`)
- Mermaid diagrams

## Development

### Prerequisites

- Python 3.8+
- Rust 1.70+
- [maturin](https://github.com/PyO3/maturin)

### Setup

```bash
# Clone and enter directory
git clone https://github.com/ChungNYCU/markdown-it-accel.git
cd markdown-it-accel

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .[dev]
```

### Building

```bash
# Development build
maturin develop

# Release build
maturin develop --release

# Build wheels
maturin build --release
```

### Testing

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=markdown_it_accel

# Run benchmarks
python bench/bench_render.py
```

### Code Quality

```bash
# Format Python code
black .

# Lint Python code  
ruff check .

# Format Rust code
cargo fmt

# Lint Rust code
cargo clippy
```

## Architecture

The library consists of three main components:

1. **Rust Core** (`src/lib.rs`): PyO3 module using pulldown-cmark for fast HTML generation
2. **Python Shim** (`markdown_it_accel/_shim.py`): Monkey-patches markdown-it-py instances
3. **Fallback Logic**: Automatic detection and graceful degradation

### How It Works

```python
# Before acceleration
md = MarkdownIt()
html = md.render(text)  # Pure Python

# After acceleration  
use_rust_core(md)
html = md.render(text)  # Rust + Python fallback
```

The `use_rust_core()` function replaces the `render` method with a wrapper that:

1. Checks if content is supported by Rust implementation
2. Attempts fast Rust rendering via `pulldown-cmark`
3. Falls back to original Python implementation on any issue

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) - The Python markdown parser this library accelerates
- [pulldown-cmark](https://github.com/raphlinus/pulldown-cmark) - The fast Rust markdown parser powering the acceleration
- [PyO3](https://github.com/PyO3/pyo3) - Rust bindings for Python
- [maturin](https://github.com/PyO3/maturin) - Build system for Rust-based Python extensions

## Changelog

### 0.1.0 (2025-09-03)

- Initial release
- Basic CommonMark support with Rust acceleration
- Automatic fallback mechanism
- Cross-platform binary wheels
- Comprehensive test suite and benchmarks