#!/usr/bin/env python3
"""
Generate additional test data for markdown-it-accel benchmarks.

This script consolidates the test data generation functionality and provides
options for creating different types of test documents.
"""

import argparse
from pathlib import Path


def generate_basic_content(sections: int = 10) -> str:
    """Generate basic markdown content with mixed elements."""

    content = [
        "# Test Document",
        "",
        "This is an automatically generated test document for performance testing.",
        "",
    ]

    for i in range(1, sections + 1):
        section = f"""## Section {i}

This is section {i} with various markdown elements.

### Text Formatting

This paragraph contains **bold text**, *italic text*, ***bold and italic***, and `inline code`.

Regular paragraph with some longer text to increase document size. Lorem ipsum dolor sit amet,
consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

### Lists

#### Unordered List

- Item 1 in section {i}
- Item 2 with [a link](https://example.com/section{i})
- Item 3 with **bold text**
  - Nested item A
  - Nested item B

#### Ordered List

1. First item
2. Second item with *emphasis*
3. Third item

### Code Block

```python
def section_{i}_function():
    '''Example function for section {i}'''
    result = {i} * 2
    return f"Section {{i}} result: {{result}}"

print(section_{i}_function())
```

### Blockquote

> This is a blockquote in section {i}.
>
> It can contain **bold** and *italic* text.

"""
        content.append(section)

    content.append(
        """## Conclusion

This document tests various markdown features for performance benchmarking.
"""
    )

    return "\n".join(content)


def generate_table_heavy_content(
    table_count: int = 20, rows_per_table: int = 10
) -> str:
    """Generate content with many tables."""

    content = [
        "# Table-Heavy Test Document",
        "",
        f"This document contains {table_count} tables with {rows_per_table} rows each.",
        "",
    ]

    for i in range(1, table_count + 1):
        table_section = f"""## Table {i}

### Data Table {i}

| ID | Name | Category | Value | Status | Score | Location |
|----|------|----------|-------|--------|-------|----------|
"""

        # Generate table rows
        for j in range(1, rows_per_table + 1):
            row = f"| {j:03d} | Item-{i}-{j} | Cat-{(j%5)+1} | {j*10+i} | {'Active' if j%2 else 'Inactive'} | {(j*3+i)%100} | Zone-{(j%3)+1} |"
            table_section += row + "\n"

        table_section += f"""
Description for table {i}: This table contains sample data for testing
table rendering performance with {rows_per_table} rows.

"""
        content.append(table_section)

    return "\n".join(content)


def generate_code_heavy_content(code_blocks: int = 30) -> str:
    """Generate content with many code blocks."""

    languages = ["python", "javascript", "rust", "go", "java", "cpp", "typescript"]

    content = [
        "# Code-Heavy Test Document",
        "",
        f"This document contains {code_blocks} code blocks in various languages.",
        "",
    ]

    for i in range(1, code_blocks + 1):
        lang = languages[(i - 1) % len(languages)]

        if lang == "python":
            code = f'''def process_data_{i}(data):
    """Process data for example {i}."""
    result = []
    for item in data:
        if item.value > {i}:
            processed = item.value * {i}
            result.append(processed)
    return result

# Example {i} usage
data = [DataPoint(value=x*{i}) for x in range(10)]
processed = process_data_{i}(data)
print(f"Processed {{len(processed)}} items")'''

        elif lang == "javascript":
            code = f"""class DataProcessor{i} {{
    constructor() {{
        this.id = {i};
        this.data = [];
    }}

    process(items) {{
        return items
            .filter(item => item.value > {i})
            .map(item => ({{
                ...item,
                processed: item.value * this.id
            }}));
    }}
}}

// Example {i}
const processor = new DataProcessor{i}();
const result = processor.process(sampleData);
console.log(`Processed ${{result.length}} items`);"""

        elif lang == "rust":
            code = f"""use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct DataItem {{
    id: u64,
    value: i32,
    category: String,
}}

impl DataItem {{
    pub fn process_{i}(&self) -> i32 {{
        self.value * {i}
    }}
}}

fn main() {{
    let items = vec![
        DataItem {{ id: 1, value: {i}, category: "test".to_string() }},
        DataItem {{ id: 2, value: {i*2}, category: "data".to_string() }},
    ];

    let processed: Vec<_> = items.iter()
        .map(|item| item.process_{i}())
        .collect();

    println!("Processed {{}} items", processed.len());
}}"""

        else:
            code = f"""// Example {i} in {lang}
function example{i}() {{
    const data = generateData({i});
    const result = processData(data);
    return result.filter(item => item.value > {i});
}}

const output{i} = example{i}();
console.log("Result:", output{i});"""

        section = f"""## Code Example {i}

Example {i} demonstrates {lang} code processing:

```{lang}
{code}
```

This example shows typical {lang} patterns for data processing and filtering.

"""
        content.append(section)

    return "\n".join(content)


def generate_mixed_content(size_kb: int = 100) -> str:
    """Generate mixed content targeting a specific size."""

    # Estimate content needed (rough approximation)
    target_chars = size_kb * 1024
    sections_needed = max(1, target_chars // 2000)  # ~2KB per section

    content = [
        f"# Mixed Content Document ({size_kb}KB target)",
        "",
        "This document contains mixed markdown elements targeting a specific size.",
        "",
    ]

    for i in range(1, sections_needed + 1):
        section_type = i % 4

        if section_type == 0:
            # Text-heavy section
            section = f"""## Text Section {i}

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.

**Bold text** and *italic text* are mixed throughout this section along with
`inline code` and [links](https://example.com/section{i}).

"""

        elif section_type == 1:
            # List section
            items = [f"List item {j} in section {i}" for j in range(1, 8)]
            section = (
                f"""## List Section {i}

### Unordered List

"""
                + "\n".join(f"- {item}" for item in items)
                + """

### Ordered List

"""
                + "\n".join(f"{j}. {item}" for j, item in enumerate(items, 1))
                + "\n\n"
            )

        elif section_type == 2:
            # Code section
            section = f"""## Code Section {i}

```python
class DataProcessor{i}:
    def __init__(self, section_id={i}):
        self.section_id = section_id
        self.data = []

    def add_item(self, value):
        self.data.append({{
            'id': len(self.data),
            'value': value * self.section_id,
            'section': self.section_id
        }})

    def process_all(self):
        return [item['value'] * 2 for item in self.data]

# Usage
processor = DataProcessor{i}()
for i in range(5):
    processor.add_item(i + {i})
results = processor.process_all()
print(f"Section {i} results: {{results}}")
```

"""

        else:
            # Table section
            section = (
                f"""## Table Section {i}

| Column A | Column B | Column C | Value | Status |
|----------|----------|----------|-------|--------|
"""
                + "\n".join(
                    f"| Row {i}-{j} | Data {j} | Info {j} | {j*i} | {'Active' if j%2 else 'Inactive'} |"
                    for j in range(1, 6)
                )
                + "\n\n"
            )

        content.append(section)

    result = "\n".join(content)

    # Add more content if we're under target
    actual_size = len(result)
    if actual_size < target_chars * 0.8:  # If significantly under target
        padding_needed = target_chars - actual_size
        padding_sections = padding_needed // 500  # ~500 chars per padding

        for i in range(padding_sections):
            content.append(
                f"""## Padding Section {i+1}

This is additional content to reach the target document size. It contains
standard markdown elements including **bold**, *italic*, and `code` text.

> This blockquote adds more content while testing blockquote rendering performance.

"""
            )

    return "\n".join(content)


def main():
    """Main generation function."""

    parser = argparse.ArgumentParser(description="Generate markdown test data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data",
        help="Output directory for generated files",
    )

    subparsers = parser.add_subparsers(dest="command", help="Generation commands")

    # Basic content generator
    basic_parser = subparsers.add_parser("basic", help="Generate basic mixed content")
    basic_parser.add_argument(
        "--sections", type=int, default=50, help="Number of sections to generate"
    )
    basic_parser.add_argument(
        "--output", default="GENERATED_BASIC.md", help="Output filename"
    )

    # Table-heavy generator
    table_parser = subparsers.add_parser("tables", help="Generate table-heavy content")
    table_parser.add_argument(
        "--count", type=int, default=25, help="Number of tables to generate"
    )
    table_parser.add_argument("--rows", type=int, default=15, help="Rows per table")
    table_parser.add_argument(
        "--output", default="GENERATED_TABLES.md", help="Output filename"
    )

    # Code-heavy generator
    code_parser = subparsers.add_parser("code", help="Generate code-heavy content")
    code_parser.add_argument(
        "--blocks", type=int, default=40, help="Number of code blocks to generate"
    )
    code_parser.add_argument(
        "--output", default="GENERATED_CODE.md", help="Output filename"
    )

    # Size-targeted generator
    size_parser = subparsers.add_parser(
        "size", help="Generate content targeting specific size"
    )
    size_parser.add_argument("--kb", type=int, default=200, help="Target size in KB")
    size_parser.add_argument(
        "--output", default="GENERATED_MIXED.md", help="Output filename"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Create output directory
    args.output_dir.mkdir(exist_ok=True)

    print(f"Generating {args.command} content...")

    # Generate content based on command
    if args.command == "basic":
        content = generate_basic_content(args.sections)
        output_file = args.output_dir / args.output

    elif args.command == "tables":
        content = generate_table_heavy_content(args.count, args.rows)
        output_file = args.output_dir / args.output

    elif args.command == "code":
        content = generate_code_heavy_content(args.blocks)
        output_file = args.output_dir / args.output

    elif args.command == "size":
        content = generate_mixed_content(args.kb)
        output_file = args.output_dir / args.output

    # Write file
    output_file.write_text(content, encoding="utf-8")

    # Report results
    file_size = len(content)
    line_count = len(content.splitlines())

    print(f"Generated: {output_file}")
    print(f"Size: {file_size:,} characters ({file_size/1024:.1f}KB)")
    print(f"Lines: {line_count:,}")

    return 0


if __name__ == "__main__":
    exit(main())
