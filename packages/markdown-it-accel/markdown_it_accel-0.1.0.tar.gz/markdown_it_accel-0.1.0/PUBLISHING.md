# PyPI Publishing Guide

This document outlines the requirements and process for publishing `markdown-it-accel` to PyPI.

## Requirements Met ✅

### Package Metadata
- ✅ Complete `pyproject.toml` with all required PyPI fields
- ✅ Comprehensive classifiers for discoverability
- ✅ Keywords optimized for search
- ✅ License (MIT) and author information
- ✅ Project URLs (homepage, repository, issues, docs)
- ✅ Python version compatibility (3.8+)

### Package Structure  
- ✅ Proper Python package in `python/markdown_it_accel/`
- ✅ `__init__.py` with version and exports
- ✅ Type hints file (`_rust.pyi`)
- ✅ `MANIFEST.in` for source distribution
- ✅ `LICENSE` and `README.md` files

### Build System
- ✅ Maturin build backend configured
- ✅ PyO3 bindings with abi3 support (single wheel for all Python 3.8+)
- ✅ Rust source code in `src/`
- ✅ Cargo.toml with proper dependencies

### CI/CD Pipeline
- ✅ Automated wheel building for multiple platforms:
  - Linux x86_64 (manylinux)
  - Windows x64
  - macOS x86_64 (Intel)
  - macOS aarch64 (Apple Silicon)
- ✅ Source distribution (sdist) building
- ✅ Automated PyPI publishing on GitHub releases
- ✅ Tests pass on multiple Python versions

## Publishing Process

### Automatic Publishing (Recommended)
1. Create a new release on GitHub with a version tag (e.g., `v0.1.0`)
2. GitHub Actions will automatically:
   - Build wheels for all platforms
   - Build source distribution
   - Publish to PyPI using trusted publishing

### Manual Publishing (Fallback)
```bash
# Build wheels locally
maturin build --release

# Build source distribution
maturin sdist

# Upload to PyPI (requires API token)
twine upload target/wheels/*
```

## PyPI Environment Setup

The GitHub Actions workflow uses OpenID Connect (OIDC) trusted publishing, which requires:
1. Creating a PyPI project named `markdown-it-accel`
2. Configuring trusted publishing for the GitHub repository
3. Setting up the `pypi` environment in GitHub

## Post-Publishing Verification

After publishing, verify:
1. Package appears on PyPI: https://pypi.org/project/markdown-it-accel/
2. Installation works: `pip install markdown-it-accel`
3. Basic functionality: `python -c "from markdown_it_accel import is_available; print(is_available())"`
4. Performance benchmarks show expected improvements

## Version Management

- Current version: `0.1.0`
- Update version in `pyproject.toml` and create corresponding Git tags
- Follow semantic versioning (SemVer)
- Consider pre-release versions for testing (`0.1.0rc1`)