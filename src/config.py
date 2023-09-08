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


class GuiConfig(BaseModel):
    language: str
    program_name: str


class ConsoleConfig(BaseModel):
    url: HttpUrl
    is_headless: bool
    output_format: OutputFormat
    output_path: Path


class AppConfig(BaseModel):
    mode: Mode
    max_rows: Optional[int] = None
    gui: Optional[GuiConfig] = None
    console: Optional[ConsoleConfig] = None


def load_config(file_path: Path) -> AppConfig:
    with open(file_path, "r") as f:
        config_data = yaml.safe_load(f)

    return AppConfig(**config_data)
