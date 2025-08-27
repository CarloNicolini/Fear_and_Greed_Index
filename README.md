# Fear and Greed Index

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package for scraping and analyzing CNN's Fear and Greed Index historical data with a command-line interface.

## Overview

This package provides tools to collect, process, and analyze historical Fear and Greed Index data from CNN's financial data API. The Fear and Greed Index is a market sentiment indicator that combines multiple financial metrics to gauge investor sentiment on a scale from 0 (Extreme Fear) to 100 (Extreme Greed).

## Features

- Modern CLI powered by Typer with comprehensive help and validation
- Rich terminal output with progress bars, tables, and colored console display
- Fast data processing using Polars for efficient DataFrame operations
- Parquet and CSV output format support for optimal data storage
- Data merging capability to update existing datasets
- Comprehensive summary statistics with tabular displays
- Robust error handling with user-friendly messages

## Market Sentiment Components

The Fear and Greed Index combines seven market sentiment indicators:

- **Stock Price Momentum**: S&P 500 versus 125-day moving average
- **Stock Price Strength**: Number of stocks hitting 52-week highs versus lows
- **Stock Price Breadth**: Trading volume in advancing versus declining stocks
- **Put/Call Options**: Put/call ratio as a fear indicator
- **Junk Bond Demand**: Spread between high-yield bonds and treasury bonds
- **Market Volatility**: VIX compared to 50-day moving average
- **Safe Haven Demand**: Performance difference between stocks and bonds

**Index Scale:**
- 0-24: Extreme Fear
- 25-49: Fear
- 50-74: Greed  
- 75-100: Extreme Greed

## Installation

### Requirements

- Python 3.12 or higher
- uv package manager (recommended) or pip

### Installing the Package

```bash
# Clone the repository
git clone https://github.com/yourusername/Fear_and_Greed_Index.git
cd Fear_and_Greed_Index

# Install using uv (recommended)
uv sync

# Alternative installation with pip
pip install -e .
```

### Dependencies

- **polars** (>= 1.32.3): High-performance DataFrame operations
- **typer** (>= 0.16.1): Modern CLI framework
- **rich** (>= 13.9.4): Rich text and beautiful formatting
- **requests** (>= 2.31.0): HTTP library for API requests
- **fake-useragent** (>= 2.2.0): Random user agents for web scraping

## Usage

### Command Line Interface

#### Basic Commands

```bash
# Display help information
uv run fng-cli --help

# Basic data scraping with default settings
uv run fng-cli scrape

# Display Fear and Greed Index information
uv run fng-cli info
```

#### Advanced Usage

```bash
# Scrape data for a specific date range
uv run fng-cli scrape \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --output fng_2023.parquet

# Merge with existing CSV data and backfill missing values
uv run fng-cli scrape \
    --input-csv existing_data.csv \
    --backfill \
    --output merged_data.parquet

# Export data in CSV format
uv run fng-cli scrape \
    --format csv \
    --output fng_data.csv \
    --no-summary
```

### Python API

```python
from pathlib import Path
from fng import FearAndGreedIndex

# Initialize the scraper
scraper = FearAndGreedIndex()

# Process data for a specific date range
data = scraper.process_data(
    start_date="2024-01-01",
    end_date="2024-01-31",
    backfill=True
)

# Save data in different formats
scraper.save_data(data, Path("output.parquet"), "parquet")
scraper.save_data(data, Path("output.csv"), "csv")

# Display summary statistics
scraper.display_summary(data)

# Access data properties
print(f"Total records: {data.height}")
print(f"Average Fear and Greed Index: {data['Fear Greed'].mean():.2f}")
```

## Command Reference

### fng-cli scrape

Primary command for scraping Fear and Greed Index data from CNN's API.

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--start-date` | `-s` | TEXT | Start date in YYYY-MM-DD format | `2020-09-19` |
| `--end-date` | | TEXT | End date in YYYY-MM-DD format | Current date |
| `--input-csv` | `-i` | FILE | Path to existing CSV file for merging | None |
| `--output` | `-o` | PATH | Output file path | `fng_data.parquet` |
| `--format` | `-f` | TEXT | Output format (parquet or csv) | `parquet` |
| `--backfill` | `-b` | FLAG | Backfill missing values instead of zeros | False |
| `--summary` | | FLAG | Display data summary after processing | True |

### fng-cli info

Displays comprehensive information about the Fear and Greed Index methodology, components, and interpretation scale.

## Examples

### Historical Data Analysis

```bash
# Collect data from the beginning of 2023
uv run fng-cli scrape \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --output historical_2023.parquet
```

### Data Integration

```bash
# Update existing dataset with new data
uv run fng-cli scrape \
    --input-csv legacy_data.csv \
    --start-date 2024-01-01 \
    --backfill \
    --output updated_dataset.parquet
```

### Export for External Analysis

```bash
# Generate CSV for use in Excel or other analysis tools
uv run fng-cli scrape \
    --start-date 2020-01-01 \
    --format csv \
    --output complete_dataset.csv
```

## Architecture

### Project Structure

```
src/fng/
├── __init__.py          # Package initialization and exports
├── fngindex.py          # Core FearAndGreedIndex class implementation
└── cli.py              # Command-line interface using Typer
```

### Core Components

**FearAndGreedIndex Class**

The main class providing data collection and processing functionality:

- `fetch_historical_data(start_date)`: Retrieves data from CNN API
- `load_existing_data(csv_file)`: Loads data from existing CSV files
- `process_data(start_date, end_date, csv_file, backfill)`: Main processing pipeline
- `save_data(data, output_path, format_type)`: Exports data in specified format
- `display_summary(data)`: Generates statistical summary and data preview

## Development

### Setting Up Development Environment

```bash
# Clone and set up the development environment
git clone https://github.com/yourusername/Fear_and_Greed_Index.git
cd Fear_and_Greed_Index
uv sync

# Install development dependencies
uv add --dev pytest black ruff mypy

# Run code formatting
uv run black src/
uv run ruff check src/

# Run type checking
uv run mypy src/
```

### Running Tests

```bash
# Execute test suite
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/fng
```

### Code Quality

This project follows Python best practices:

- **Code Style**: Black formatting with line length of 88 characters
- **Linting**: Ruff for fast Python linting
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings following Google style

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make changes following the existing code style and conventions
4. Add tests for new functionality
5. Ensure all tests pass and code quality checks succeed
6. Commit changes (`git commit -m 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.

## Data Source and Legal Notice

This package retrieves data from CNN's publicly available Fear and Greed Index API. The data is used for educational and analytical purposes. Users are responsible for ensuring compliance with CNN's terms of service and any applicable data usage policies.

## Acknowledgments

- Original concept inspired by [hackingthemarkets/sentiment-fear-and-greed](https://github.com/hackingthemarkets/sentiment-fear-and-greed)
- Data provided by [CNN Fear and Greed Index](https://www.cnn.com/markets/fear-and-greed)
- Built using modern Python tooling: Polars, Typer, and Rich

## Support

For questions, issues, or contributions, please use the GitHub issue tracker or submit pull requests through the standard GitHub workflow.

---

**Disclaimer**: The Fear and Greed Index is one of many market sentiment indicators. This tool is provided for educational and analytical purposes only. Always conduct thorough research and consider multiple factors when making investment decisions.