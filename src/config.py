from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from click import Option
from pydantic import BaseModel, HttpUrl, ValidationError


class Mode(Enum):
    GUI = "gui"
    CONSOLE = "console"


class OutputFormat(Enum):
    CSV = "csv"
    EXCEL = "excel"


class GuiDefaultValues(BaseModel):
    url: Optional[HttpUrl] = None
    is_headless: bool = True
    output_format: OutputFormat = OutputFormat.EXCEL
    output_path: Optional[Path] = None


class GuiConfig(BaseModel):
    language: str = "en"
    program_name: str = "Power BI Table Scraper"
    default_values: GuiDefaultValues = GuiDefaultValues()


class ConsoleConfig(BaseModel):
    url: HttpUrl
    is_headless: bool = True
    output_format: OutputFormat = OutputFormat.EXCEL
    output_path: Path = Path("output.xlsx").absolute()


class AppConfig(BaseModel):
    mode: Mode
    max_rows: Optional[int] = None
    should_uncheck_filter: bool = False
    gui: GuiConfig = GuiConfig()
    console: Optional[ConsoleConfig] = None


def load_config(file_path: Path) -> AppConfig:
    with open(file_path, "r") as f:
        config_data = yaml.safe_load(f)

    return AppConfig(**config_data)
