import argparse
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
