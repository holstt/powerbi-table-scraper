# pyright: reportUnknownMemberType=false

import logging
from dataclasses import dataclass
from time import sleep
from typing import Optional

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.scraper.filter_scraper import FilterScraper
from src.scraper.table_scraper import TableScraper

logger = logging.getLogger(__name__)

# NOTE:
# We can't rely on waiting for elements to be visible (i.e. EC.visibility_of_element_located) as an explicit wait may result in PowerBI freezing/becoming non-interactive for some reason
# Therefore, we set implicit wait to 10 to allow up to 10 seconds for elements to appear before throwing an exception when using .find_element(s)
# NB! If elements are not certain to appear, we can temporarily lower the implicit wait time if it is safe to do so, and then restore it afterwards

DEFAULT_WAIT = 10  # seconds
PAGE_LOADED_CSS_SELECTOR = "transform.bringToFront"


class ScraperException(Exception):
    pass


# XXX: Split into separate options for PowerBI and Selenium?
# is_console_enabled: If true, the selenium driver will open a console window if running in no-console mode e.g. in a GUI
# is_headless: If true, the selenium driver will run in headless mode (no browser window)
@dataclass(frozen=True)
class ScraperOptions:
    url: str
    is_headless: bool = False
    is_console_enabled: bool = True
    should_uncheck_filter: bool = False


# @dataclass(frozen=True)
# class ScrapeResult:
#     table: pd.DataFrame


class PowerBiScraper:
    def __init__(self, options: ScraperOptions, driver: WebDriver):
        self._driver = driver
        self._options = options
        logger.debug(f"Driver created with options: {options}")
        self._wait = WebDriverWait(self._driver, DEFAULT_WAIT)
        # XXX: Inject?
        self._table_scraper = TableScraper(self._driver)
        self._filter_scraper = FilterScraper(self._driver)

    def scrape(self, max_rows: Optional[int] = None):
        # Warn if using limit
        if max_rows:
            logger.warn(f"**Warning: Limiting scrape to {max_rows} rows**")

        logger.debug("Scraping started")
        try:
            self._load_page()
            self._switch_if_iframe()
            if self._options.should_uncheck_filter:
                self._filter_scraper.uncheck_filter()
            table = self._table_scraper.execute(max_rows)
        except Exception as e:
            raise ScraperException("An error occurred while scraping") from e

        logger.debug("Scraping complete")
        return table

    def close(self):
        self._driver.close()

    # If dashboard embedded in page, it will be in an iframe -> switch to iframe
    def _switch_if_iframe(self):
        # Disable wait time to avoid waiting for iframe to appear
        self._driver.implicitly_wait(0)

        # find_elementS to avoid exception if no iframe found
        iframe = self._driver.find_elements(By.CSS_SELECTOR, "iframe")
        if iframe:
            iframe = iframe[0]
            self._driver.switch_to.frame(iframe)
            # Scroll to iframe to ensure it is in view
            self._driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
            logger.debug("Switched to iframe")
        else:
            logger.debug("No iframe found")

        # Restore wait time
        self._driver.implicitly_wait(DEFAULT_WAIT)

    def _load_page(self):
        logger.debug("Loading page...")
        self._driver.get(self._options.url)
        self._wait.until(
            EC.presence_of_element_located(  # Do not use visibility_of_element_located, as it may make the page non-interactive
                (By.CSS_SELECTOR, PAGE_LOADED_CSS_SELECTOR)
            )  # Present when page is loaded
        )
        sleep(1)  # For good measure
        logger.debug("Page loaded")
