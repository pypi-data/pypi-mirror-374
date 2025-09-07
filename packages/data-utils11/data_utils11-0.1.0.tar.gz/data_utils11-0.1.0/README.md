# Data Utils

A simple data utilities package for common data operations.

## Installation

```bash
# From workspace root
uv sync

# Run the CLI
uv run data-utils --help
```

## Usage

```bash
# Generate sample data
uv run data-utils generate --rows 1000 --output sample.parquet

# Inspect data
uv run data-utils inspect sample.parquet

# Convert formats
uv run data-utils convert sample.parquet --output sample.csv --format csv
```
