# pyright: reportUnknownMemberType=false

import logging
from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver

from src.scraper.powerbi_scraper import ScraperOptions

logger = logging.getLogger(__name__)

DEFAULT_WAIT = 10  # seconds


# Create driver by inheriting from webdriver.Chrome
class CustomDriver(WebDriver):
    def __init__(self, options: ScraperOptions):
        # We create our own chrome_service to use CREATE_NO_WINDOW flag
        # CREATE_NO_WINDOW will avoid opening driver console window if running in no-console mode e.g. in a GUI
        chrome_service = ChromeService()
        if not options.is_console_enabled:
            logger.debug("Disabled Selenium driver console window")
            chrome_service.creation_flags = CREATE_NO_WINDOW

        chrome_options = webdriver.ChromeOptions()

        if options.is_headless:
            chrome_options.add_argument("--headless=new")

        super().__init__(options=chrome_options, service=chrome_service)
        # Driver will wait for X seconds for elements to appear before throwing an exception (default is 0)
        self.implicitly_wait(DEFAULT_WAIT)
