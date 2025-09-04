# Table-Heavy Markdown Document

This document is designed to test performance with many tables.

## Introduction

Tables are often computationally expensive to render, so this document focuses on table-heavy content.

""" + "\n\n".join([f"""## Table Set {i}

### Employee Data Table {i}

| ID | Name | Department | Salary | Years | Performance | Bonus | Location |
|----|------|------------|---------|-------|-------------|-------|----------|
""" + "\n".join([f"| {j:03d} | Employee {i}-{j} | Dept-{(j%5)+1} | ${(j*1000+50000):,} | {(j%10)+1} | {['Poor','Fair','Good','Excellent'][j%4]} | ${(j*100):,} | Office-{(j%3)+1} |" for j in range(1, 26)]) + f"""

### Sales Data Table {i}

| Quarter | Product | Units Sold | Revenue | Profit Margin | Market Share | Growth Rate | Region |
|---------|---------|------------|---------|---------------|--------------|-------------|--------|
""" + "\n".join([f"| Q{(j%4)+1} | Product-{i}-{j} | {j*100+500:,} | ${(j*5000+25000):,} | {(j%20)+10}% | {(j%15)+5}% | +{(j%30)+5}% | Region-{(j%4)+1} |" for j in range(1, 21)]) + f"""

### Inventory Table {i}

| SKU | Item Name | Category | Stock | Reorder Level | Unit Cost | Retail Price | Supplier |
|-----|-----------|----------|-------|---------------|-----------|--------------|----------|
""" + "\n".join([f"| SKU-{i}-{j:03d} | Item {i}-{j} | Cat-{(j%8)+1} | {j*10+100} | {j*2+20} | ${(j*2.5+10):.2f} | ${(j*5+25):.2f} | Supplier-{(j%5)+1} |" for j in range(1, 31)]) for i in range(1, 16)]) + """

## Summary Tables

### Performance Summary

| Metric | Min | Max | Average | Median | Std Dev |
|--------|-----|-----|---------|--------|---------|
| Processing Time | 0.001s | 2.456s | 0.234s | 0.189s | 0.123s |
| Memory Usage | 12MB | 156MB | 45MB | 38MB | 23MB |
| CPU Usage | 5% | 95% | 34% | 28% | 18% |
| Throughput | 100/s | 5000/s | 1250/s | 1100/s | 450/s |

### Comparison Matrix

| Implementation | Speed | Memory | Features | Compatibility | Score |
|----------------|-------|--------|----------|---------------|-------|
| Pure Python | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3.8/5 |
| Rust Accel | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4.5/5 |
| C Extension | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 3.6/5 |
"""