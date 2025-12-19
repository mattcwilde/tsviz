# Time Series Visualization CLI (tsviz)

A production-ready Python CLI tool for creating interactive time series visualizations using Plotly.

## Features

- Automatically detects time series columns in CSV and Excel files
- Plots all non-empty numeric columns or specific columns of your choice
- Interactive Plotly charts with hover information
- Shows day of the week on hover for date columns with years
- Labeled legends for multiple columns
- Save plots as HTML files or open in browser

## Installation

```bash
pip install -e .
```

## Usage

### Basic usage - plot all numeric columns:
```bash
tsviz data.csv
```

### Plot specific columns:
```bash
tsviz data.csv -c column1 -c column2
```

### Save to HTML file:
```bash
tsviz data.xlsx -o output.html
```

### Custom title:
```bash
tsviz data.csv -c temperature -t "Temperature Over Time"
```

## Supported File Formats

- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

## Requirements

- Python 3.7+
- pandas
- plotly
- click
