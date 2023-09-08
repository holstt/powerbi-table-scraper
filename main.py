import logging
from pathlib import Path

import pandas as pd

from src import config, utils
from src.config import AppConfig, Mode
from src.save import save_csv

logger = logging.getLogger(__name__)


def main(app_config: AppConfig):
    logger.info(f"Running in {app_config.mode} mode")

    # Get specific config based on mode
    if app_config.mode == Mode.GUI:
        if app_config.gui is None:
            raise ValueError("Mode is set to GUI but GUI config is missing")
        logger.debug(f"Using GUI config: {app_config.gui}")
    # Use app_config.gui
    elif app_config.mode == Mode.CONSOLE:
        if app_config.console is None:
            raise ValueError("Mode is set to CONSOLE but CONSOLE config is missing")
        # Use app_config.console
        logger.debug(f"Using CONSOLE config: {app_config.console}")


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
        logger.exception(f"Unhandled exception occurred: {e}")
        raise e