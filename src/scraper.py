import logging
from dataclasses import dataclass
from subprocess import CREATE_NO_WINDOW
from time import sleep
from typing import Optional

import pandas as pd
from pydantic import HttpUrl
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


TABLE_CSS_SELECTOR = ".tableEx"


@dataclass(frozen=True)
class ScraperOptions:
    url: str
    is_headless: bool = False
    is_console_enabled: bool = True


@dataclass(frozen=True)
class ScrapeResult:
    table: pd.DataFrame


class PowerBiScraper:
    # is_console_enabled: If true, the selenium driver will open a console window if running in no-console mode e.g. in a GUI
    # is_headless: If true, the selenium driver will run in headless mode (no browser window)
    def __init__(self, options: ScraperOptions):
        self._driver = self._create_driver(options)
        self._options = options
        logger.debug(f"Driver created with options: {options}")

    def scrape(self):
        self._driver.get(self._options.url)

    def _create_driver(self, options: ScraperOptions) -> WebDriver:
        # We create our own chrome_service to use CREATE_NO_WINDOW flag
        # CREATE_NO_WINDOW will avoid opening driver console window if running in no-console mode e.g. in a GUI
        chrome_service = ChromeService()
        if not options.is_console_enabled:
            logger.debug("Disabled Selenium driver console window")
            chrome_service.creation_flags = CREATE_NO_WINDOW

        chrome_options = webdriver.ChromeOptions()

        if options.is_headless:
            chrome_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
        # Driver will wait for 10 seconds for elements to appear before throwing an exception (default is 0)
        driver.implicitly_wait(10)
        return driver
