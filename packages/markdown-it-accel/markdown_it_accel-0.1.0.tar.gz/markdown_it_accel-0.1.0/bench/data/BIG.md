# Large Markdown Document for Performance Testing

This document contains various markdown features to test the performance of the markdown-it-accel library.

## Introduction

Markdown is a lightweight markup language with plain-text formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.

### Features Tested

This document tests the following features:

1. **Headers** - Multiple levels of headers
2. **Emphasis** - *Italic* and **bold** text
3. **Lists** - Both ordered and unordered lists
4. **Links** - [Internal links](http://example.com) and external references
5. **Code blocks** - Both inline `code` and fenced code blocks
6. **Tables** - Data representation in tabular format
7. **Blockquotes** - For highlighting quoted content

## Performance Test Content

### Section 1: Headers and Paragraphs

# Header Level 1
## Header Level 2  
### Header Level 3
#### Header Level 4
##### Header Level 5
###### Header Level 6

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Section 2: Text Formatting

This paragraph contains **bold text**, *italic text*, and ***bold italic text***. We also have ~~strikethrough text~~ and `inline code`.

Here's some more text with various formatting: **Lorem** *ipsum* `dolor` sit amet, **consectetur** *adipiscing* elit. ~~Sed~~ do `eiusmod` tempor **incididunt** ut *labore* et dolore magna aliqua.

### Section 3: Lists

#### Unordered Lists

- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
    - Deeply nested item 2.2.1
    - Deeply nested item 2.2.2
- Item 3
- Item 4 with a very long description that spans multiple lines and contains various formatting like **bold** and *italic* text

#### Ordered Lists

1. First item
2. Second item
   1. Nested numbered item 2.1
   2. Nested numbered item 2.2
      1. Deeply nested item 2.2.1
      2. Deeply nested item 2.2.2
3. Third item
4. Fourth item with inline `code` and **bold** text

### Section 4: Links and Images

Here are some links: [Google](https://google.com), [GitHub](https://github.com), [Stack Overflow](https://stackoverflow.com).

Reference style links: [Link 1][1], [Link 2][2], [Link 3][3].

[1]: https://example1.com "Example 1"
[2]: https://example2.com "Example 2"  
[3]: https://example3.com "Example 3"

Images: ![Alt text](https://via.placeholder.com/150), ![Another image](https://via.placeholder.com/300x200).

### Section 5: Code Blocks

Here's an inline code example: `print("Hello, World!")`.

```python
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Generate Fibonacci sequence
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

```javascript
function quickSort(arr) {
    if (arr.length <= 1) {
        return arr;
    }
    
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = [];
    const right = [];
    
    for (let i = 0; i < arr.length; i++) {
        if (i === Math.floor(arr.length / 2)) continue;
        if (arr[i] < pivot) {
            left.push(arr[i]);
        } else {
            right.push(arr[i]);
        }
    }
    
    return [...quickSort(left), pivot, ...quickSort(right)];
}
```

```rust
fn main() {
    let numbers = vec![64, 34, 25, 12, 22, 11, 90];
    println!("Original: {:?}", numbers);
    
    let mut sorted = numbers.clone();
    bubble_sort(&mut sorted);
    println!("Sorted: {:?}", sorted);
}

fn bubble_sort(arr: &mut Vec<i32>) {
    let n = arr.len();
    for i in 0..n {
        for j in 0..n - 1 - i {
            if arr[j] > arr[j + 1] {
                arr.swap(j, j + 1);
            }
        }
    }
}
```

### Section 6: Tables

| Language | Performance | Memory Usage | Learning Curve |
|----------|-------------|--------------|----------------|
| Rust     | Excellent   | Low          | Steep          |
| Python   | Good        | Medium       | Easy           |
| JavaScript | Good      | Medium       | Easy           |
| C++      | Excellent   | Low          | Very Steep     |
| Go       | Very Good   | Low          | Moderate       |

| Feature | Rust | Python | JavaScript | C++ |
|---------|------|--------|------------|-----|
| Memory Safety | ✓ | ✓ | ✓ | ✗ |
| Performance | ✓✓✓ | ✓ | ✓✓ | ✓✓✓ |
| Ecosystem | ✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| Learning Curve | ✗ | ✓✓✓ | ✓✓ | ✗ |

### Section 7: Blockquotes

> This is a blockquote. It can contain multiple lines and various formatting.
> 
> > This is a nested blockquote.
> > It demonstrates how blockquotes can be nested within each other.
> 
> Back to the first level blockquote with **bold** text and *italic* text.

> **Albert Einstein** said:
> 
> "Two things are infinite: the universe and human stupidity; and I'm not sure about the universe."

> Here's a blockquote with a list:
> 
> 1. First item in blockquote
> 2. Second item in blockquote
>    - Nested unordered item
>    - Another nested item
> 3. Third item in blockquote

### Section 8: Mixed Content

Here's a paragraph that combines multiple features: [This link](https://example.com) leads to a page about **performance optimization** in *various programming languages*. The page contains `code examples` and ~~outdated information~~ that has been updated.

```python
# Here's a code block within mixed content
def process_markdown(content):
    """Process markdown content with various features."""
    # Handle headers
    content = process_headers(content)
    
    # Handle emphasis
    content = process_emphasis(content)
    
    # Handle links
    content = process_links(content)
    
    return content
```

More content with [another link](https://github.com) and some **bold text** followed by a table:

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Insert    | O(1)           | O(1)             |
| Delete    | O(1)           | O(1)             |
| Search    | O(n)           | O(1)             |
| Sort      | O(n log n)     | O(log n)         |

## Stress Test Section

This section contains repetitive content to stress test the parser:

### Repeated Headers

# Main Title 1
## Subtitle 1.1
### Sub-subtitle 1.1.1
# Main Title 2
## Subtitle 2.1
### Sub-subtitle 2.1.1
# Main Title 3
## Subtitle 3.1
### Sub-subtitle 3.1.1

### Repeated Lists

- Alpha
  - Alpha.1
    - Alpha.1.a
    - Alpha.1.b
  - Alpha.2
- Beta
  - Beta.1
  - Beta.2
    - Beta.2.a
    - Beta.2.b
- Gamma
  - Gamma.1
  - Gamma.2
  - Gamma.3

1. First
   1. First.1
      1. First.1.a
      2. First.1.b
   2. First.2
2. Second
   1. Second.1
   2. Second.2
      1. Second.2.a
      2. Second.2.b
3. Third

### Repeated Code Blocks

```python
print("Hello, World! - Block 1")
```

```python  
print("Hello, World! - Block 2")
```

```python
print("Hello, World! - Block 3")
```

### Many Links

[Link 1](http://1.example.com) | [Link 2](http://2.example.com) | [Link 3](http://3.example.com) | [Link 4](http://4.example.com) | [Link 5](http://5.example.com)

[Link 6](http://6.example.com) | [Link 7](http://7.example.com) | [Link 8](http://8.example.com) | [Link 9](http://9.example.com) | [Link 10](http://10.example.com)

## Conclusion

This large document tests various aspects of markdown parsing including headers, emphasis, lists, links, code blocks, tables, and blockquotes. It should provide a good benchmark for comparing the performance of different markdown parsers, especially when testing the Rust-accelerated version against the pure Python implementation.

The document contains approximately 1000+ lines of varied markdown content to ensure a comprehensive performance test.

---

*End of performance test document*