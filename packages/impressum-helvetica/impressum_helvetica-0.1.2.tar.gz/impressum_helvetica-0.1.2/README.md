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

### As a Python Package

After installation, you can import and use the package in your Python code:

```python
import asyncio
from impressum_helvetica.collect_impressum import capture_and_return_impressum_url

# Capture impressum for a single website
async def main():
    
    # Capture and get the impressum URL
    impressum_url = await capture_and_return_impressum_url("interdiscount.ch")
    print(f"Found impressum at: {impressum_url}")

# Run the async function
asyncio.run(main())
```

### Command Line Interface

#### Single website
```bash
python impressum_helvetica/collect_impressum.py digitec.ch
python impressum_helvetica/collect_impressum.py interdiscount.ch
```

#### Batch processing
```bash
python impressum_helvetica/collect_impressum.py
```
Processes all hostnames from `impressum_helvetica/hostnames.py` that don't have Impressum URLs yet.

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
