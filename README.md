# powerbi-table-scraper

[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Python tool for scraping Power BI tables into an Excel or CSV file using Selenium. The tool can be run as a console application or with a GUI.

![**Placeholder for screenshot/GIF of GUI**](path-to-screenshot-or-gif)

## Prerequisites

-   [Python 3.11](https://www.python.org/downloads/release/python-311/)
-   [Poetry](https://python-poetry.org/docs/) (optional)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/holstt/powerbi-table-scraper.git
cd powerbi-table-scraper
```

2. Install dependencies using Poetry:

```bash
poetry install
```

For non-poetry users, a `requirements.txt` file is also provided.

## Configuration

To set up configuration:

1. Rename `config.example.yml` to `config.yml`.

2. Update the `config.yml` file with your specific settings.

-   To switch between GUI and Console mode, change the `mode` value to either `gui` or `console`.
-   Depending on the mode, the `gui` or `console` section of the config file will be used. The other section will be ignored, but you can keep it in the file if you still want to have the possibility to switch between modes.

```yml
mode: gui # or console
# max_rows: 3 # Uncomment to limit the number of rows scraped (e.g. for testing)

gui:
    language: en # en or da
    program_name: PowerBI Table Scraper

console:
    url: https://app.powerbi.com/XXXXX # URL to the Power BI report
    is_headless: false # 'true' hides the the browser window
    output_path: /path/to/output.ext # Any file extension will be ignored - is determined by output_format
    output_format: excel # excel or csv
```

## Usage

After setting up `./config.yml`:

```bash
python main.py
```

For the GUI mode, follow the on-screen instructions. For the Console mode, scraping will start automatically based on the settings defined in `config.yml`.

### Creating a Standalone Executable with PyInstaller

To create a standalone executable of the tool, run the following command:

```bash
pyinstaller --onefile --noconsole --name="Power BI Table Scraper" ./src/main.py
```

The executable will be created in the `./dist` folder - remember to include the `config.yml` file in the same folder as the executable. Now the tool can be run without having to install Python or any dependencies.
