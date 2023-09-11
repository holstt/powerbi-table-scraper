import argparse
import json
import logging
import time
from pathlib import Path


def setup_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(name)-25s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.Formatter.converter = time.gmtime  # Use UTC

    # Avoid getting debug logs from external modules
    logging.getLogger("selenium").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)


def get_config_path_from_args():
    args = get_args()
    config_file_path = Path(args["config"])
    return config_file_path


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c",
        "--config",
        required=False,
        help="Path of yaml config file",
        default="./config.yml",  # Assume in root directory
    )
    args = vars(ap.parse_args())
    return args


# Load language strings from a JSON file
def load_language(lang_code: str) -> dict[str, str]:
    with open(f"./locales/{lang_code}.json", "r", encoding="utf-8") as file:
        lang: dict[str, str] = json.load(file)
        return lang
