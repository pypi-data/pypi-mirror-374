# Benchmark Suite for markdown-it-accel

This directory contains a comprehensive benchmark suite for testing the performance of `markdown-it-accel` against pure Python `markdown-it-py`.

## Directory Structure

```
bench/
├── README.md                 # This file
├── data/                    # Test markdown files
│   ├── BIG.md              # Medium-sized test document (8KB)
│   ├── HUGE.md             # Large test document (445KB) 
│   ├── CODE_HEAVY.md       # Code-block heavy document
│   └── TABLE_HEAVY.md      # Table-heavy document
├── scripts/                # Benchmark and utility scripts
│   ├── benchmark.py        # Main consolidated benchmark script
│   ├── compare_libraries.py # Compare against other markdown libraries
│   └── generate_test_data.py # Generate additional test data
├── results/                # Benchmark results and outputs
│   ├── benchmark_results.json
│   ├── python_output.html
│   └── rust_output.html
└── utils/                  # Utility modules
    └── profiler.py         # Performance profiling utilities
```

## Usage

### Quick Benchmark

Run the main benchmark script:

```bash
cd bench
python scripts/benchmark.py
```

This will:
- Test all markdown files in `data/`
- Compare Python vs Rust performance
- Generate detailed performance reports
- Save results to `results/`

### Available Scripts

#### `benchmark.py` - Main Benchmark Suite
- Comprehensive performance testing
- Memory usage profiling
- Scaling analysis
- Detailed reporting

#### `compare_libraries.py` - Library Comparison
- Compare against other Python markdown libraries
- Includes `markdown`, `mistune`, etc. (if available)
- Side-by-side performance comparison

#### `generate_test_data.py` - Test Data Generator
- Generate additional test files
- Create documents with specific characteristics
- Scaling test data generation

### Benchmark Types

1. **Basic Performance**: Simple time comparison
2. **Memory Profiling**: Memory usage analysis
3. **Scaling Tests**: Performance vs document size
4. **Content-Type Tests**: Performance by content characteristics
5. **Throughput Tests**: Characters/second processing rates

### Test Data

The `data/` directory contains various test files:

- **BIG.md**: General-purpose medium-sized document with mixed content
- **HUGE.md**: Large document with 15K lines for stress testing
- **CODE_HEAVY.md**: Document with many code blocks
- **TABLE_HEAVY.md**: Document with complex table structures

### Interpreting Results

#### Performance Metrics
- **Mean Time**: Average processing time
- **Speedup**: Rust time / Python time ratio
- **Throughput**: Characters processed per second
- **Memory Usage**: Peak memory consumption

#### Typical Results
- **Small docs** (< 1KB): 5-8x speedup
- **Medium docs** (1-50KB): 8-12x speedup  
- **Large docs** (> 100KB): 5-6x speedup

### Adding New Tests

1. **New Test Data**: Add `.md` files to `data/`
2. **Custom Benchmarks**: Extend `benchmark.py` 
3. **New Metrics**: Add to `utils/profiler.py`

### Environment Variables

- `MARKDOWN_IT_ACCEL=0`: Disable Rust acceleration
- `BENCHMARK_ITERATIONS=N`: Set number of test iterations
- `BENCHMARK_WARMUP=N`: Set warmup iterations

## Dependencies

Required packages:
- `markdown-it-py`
- `markdown-it-accel` 
- `psutil` (for memory profiling)

Optional packages for comparison:
- `markdown`
- `mistune`
- `commonmark`

## Output Files

Results are saved to `results/`:
- `benchmark_results.json`: Detailed performance data
- `python_output.html`: Python renderer output sample
- `rust_output.html`: Rust renderer output sample
- `performance_report.txt`: Human-readable summary