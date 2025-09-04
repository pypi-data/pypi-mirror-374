# Code-Heavy Markdown Document

This document contains many code blocks to test code rendering performance.

## Introduction

Code blocks can be expensive to process, especially with syntax highlighting attributes.

""" + "\n\n".join([f"""## Code Example Set {i}

### Python Examples

```python
# Example {i}: Data processing pipeline
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class DataProcessor:
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = None
    
    def load_data(self) -> pd.DataFrame:
        \"\"\"Load data from source.\"\"\"
        try:
            if self.data_source.endswith('.csv'):
                return pd.read_csv(self.data_source)
            elif self.data_source.endswith('.json'):
                return pd.read_json(self.data_source)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error loading data: {{e}}")
            return pd.DataFrame()
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Clean and transform data.\"\"\"
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(df.mean() if df.dtypes.name in ['int64', 'float64'] else 'Unknown')
        
        # Feature engineering
        if 'date' in df.columns:
            df['year'] = pd.to_datetime(df['date']).dt.year
            df['month'] = pd.to_datetime(df['date']).dt.month
        
        return df

# Usage example {i}
processor = DataProcessor(f'data_{{i}}.csv')
raw_data = processor.load_data()
clean_data = processor.process_data(raw_data)
```

### JavaScript Examples

```javascript
// Example {i}: Async data fetching and processing
class APIClient {{
    constructor(baseUrl, apiKey) {{
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.cache = new Map();
    }}

    async fetchData(endpoint, params = {{}}) {{
        const cacheKey = `${{endpoint}}_${{JSON.stringify(params)}}`;
        
        if (this.cache.has(cacheKey)) {{
            console.log(`Cache hit for ${{cacheKey}}`);
            return this.cache.get(cacheKey);
        }}

        try {{
            const url = new URL(endpoint, this.baseUrl);
            Object.keys(params).forEach(key => 
                url.searchParams.append(key, params[key])
            );

            const response = await fetch(url, {{
                headers: {{
                    'Authorization': `Bearer ${{this.apiKey}}`,
                    'Content-Type': 'application/json'
                }}
            }});

            if (!response.ok) {{
                throw new Error(`HTTP error! status: ${{response.status}}`);
            }}

            const data = await response.json();
            this.cache.set(cacheKey, data);
            
            return data;
        }} catch (error) {{
            console.error(`Error fetching data from ${{endpoint}}:`, error);
            throw error;
        }}
    }}

    async batchProcess(endpoints) {{
        const promises = endpoints.map(endpoint => 
            this.fetchData(endpoint).catch(err => ({{ error: err, endpoint }}))
        );
        
        return await Promise.all(promises);
    }}
}}

// Usage example {i}
const client = new APIClient('https://api.example{i}.com', 'your-api-key-{i}');
const results = await client.batchProcess(['/users', '/posts', '/comments']);
```

### Rust Examples

```rust
// Example {i}: High-performance data processing
use std::collections::{{HashMap, HashSet}};
use std::sync::{{Arc, Mutex}};
use tokio::{{fs, time}};
use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataRecord {{
    id: u64,
    timestamp: u64,
    value: f64,
    category: String,
    metadata: HashMap<String, String>,
}}

#[derive(Debug)]
pub struct DataProcessor {{
    records: Vec<DataRecord>,
    index: HashMap<String, Vec<usize>>,
    cache: Arc<Mutex<HashMap<String, Vec<DataRecord>>>>,
}}

impl DataProcessor {{
    pub fn new() -> Self {{
        Self {{
            records: Vec::new(),
            index: HashMap::new(),
            cache: Arc::new(Mutex::new(HashMap::new())),
        }}
    }}

    pub async fn load_from_file(&mut self, path: &str) -> Result<(), Box<dyn std::error::Error>> {{
        let content = fs::read_to_string(path).await?;
        self.records = serde_json::from_str(&content)?;
        self.build_index();
        Ok(())
    }}

    fn build_index(&mut self) {{
        self.index.clear();
        for (idx, record) in self.records.iter().enumerate() {{
            self.index
                .entry(record.category.clone())
                .or_insert_with(Vec::new)
                .push(idx);
        }}
    }}

    pub fn filter_by_category(&self, category: &str) -> Vec<&DataRecord> {{
        self.index
            .get(category)
            .map(|indices| indices.iter().map(|&idx| &self.records[idx]).collect())
            .unwrap_or_default()
    }}

    pub fn aggregate_values(&self) -> HashMap<String, f64> {{
        let mut sums = HashMap::new();
        for record in &self.records {{
            *sums.entry(record.category.clone()).or_insert(0.0) += record.value;
        }}
        sums
    }}
}}

// Example usage {i}
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {{
    let mut processor = DataProcessor::new();
    processor.load_from_file("data_{i}.json").await?;
    
    let aggregates = processor.aggregate_values();
    println!("Aggregated values: {{:#?}}", aggregates);
    
    Ok(())
}}
```

### Go Examples

```go
// Example {i}: Concurrent data processing
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "sync"
    "time"
)

type DataPoint struct {{
    ID        int64   `json:"id"`
    Timestamp int64   `json:"timestamp"`
    Value     float64 `json:"value"`
    Source    string  `json:"source"`
}}

type Processor struct {{
    client     *http.Client
    results    chan DataPoint
    errors     chan error
    wg         sync.WaitGroup
    rateLimit  chan struct{{}}
}}

func NewProcessor(maxConcurrent int) *Processor {{
    return &Processor{{
        client: &http.Client{{
            Timeout: 30 * time.Second,
        }},
        results:   make(chan DataPoint, 100),
        errors:    make(chan error, 100),
        rateLimit: make(chan struct{{}}, maxConcurrent),
    }}
}}

func (p *Processor) ProcessURL(ctx context.Context, url string) {{
    defer p.wg.Done()
    
    select {{
    case p.rateLimit <- struct{{}}{{}}:
        defer func() {{ <-p.rateLimit }}()
    case <-ctx.Done():
        return
    }}

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {{
        p.errors <- fmt.Errorf("creating request for %s: %w", url, err)
        return
    }}

    resp, err := p.client.Do(req)
    if err != nil {{
        p.errors <- fmt.Errorf("requesting %s: %w", url, err)
        return
    }}
    defer resp.Body.Close()

    var dataPoint DataPoint
    if err := json.NewDecoder(resp.Body).Decode(&dataPoint); err != nil {{
        p.errors <- fmt.Errorf("decoding response from %s: %w", url, err)
        return
    }}

    select {{
    case p.results <- dataPoint:
    case <-ctx.Done():
    }}
}}

func (p *Processor) ProcessBatch(ctx context.Context, urls []string) {{
    for _, url := range urls {{
        p.wg.Add(1)
        go p.ProcessURL(ctx, url)
    }}
    
    go func() {{
        p.wg.Wait()
        close(p.results)
        close(p.errors)
    }}()
}}

// Example usage {i}
func main() {{
    urls := []string{{
        "https://api{i}.example.com/data1",
        "https://api{i}.example.com/data2",
        "https://api{i}.example.com/data3",
    }}

    processor := NewProcessor(10)
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
    defer cancel()

    processor.ProcessBatch(ctx, urls)

    var results []DataPoint
    for result := range processor.results {{
        results = append(results, result)
    }}

    fmt.Printf("Processed %d data points\\n", len(results))
}}
```

""" for i in range(1, 21)]) + """

## Performance Considerations

### Code Block Rendering

Code blocks require special handling:

1. **Syntax Detection** - Language detection from fence info
2. **Escaping** - HTML entity escaping for code content  
3. **Class Attribution** - Adding appropriate CSS classes
4. **Whitespace Preservation** - Maintaining formatting

### Optimization Strategies

```bash
# Benchmark different approaches
time markdown_processor large_code_file.md > /dev/null
perf stat -e cycles,instructions markdown_processor large_code_file.md
valgrind --tool=massif markdown_processor large_code_file.md
```
"""