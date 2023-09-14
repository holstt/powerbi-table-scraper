import logging
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from src import config, utils
from src.config import AppConfig, Mode, OutputFormat
from src.gui.gui import ScraperGui, UiSubmitArgs
from src.save import save_table
from src.scraper import PowerBiScraper, ScraperOptions

logger = logging.getLogger(__name__)


def main(app_config: AppConfig):
    logger.info(f"Running in {app_config.mode} mode")

    match app_config.mode:
        case Mode.GUI:
            use_gui(app_config)
        case Mode.CONSOLE:
            use_console(app_config)

    # input("Press enter to exit")


def use_gui(app_config: AppConfig):
    # if app_config.gui is None:
    #     raise ValueError("Mode is set to GUI but GUI config is missing")
    logger.debug(f"Using GUI config: {app_config.gui}")

    def on_run_scrape(
        ui_args: UiSubmitArgs, on_scrape_complete: Callable[[pd.DataFrame], None]
    ):
        table = scrape_and_save(
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
    table = scrape_and_save(
        ScraperOptions(
            url=config.url.unicode_string(),
            is_headless=config.is_headless,
            should_uncheck_filter=app_config.should_uncheck_filter,
        ),
        config.output_path,
        config.output_format,
        max_rows=app_config.max_rows,
    )


def scrape_and_save(
    options: ScraperOptions,
    save_path: Path,
    save_format: OutputFormat,
    max_rows: Optional[int] = None,
) -> pd.DataFrame:
    scraper = PowerBiScraper(options)
    table = scraper.scrape(max_rows=max_rows)
    scraper.close()  # XXX: Choose to browser keep open?
    save_path = save_table(table, save_path, save_format)
    logger.info(f"Table saved to {save_path.absolute()}")
    return table


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
