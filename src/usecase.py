import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import OutputFormat
from src.save import save_table
from src.scraper.driver import CustomDriver
from src.scraper.powerbi_scraper import PowerBiScraper, ScraperOptions

logger = logging.getLogger(__name__)


def scrape_and_save(
    options: ScraperOptions,
    save_path: Path,
    save_format: OutputFormat,
    max_rows: Optional[int] = None,
) -> pd.DataFrame:
    scraper = PowerBiScraper(options, CustomDriver(options))
    table = scraper.scrape(max_rows=max_rows)
    scraper.close()  # XXX: Choose to browser keep open? E.g. when debugging
    save_path = save_table(table, save_path, save_format)
    logger.info(f"Table saved to {save_path.absolute()}")
    return table
