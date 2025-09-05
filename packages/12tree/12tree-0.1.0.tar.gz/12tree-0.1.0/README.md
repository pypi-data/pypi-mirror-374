# 12Tree

12Tree is an efficient floating point data store built on AVL tree indexing. It provides fast insertion, search, and range queries for floating point numbers with automatic balancing for optimal performance.

## Features

- 🚀 **High Performance**: AVL tree balancing ensures O(log n) operations
- 🔍 **Range Queries**: Efficiently find all values within a range
- 🎯 **Tolerance Search**: Search with floating point tolerance
- 💾 **Persistence**: Save and load data to/from JSON files
- 🖥️ **CLI Interface**: Command-line interface for easy interaction
- 📊 **Statistics**: Built-in size and performance tracking

## Installation

```bash
pip install 12tree
```

## Quick Start

### Using the CLI

```bash
# Insert some values
12tree insert 3.14 "pi"
12tree insert 2.71 "e"
12tree insert 1.41 "sqrt(2)"

# Search for a value
12tree search 3.14

# Find values in a range
12tree range-search 1.0 4.0

# List all values
12tree list-values

# Show statistics
12tree stats
```

### Using the Python API

```python
from twelve_tree import FloatTreeStore

# Create a store
store = FloatTreeStore()

# Insert values
store.insert(3.14, "pi")
store.insert(2.71, "e")
store.insert(1.41, "sqrt(2)")

# Search with tolerance
result = store.search(3.14159, tolerance=0.01)
print(result)  # "pi"

# Range search
results = store.find_range(1.0, 3.0)
for result in results:
    print(f"Value: {result['value']}, Data: {result['data']}")

# Get all values (sorted)
values = store.get_all_values()
print(values)  # [1.41, 2.71, 3.14]
```

## API Reference

### FloatTreeStore

#### Methods

- `insert(value: float, data: Any = None)` - Insert a floating point value
- `search(value: float, tolerance: float = 0.0)` - Search for a value with tolerance
- `find_range(min_val: float, max_val: float)` - Find all values in a range
- `get_all_values()` - Get all values in sorted order
- `size()` - Get number of stored values
- `is_empty()` - Check if store is empty
- `clear()` - Clear all data
- `save_to_file(filepath)` - Save to JSON file
- `load_from_file(filepath)` - Load from JSON file

### CLI Commands

- `12tree insert <value> [data]` - Insert a value
- `12tree search <value> [--tolerance TOL]` - Search for a value
- `12tree range-search <min> <max>` - Find values in range
- `12tree list-values` - List all values
- `12tree stats` - Show statistics
- `12tree save <filepath>` - Save to file
- `12tree load <filepath>` - Load from file
- `12tree clear` - Clear all data

## Performance

- **Insert**: O(log n)
- **Search**: O(log n)
- **Range Query**: O(log n + k) where k is result size
- **Memory**: O(n) for n values

## Use Cases

- **Scientific Computing**: Store and query floating point measurements
- **Financial Data**: Index stock prices, rates, and calculations
- **Geospatial Data**: Store coordinates and perform proximity searches
- **Time Series**: Efficiently store and query timestamped float values
- **Machine Learning**: Feature storage and similarity searches

## Requirements

- Python 3.8+
- No external dependencies (only typer for CLI)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Roadmap

- [ ] B-tree indexing for even better performance
- [ ] Compression for large datasets
- [ ] Concurrent access support
- [ ] REST API server
- [ ] GUI interface
