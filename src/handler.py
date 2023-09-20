import logging
from typing import Callable

import pandas as pd

import src.usecase as usecase
from src.config import AppConfig
from src.gui.gui import ScraperGui, UiSubmitArgs
from src.scraper.powerbi_scraper import ScraperOptions

logger = logging.getLogger(__name__)


def use_gui(app_config: AppConfig):
    # if app_config.gui is None:
    #     raise ValueError("Mode is set to GUI but GUI config is missing")
    logger.debug(f"Using GUI config: {app_config.gui}")

    def on_run_scrape(
        ui_args: UiSubmitArgs, on_scrape_complete: Callable[[pd.DataFrame], None]
    ):
        table = usecase.scrape_and_save(
            ScraperOptions(
                url=ui_args.url,
                is_console_enabled=False,
                should_uncheck_filter=app_config.should_uncheck_filter,
                is_headless=ui_args.is_headless,
            ),
            ui_args.output_path,
            ui_args.output_format,
            max_rows=app_config.max_rows,
        )
        # Notify UI that scrape is complete
        on_scrape_complete(table)

    ui = ScraperGui(app_config.gui, on_run_scrape)
    ui.show()


def use_console(app_config: AppConfig):
    if app_config.console is None:
        raise ValueError("Mode is set to CONSOLE but CONSOLE config is missing")
    logger.debug(f"Using CONSOLE config: {app_config.console}")

    config = app_config.console
    table = usecase.scrape_and_save(
        ScraperOptions(
            url=config.url.unicode_string(),
            is_headless=config.is_headless,
            should_uncheck_filter=app_config.should_uncheck_filter,
        ),
        config.output_path,
        config.output_format,
        max_rows=app_config.max_rows,
    )
