.PHONY: dev install test bench clean format lint build release

# Development
dev:
	maturin develop

dev-release:
	maturin develop --release

install:
	pip install -e .[dev]

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=markdown_it_accel --cov-report=html

bench:
	python bench/bench_render.py

compare:
	python bench/compare.py

# Code quality
format:
	black .
	cargo fmt

lint:
	ruff check .
	black --check .
	cargo clippy -- -D warnings

# Building
build:
	maturin build --release

build-all:
	maturin build --release --target x86_64-pc-windows-msvc
	maturin build --release --target x86_64-unknown-linux-gnu
	maturin build --release --target x86_64-apple-darwin
	maturin build --release --target aarch64-apple-darwin

# Release
release-test:
	maturin publish --repository testpypi

release:
	maturin publish

# Cleanup
clean:
	rm -rf target/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Setup
setup-rust:
	rustup toolchain install stable
	rustup default stable
	rustup component add rustfmt clippy

setup-python:
	pip install --upgrade pip
	pip install maturin pytest markdown-it-py ruff black mypy

setup: setup-rust setup-python

# Help
help:
	@echo "Available targets:"
	@echo "  dev          - Build in development mode"
	@echo "  dev-release  - Build in release mode for development"
	@echo "  install      - Install package in development mode"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  bench        - Run benchmark"
	@echo "  compare      - Compare with other libraries"
	@echo "  format       - Format code"
	@echo "  lint         - Lint code"
	@echo "  build        - Build release wheels"
	@echo "  build-all    - Build wheels for all platforms"
	@echo "  release-test - Release to TestPyPI"
	@echo "  release      - Release to PyPI"
	@echo "  clean        - Clean build artifacts"
	@echo "  setup        - Setup development environment"
	@echo "  help         - Show this help"