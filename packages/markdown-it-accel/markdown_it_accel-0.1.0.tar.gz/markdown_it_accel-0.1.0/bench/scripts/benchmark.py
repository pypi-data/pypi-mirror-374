#!/usr/bin/env python3
"""
Consolidated benchmark script for markdown-it-accel performance testing.

This script combines functionality from multiple benchmark scripts into a
single, comprehensive testing suite with proper organization.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_it import MarkdownIt
from markdown_it_accel import is_available, use_rust_core
from utils.profiler import (
    BenchmarkSuite,
    benchmark_function,
    calculate_speedup,
    calculate_throughput,
    format_size,
    format_throughput,
    format_time,
)


def load_test_files(data_dir: Path) -> Dict[str, str]:
    """Load all test markdown files from data directory."""
    test_files = {}

    for md_file in data_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            test_files[md_file.stem] = content
            print(
                f"Loaded {md_file.stem}: {format_size(len(content))}, {len(content.splitlines()):,} lines"
            )
        except Exception as e:
            print(f"Warning: Could not load {md_file}: {e}")

    if not test_files:
        raise FileNotFoundError(f"No markdown files found in {data_dir}")

    return test_files


def create_renderers() -> Tuple[MarkdownIt, MarkdownIt]:
    """Create Python and Rust-accelerated markdown renderers."""
    # Configure both renderers identically
    config = "commonmark"
    plugins = ["table", "strikethrough", "linkify"]

    md_python = MarkdownIt(config).enable(plugins)
    md_rust = MarkdownIt(config).enable(plugins)

    # Apply Rust acceleration to second renderer
    if is_available():
        use_rust_core(md_rust)
        print("* Rust acceleration enabled")
    else:
        print("* Rust acceleration not available")

    return md_python, md_rust


def run_basic_benchmark(
    test_files: Dict[str, str], iterations: int = 10
) -> Dict[str, Any]:
    """Run basic performance comparison between Python and Rust implementations."""

    print(f"\n{'='*80}")
    print("BASIC PERFORMANCE BENCHMARK")
    print(f"{'='*80}")

    md_python, md_rust = create_renderers()
    suite = BenchmarkSuite("Basic Performance")
    results = {"rust_available": is_available(), "test_files": {}, "summary": {}}

    total_python_time = 0
    total_rust_time = 0

    for file_name, content in test_files.items():
        print(f"\nBenchmarking {file_name}:")
        print(
            f"Content: {format_size(len(content))}, {len(content.splitlines()):,} lines"
        )
        print("-" * 60)

        # Benchmark Python implementation
        python_stats = benchmark_function(
            md_python.render, content, iterations=iterations, warmup=2
        )

        python_time = python_stats["mean_time"]
        python_throughput = calculate_throughput(len(content), python_time)
        total_python_time += python_time

        print(
            f"Python: {format_time(python_time)} ± {format_time(python_stats['std_time'])}"
        )
        print(f"        {format_throughput(python_throughput)}")
        print(f"        Memory: {python_stats['peak_memory_mb']:.1f}MB peak")

        # Benchmark Rust implementation (if available)
        rust_stats = None
        speedup = None

        if is_available():
            rust_stats = benchmark_function(
                md_rust.render, content, iterations=iterations, warmup=2
            )

            rust_time = rust_stats["mean_time"]
            rust_throughput = calculate_throughput(len(content), rust_time)
            speedup = calculate_speedup(python_time, rust_time)
            total_rust_time += rust_time

            print(
                f"Rust:   {format_time(rust_time)} ± {format_time(rust_stats['std_time'])}"
            )
            print(f"        {format_throughput(rust_throughput)}")
            print(f"        Memory: {rust_stats['peak_memory_mb']:.1f}MB peak")
            print(f"        Speedup: {speedup:.2f}x faster")

            # Add to suite for summary
            suite.add_test(
                file_name,
                {
                    "mean_time": rust_time,
                    "peak_memory_mb": rust_stats["peak_memory_mb"],
                    "speedup": speedup,
                },
            )

        # Store results
        file_results = {
            "content_chars": len(content),
            "content_lines": len(content.splitlines()),
            "python": {
                "mean_time": python_time,
                "std_time": python_stats["std_time"],
                "throughput": python_throughput,
                "memory_mb": python_stats["peak_memory_mb"],
            },
        }

        if rust_stats:
            file_results["rust"] = {
                "mean_time": rust_time,
                "std_time": rust_stats["std_time"],
                "throughput": rust_throughput,
                "memory_mb": rust_stats["peak_memory_mb"],
            }
            file_results["speedup"] = speedup

        results["test_files"][file_name] = file_results

    # Calculate overall summary
    if total_rust_time > 0:
        overall_speedup = total_python_time / total_rust_time
        results["summary"] = {
            "total_python_time": total_python_time,
            "total_rust_time": total_rust_time,
            "overall_speedup": overall_speedup,
        }

        # Print suite summary
        suite.print_summary()

    return results


def run_scaling_benchmark(iterations: int = 5) -> Dict[str, Any]:
    """Test performance scaling with different document sizes."""

    print(f"\n{'='*80}")
    print("SCALING BENCHMARK")
    print(f"{'='*80}")

    if not is_available():
        print("Rust acceleration not available - skipping scaling test")
        return {}

    md_python, md_rust = create_renderers()

    # Base content for scaling test
    base_content = """# Test Document

This is a test document with various **markdown** features.

## Section with Lists

- Item 1 with *italic text*
- Item 2 with `inline code`
- Item 3 with [a link](https://example.com)

## Code Block

```python
def test_function():
    return "Hello World"
```

## Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Value 1  | Result 1 |
| Data 2   | Value 2  | Result 2 |

> This is a blockquote with **bold** text.

"""

    multipliers = [1, 5, 10, 25, 50, 100]
    results = []

    print(
        f"{'Multiplier':<12} {'Size':<12} {'Python':<12} {'Rust':<12} {'Speedup':<10}"
    )
    print("-" * 70)

    for multiplier in multipliers:
        content = base_content * multiplier
        char_count = len(content)

        # Benchmark both implementations
        python_stats = benchmark_function(
            md_python.render, content, iterations=iterations, warmup=1
        )
        rust_stats = benchmark_function(
            md_rust.render, content, iterations=iterations, warmup=1
        )

        python_time = python_stats["mean_time"]
        rust_time = rust_stats["mean_time"]
        speedup = calculate_speedup(python_time, rust_time)

        results.append(
            {
                "multiplier": multiplier,
                "size_chars": char_count,
                "python_time": python_time,
                "rust_time": rust_time,
                "speedup": speedup,
            }
        )

        print(
            f"{multiplier:<12} {format_size(char_count):<12} {format_time(python_time):<12} {format_time(rust_time):<12} {speedup:<10.2f}"
        )

    return {"scaling_results": results}


def verify_output_equivalence(test_files: Dict[str, str]) -> Dict[str, Any]:
    """Verify that Python and Rust implementations produce equivalent output."""

    print(f"\n{'='*80}")
    print("OUTPUT EQUIVALENCE VERIFICATION")
    print(f"{'='*80}")

    if not is_available():
        print("Rust acceleration not available - skipping equivalence check")
        return {}

    md_python, md_rust = create_renderers()
    results = {}

    for file_name, content in test_files.items():
        python_output = md_python.render(content)
        rust_output = md_rust.render(content)

        # Compare outputs
        are_identical = python_output == rust_output
        length_diff = abs(len(python_output) - len(rust_output))

        results[file_name] = {
            "identical": are_identical,
            "python_length": len(python_output),
            "rust_length": len(rust_output),
            "length_difference": length_diff,
        }

        status = "IDENTICAL" if are_identical else f"DIFFER ({length_diff} chars)"
        print(f"{file_name:<20} {status}")

    return {"equivalence_results": results}


def save_results(results: Dict[str, Any], output_dir: Path):
    """Save benchmark results to files."""
    output_dir.mkdir(exist_ok=True)

    # Save JSON results
    json_file = output_dir / "benchmark_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    # Save human-readable report
    report_file = output_dir / "performance_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("markdown-it-accel Performance Benchmark Report\n")
        f.write("=" * 50 + "\n\n")

        if "basic_benchmark" in results:
            basic = results["basic_benchmark"]
            if "summary" in basic and basic["summary"]:
                f.write(
                    f"Overall Speedup: {basic['summary']['overall_speedup']:.2f}x\n"
                )
                f.write(
                    f"Total Python Time: {format_time(basic['summary']['total_python_time'])}\n"
                )
                f.write(
                    f"Total Rust Time: {format_time(basic['summary']['total_rust_time'])}\n\n"
                )

        # File-by-file breakdown
        if "basic_benchmark" in results and "test_files" in results["basic_benchmark"]:
            f.write("File Performance Breakdown:\n")
            f.write("-" * 30 + "\n")

            for file_name, file_data in results["basic_benchmark"][
                "test_files"
            ].items():
                f.write(f"\n{file_name}:\n")
                f.write(f"  Size: {format_size(file_data['content_chars'])}\n")
                f.write(f"  Python: {format_time(file_data['python']['mean_time'])}\n")

                if "rust" in file_data:
                    f.write(f"  Rust: {format_time(file_data['rust']['mean_time'])}\n")
                    f.write(f"  Speedup: {file_data['speedup']:.2f}x\n")

    print("\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Report: {report_file}")


def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="markdown-it-accel benchmark suite")
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=10,
        help="Number of benchmark iterations (default: 10)",
    )
    parser.add_argument(
        "--no-scaling", action="store_true", help="Skip scaling benchmark"
    )
    parser.add_argument(
        "--no-equivalence", action="store_true", help="Skip output equivalence check"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data",
        help="Directory containing test markdown files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "results",
        help="Directory for output files",
    )

    args = parser.parse_args()

    print("markdown-it-accel Comprehensive Benchmark Suite")
    print(f"{'='*80}")
    print(f"Rust Available: {is_available()}")
    print(f"Test Iterations: {args.iterations}")
    print(f"Data Directory: {args.data_dir}")
    print(f"Output Directory: {args.output_dir}")

    try:
        # Load test files
        print(f"\nLoading test files from {args.data_dir}...")
        test_files = load_test_files(args.data_dir)
        print(f"Loaded {len(test_files)} test files")

        # Collect all results
        all_results = {}

        # Run basic benchmark
        all_results["basic_benchmark"] = run_basic_benchmark(
            test_files, args.iterations
        )

        # Run scaling benchmark
        if not args.no_scaling and is_available():
            all_results["scaling_benchmark"] = run_scaling_benchmark()

        # Verify output equivalence
        if not args.no_equivalence and is_available():
            all_results["equivalence_check"] = verify_output_equivalence(test_files)

        # Save results
        save_results(all_results, args.output_dir)

        print(f"\n{'='*80}")
        print("BENCHMARK COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
