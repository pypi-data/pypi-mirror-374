# Impressum Helvetica

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-dependency%20management-orange.svg)](https://python-poetry.org/)
[![Playwright](https://img.shields.io/badge/playwright-automation-green.svg)](https://playwright.dev/)

Automatically collect Impressum (legal notice) pages from websites using Playwright.

## Installation

```bash
poetry shell
poetry install
playwright install
```

## Usage

### Single website
```bash
python src/collect_impressum.py digitec.ch
python src/collect_impressum.py interdiscount.ch
```

### Batch processing
```bash
python src/collect_impressum.py
```
Processes all hostnames from `src/hostnames.py` that don't have Impressum URLs yet.

## Examples

The tool automatically:
- Finds Impressum links using multilingual keywords (German, English, French)
- Handles cookie consent banners
- Captures full-page screenshots
- Saves HTML content

### Output Structure
```
results/
├── html/
│   ├── example.ch.html
└── img/
    ├── example.ch.png
```
