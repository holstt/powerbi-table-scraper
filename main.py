import logging

import src.handler as handler
from src import config, utils
from src.config import AppConfig, Mode

logger = logging.getLogger(__name__)


def main(app_config: AppConfig):
    logger.info(f"Running in {app_config.mode} mode")

    match app_config.mode:
        case Mode.GUI:
            handler.use_gui(app_config)
        case Mode.CONSOLE:
            handler.use_console(app_config)

    # input("Press enter to exit")


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
