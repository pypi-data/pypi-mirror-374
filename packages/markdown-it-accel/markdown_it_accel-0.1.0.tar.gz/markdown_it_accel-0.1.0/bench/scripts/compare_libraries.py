#!/usr/bin/env python3
"""
Compare markdown-it-accel against other popular Python markdown libraries.

This script benchmarks multiple markdown processing libraries to provide
context for the performance improvements offered by the Rust acceleration.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_it import MarkdownIt
from markdown_it_accel import is_available, use_rust_core
from utils.profiler import (
    benchmark_function,
    calculate_throughput,
    format_throughput,
    format_time,
)

# Optional library imports
LIBRARIES = {}

try:
    import markdown

    LIBRARIES["python-markdown"] = markdown
except ImportError:
    pass

try:
    import mistune

    LIBRARIES["mistune"] = mistune
except ImportError:
    pass

try:
    import commonmark

    LIBRARIES["commonmark"] = commonmark
except ImportError:
    pass


def load_test_document() -> str:
    """Load a representative test document."""
    data_dir = Path(__file__).parent.parent / "data"
    test_file = data_dir / "BIG.md"

    if not test_file.exists():
        raise FileNotFoundError(f"Test file not found: {test_file}")

    return test_file.read_text(encoding="utf-8")


def benchmark_markdown_it_python(content: str, iterations: int = 10) -> Dict[str, Any]:
    """Benchmark pure Python markdown-it-py."""
    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])

    stats = benchmark_function(md.render, content, iterations=iterations)

    return {
        "library": "markdown-it-py (Python)",
        "mean_time": stats["mean_time"],
        "std_time": stats["std_time"],
        "throughput": calculate_throughput(len(content), stats["mean_time"]),
        "memory_mb": stats["peak_memory_mb"],
    }


def benchmark_markdown_it_rust(
    content: str, iterations: int = 10
) -> Optional[Dict[str, Any]]:
    """Benchmark Rust-accelerated markdown-it-py."""
    if not is_available():
        return None

    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    use_rust_core(md)

    stats = benchmark_function(md.render, content, iterations=iterations)

    return {
        "library": "markdown-it-accel (Rust)",
        "mean_time": stats["mean_time"],
        "std_time": stats["std_time"],
        "throughput": calculate_throughput(len(content), stats["mean_time"]),
        "memory_mb": stats["peak_memory_mb"],
    }


def benchmark_python_markdown(
    content: str, iterations: int = 10
) -> Optional[Dict[str, Any]]:
    """Benchmark python-markdown library."""
    if "python-markdown" not in LIBRARIES:
        return None

    md = LIBRARIES["python-markdown"].Markdown(extensions=["tables", "codehilite"])

    def render_content(text):
        # Reset the markdown instance for each run
        md.reset()
        return md.convert(text)

    stats = benchmark_function(render_content, content, iterations=iterations)

    return {
        "library": "python-markdown",
        "mean_time": stats["mean_time"],
        "std_time": stats["std_time"],
        "throughput": calculate_throughput(len(content), stats["mean_time"]),
        "memory_mb": stats["peak_memory_mb"],
    }


def benchmark_mistune(content: str, iterations: int = 10) -> Optional[Dict[str, Any]]:
    """Benchmark mistune library."""
    if "mistune" not in LIBRARIES:
        return None

    # Use mistune v2 API if available, fallback to v1
    try:
        md = LIBRARIES["mistune"].create_markdown(
            plugins=["table", "strikethrough", "footnotes"]
        )
        render_func = md
    except AttributeError:
        # Fallback to mistune v1
        md = LIBRARIES["mistune"].Markdown()
        render_func = md

    stats = benchmark_function(render_func, content, iterations=iterations)

    return {
        "library": "mistune",
        "mean_time": stats["mean_time"],
        "std_time": stats["std_time"],
        "throughput": calculate_throughput(len(content), stats["mean_time"]),
        "memory_mb": stats["peak_memory_mb"],
    }


def benchmark_commonmark(
    content: str, iterations: int = 10
) -> Optional[Dict[str, Any]]:
    """Benchmark commonmark library."""
    if "commonmark" not in LIBRARIES:
        return None

    def render_content(text):
        ast = LIBRARIES["commonmark"].commonmark(text)
        return LIBRARIES["commonmark"].dumpHTML(ast)

    stats = benchmark_function(render_content, content, iterations=iterations)

    return {
        "library": "commonmark",
        "mean_time": stats["mean_time"],
        "std_time": stats["std_time"],
        "throughput": calculate_throughput(len(content), stats["mean_time"]),
        "memory_mb": stats["peak_memory_mb"],
    }


def run_comparison_benchmark(
    content: str, iterations: int = 10
) -> List[Dict[str, Any]]:
    """Run benchmark comparison across all available libraries."""

    benchmarks = [
        ("markdown-it-py (Python)", benchmark_markdown_it_python),
        ("markdown-it-accel (Rust)", benchmark_markdown_it_rust),
        ("python-markdown", benchmark_python_markdown),
        ("mistune", benchmark_mistune),
        ("commonmark", benchmark_commonmark),
    ]

    results = []

    for name, benchmark_func in benchmarks:
        print(f"Benchmarking {name}...")

        try:
            result = benchmark_func(content, iterations)
            if result:
                results.append(result)
                print(
                    f"  {format_time(result['mean_time'])} ± {format_time(result['std_time'])}"
                )
                print(f"  {format_throughput(result['throughput'])}")
            else:
                print("  Skipped (library not available)")
        except Exception as e:
            print(f"  Error: {e}")

    return results


def print_comparison_table(results: List[Dict[str, Any]]):
    """Print formatted comparison table."""

    print(f"\n{'='*80}")
    print("LIBRARY COMPARISON RESULTS")
    print(f"{'='*80}")

    if not results:
        print("No results to display")
        return

    # Sort by mean time (fastest first)
    sorted_results = sorted(results, key=lambda x: x["mean_time"])
    fastest_time = sorted_results[0]["mean_time"]

    # Header
    print(
        f"{'Library':<25} {'Time':<12} {'Throughput':<15} {'Memory':<10} {'Relative':<10}"
    )
    print("-" * 80)

    # Results
    for result in sorted_results:
        relative_speed = result["mean_time"] / fastest_time
        status = "FASTEST" if relative_speed == 1.0 else f"{relative_speed:.2f}x slower"

        print(
            f"{result['library']:<25} "
            f"{format_time(result['mean_time']):<12} "
            f"{format_throughput(result['throughput']):<15} "
            f"{result['memory_mb']:.1f}MB{'':<5} "
            f"{status:<10}"
        )

    print("-" * 80)

    # Performance summary
    if len(sorted_results) > 1:
        rust_result = next((r for r in sorted_results if "Rust" in r["library"]), None)
        python_result = next(
            (r for r in sorted_results if "Python" in r["library"]), None
        )

        if rust_result and python_result:
            speedup = python_result["mean_time"] / rust_result["mean_time"]
            print(f"\nRust Acceleration Speedup: {speedup:.2f}x faster than Python")

        fastest = sorted_results[0]
        slowest = sorted_results[-1]
        overall_range = slowest["mean_time"] / fastest["mean_time"]
        print(
            f"Performance Range: {overall_range:.2f}x difference between fastest and slowest"
        )


def main():
    """Main comparison execution."""

    print("markdown-it-accel Library Comparison Benchmark")
    print(f"{'='*80}")

    # Check available libraries
    print("Available Libraries:")
    base_libraries = ["markdown-it-py"]
    if is_available():
        base_libraries.append("markdown-it-accel")

    all_libs = base_libraries + list(LIBRARIES.keys())
    for lib in all_libs:
        print(f"  * {lib}")

    if not LIBRARIES:
        print("\nNote: Install additional libraries for broader comparison:")
        print("  pip install markdown mistune commonmark")

    try:
        # Load test content
        print("\nLoading test document...")
        content = load_test_document()
        print(
            f"Document: {len(content):,} characters, {len(content.splitlines()):,} lines"
        )

        # Run benchmarks
        print("\nRunning benchmarks (10 iterations each)...")
        print("-" * 50)

        results = run_comparison_benchmark(content, iterations=10)

        # Display results
        print_comparison_table(results)

        # Save results
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)

        import json

        output_file = results_dir / "library_comparison.json"
        with open(output_file, "w") as f:
            json.dump(
                {"content_size": len(content), "iterations": 10, "results": results},
                f,
                indent=2,
                default=str,
            )

        print(f"\nResults saved to: {output_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
