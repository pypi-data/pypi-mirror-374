#!/usr/bin/env python3
"""Performance profiling utilities for markdown-it-accel benchmarks."""

import gc
import statistics
import time
from typing import Any, Callable, Dict

import psutil


class PerformanceProfiler:
    """Profile memory and CPU usage during benchmark runs."""

    def __init__(self):
        self.process = psutil.Process()

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def get_cpu_percent(self) -> float:
        """Get current CPU usage percent."""
        return self.process.cpu_percent(interval=None)


def benchmark_function(
    func: Callable, *args, iterations: int = 10, warmup: int = 2
) -> Dict[str, Any]:
    """
    Benchmark a function with comprehensive profiling.

    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        iterations: Number of benchmark iterations
        warmup: Number of warmup iterations

    Returns:
        Dictionary with timing stats, memory usage, and other metrics
    """
    profiler = PerformanceProfiler()

    # Warm up runs
    for _ in range(warmup):
        gc.collect()
        func(*args)

    # Collect baseline memory
    gc.collect()
    baseline_memory = profiler.get_memory_usage()

    # Benchmark runs
    times = []
    peak_memory = baseline_memory
    total_cpu_time = 0

    for _ in range(iterations):
        # Force garbage collection
        gc.collect()

        profiler.get_memory_usage()
        start_time = time.perf_counter()
        start_cpu_time = time.process_time()

        # Execute function
        result = func(*args)

        # Measure completion
        end_time = time.perf_counter()
        end_cpu_time = time.process_time()
        end_memory = profiler.get_memory_usage()

        # Calculate metrics
        elapsed = end_time - start_time
        cpu_time = end_cpu_time - start_cpu_time
        # memory_used = end_memory - start_memory  # Not currently used

        times.append(elapsed)
        total_cpu_time += cpu_time
        peak_memory = max(peak_memory, end_memory)

        # Validate result
        if not isinstance(result, str) or len(result) == 0:
            raise ValueError(f"Invalid result from function: {type(result)}")

    return {
        "mean_time": statistics.mean(times),
        "median_time": statistics.median(times),
        "std_time": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min_time": min(times),
        "max_time": max(times),
        "all_times": times,
        "total_cpu_time": total_cpu_time,
        "peak_memory_mb": peak_memory,
        "memory_increase_mb": peak_memory - baseline_memory,
        "baseline_memory_mb": baseline_memory,
        "iterations": iterations,
    }


def calculate_throughput(content_size: int, time_seconds: float) -> float:
    """Calculate throughput in characters per second."""
    return content_size / time_seconds if time_seconds > 0 else 0


def calculate_speedup(baseline_time: float, optimized_time: float) -> float:
    """Calculate speedup ratio."""
    return baseline_time / optimized_time if optimized_time > 0 else 0


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.3f}s"


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def format_throughput(chars_per_sec: float) -> str:
    """Format throughput in human-readable format."""
    if chars_per_sec > 1_000_000:
        return f"{chars_per_sec / 1_000_000:.1f}M chars/sec"
    elif chars_per_sec > 1_000:
        return f"{chars_per_sec / 1_000:.1f}K chars/sec"
    else:
        return f"{chars_per_sec:.0f} chars/sec"


class BenchmarkSuite:
    """Manage a suite of benchmark tests."""

    def __init__(self, name: str = "Benchmark Suite"):
        self.name = name
        self.results = {}

    def add_test(self, test_name: str, result: Dict[str, Any]):
        """Add a test result to the suite."""
        self.results[test_name] = result

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics across all tests."""
        if not self.results:
            return {}

        all_times = []
        all_speedups = []
        total_memory = 0

        for result in self.results.values():
            all_times.append(result.get("mean_time", 0))
            if "speedup" in result:
                all_speedups.append(result["speedup"])
            total_memory += result.get("peak_memory_mb", 0)

        summary = {
            "total_tests": len(self.results),
            "total_time": sum(all_times),
            "average_time": statistics.mean(all_times) if all_times else 0,
            "total_memory_mb": total_memory,
            "average_memory_mb": (
                total_memory / len(self.results) if self.results else 0
            ),
        }

        if all_speedups:
            summary.update(
                {
                    "average_speedup": statistics.mean(all_speedups),
                    "best_speedup": max(all_speedups),
                    "worst_speedup": min(all_speedups),
                }
            )

        return summary

    def print_summary(self):
        """Print a formatted summary of all test results."""
        summary = self.get_summary()

        print(f"\n{self.name} Summary")
        print("=" * 60)
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Total Time: {format_time(summary.get('total_time', 0))}")
        print(f"Average Time: {format_time(summary.get('average_time', 0))}")
        print(f"Total Memory: {summary.get('total_memory_mb', 0):.1f}MB")
        print(f"Average Memory: {summary.get('average_memory_mb', 0):.1f}MB")

        if "average_speedup" in summary:
            print(f"Average Speedup: {summary['average_speedup']:.2f}x")
            print(f"Best Speedup: {summary['best_speedup']:.2f}x")
            print(f"Worst Speedup: {summary['worst_speedup']:.2f}x")
