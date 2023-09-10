import logging
from dataclasses import dataclass
from pathlib import Path
from re import S
from time import sleep
from typing import Optional

import pandas as pd

from src import config, utils
from src.config import AppConfig, Mode, OutputFormat
from src.save import save_csv, save_table
from src.scraper import PowerBiScraper, ScraperOptions

logger = logging.getLogger(__name__)


@dataclass
class GuiInput:
    url: str
    is_headless: bool
    output_path: Path
    output_format: OutputFormat


def main(app_config: AppConfig):
    logger.info(f"Running in {app_config.mode} mode")

    match app_config.mode:
        case Mode.GUI:
            use_gui(app_config)
        case Mode.CONSOLE:
            use_console(app_config)

    input("Press enter to exit")


def use_console(app_config: AppConfig):
    if app_config.console is None:
        raise ValueError("Mode is set to CONSOLE but CONSOLE config is missing")
    logger.debug(f"Using CONSOLE config: {app_config.console}")

    console_config = app_config.console
    result = scrape(
        ScraperOptions(
            url=console_config.url.unicode_string(),
            is_headless=console_config.is_headless,
            should_uncheck_filter=app_config.should_uncheck_filter,
        ),
        console_config.output_path,
        console_config.output_format,
        max_rows=app_config.max_rows,
    )


def use_gui(app_config: AppConfig):
    if app_config.gui is None:
        raise ValueError("Mode is set to GUI but GUI config is missing")
    logger.debug(f"Using GUI config: {app_config.gui}")

    gui_config = app_config.gui
    # TODO: Receive input/options from GUI
    # Pass on_gui_submit to GUI as callback
    # Use app_config.gui

    def on_gui_submit(values: GuiInput):
        result = scrape(
            ScraperOptions(
                url=values.url,
                is_console_enabled=False,
                should_uncheck_filter=app_config.should_uncheck_filter,
            ),
            values.output_path,
            values.output_format,
        )


def scrape(
    options: ScraperOptions,
    save_path: Path,
    save_format: OutputFormat,
    max_rows: Optional[int] = None,
):
    scraper = PowerBiScraper(options)
    table = scraper.scrape(max_rows=max_rows)
    # scraper.close()
    save_path = save_table(table, save_path, save_format)
    logger.info(f"Table saved to {save_path}")


if __name__ == "__main__":
    # utils.setup_logging()
    utils.setup_logging(logging.DEBUG)
    try:
        config_path = utils.get_config_path_from_args()
        app_config = config.load_config(config_path)
        main(app_config)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Unhandled exception occurred: {e}", exc_info=True)
        raise e
