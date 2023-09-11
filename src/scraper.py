# pyright: reportUnknownMemberType=false

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

# NOTE:
# We can't rely on waiting for elements to be visible (i.e. EC.visibility_of_element_located) as an explicit wait may result in PowerBI freezing/becoming non-interactive for some reason
# Therefore, we set implicit wait to 10 to allow up to 10 seconds for elements to appear before throwing an exception when using .find_element(s)
# NB! If elements are not certain to appear, we can temporarily lower the implicit wait time if it is safe to do so, and then restore it afterwards

DEFAULT_WAIT = 10  # seconds

# CSS selectors
FILTER_CSS_SELECTOR = 'div[role="listbox"]'
TABLE_CSS_SELECTOR = ".tableEx"
HEADER_ROW_CSS_SELECTOR = "div.main-cell[role='columnheader']"
DATA_CONTAINER_CSS_SELECTOR = ".mid-viewport > div:nth-child(1)"
ROWS_CSS_SELECTOR = "div[role='row'][row-index]"
ROW_INDEX_ATTRIBUTE = "row-index"
ROW_DATA_CELL_CSS_SELECTOR = ".main-cell"
TABLE_SCROLLBAR_CSS_SELECTOR = "div.scroll-bar-part-bar"


class ScraperException(Exception):
    pass


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
    # is_console_enabled: If true, the selenium driver will open a console window if running in no-console mode e.g. in a GUI
    # is_headless: If true, the selenium driver will run in headless mode (no browser window)
    def __init__(self, options: ScraperOptions):
        self._driver = self._create_driver(options)
        self._options = options
        logger.debug(f"Driver created with options: {options}")
        self._wait = WebDriverWait(self._driver, DEFAULT_WAIT)

    def scrape(self, max_rows: Optional[int] = None):
        # Warn if using limit
        if max_rows:
            logger.warn(f"**Warning: Limiting scrape to {max_rows} rows**")

        logger.debug("Scraping started")
        try:
            self._load_page()
            self._switch_if_iframe()
            if self._options.should_uncheck_filter:
                self._uncheck_filter()
            table = self._scrape_table_data(max_rows)
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

    def _scrape_table_data(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        logger.debug("Scraping table data...")

        # Get table element
        table_el = self._driver.find_element(By.CSS_SELECTOR, TABLE_CSS_SELECTOR)

        # Get column headers
        header_row = table_el.find_elements(By.CSS_SELECTOR, HEADER_ROW_CSS_SELECTOR)
        column_headers = [header.text for header in header_row]

        # Get table rows
        data_container = table_el.find_element(
            By.CSS_SELECTOR, DATA_CONTAINER_CSS_SELECTOR
        )

        table_rows: list[list[str]] = []
        processed_row_indicies: set[int] = set()

        # Reveal and scrape all currently visible rows in table.
        # Scrape and scroll until no new rows are found i.e. we have reached the end of the table.
        has_new_rows = True
        while has_new_rows:
            has_new_rows = False
            rows = data_container.find_elements(By.CSS_SELECTOR, ROWS_CSS_SELECTOR)
            logger.debug(f"Found {len(rows)} rows in current table view")

            # Process current rows
            for row in rows:
                if max_rows and len(processed_row_indicies) >= max_rows:
                    logger.debug(f"Reached max rows: {max_rows}")
                    break

                row_index = self._get_row_index(row)

                # Skip row if already processed
                if row_index in processed_row_indicies:
                    logger.debug(f"Skipping row {row_index} as already processed")
                    continue

                has_new_rows = True
                # logger.debug(f"Processing row {row_index}...")
                row_data = self._scrape_table_row(row)
                table_rows.append(row_data)
                processed_row_indicies.add(row_index)
                logger.debug(f"Processed row {row_index}, first cell: {row_data[0]}")
                # comma = ", ".join(row_data)
                # print(f"Scraped row {scrape_row_index}: {comma}")

            # Scroll down to load more rows
            logger.debug("Scrolling down to load more rows...")
            self._scroll_table_down()

        logger.debug(
            f"Scraping table data complete. Rows: {len(table_rows)}, Columns: {len(column_headers)}"
        )

        return pd.DataFrame(table_rows, columns=column_headers)

    # XXX: Make more dynamic for different table sizes
    def _scroll_table_down(self):
        # Find scroll bar and click right below it to scroll.
        scrollbar = self._driver.find_elements(
            By.CSS_SELECTOR, TABLE_SCROLLBAR_CSS_SELECTOR
        )[
            1
        ]  # Index 1 to get vertical scrollbar

        # In case the scrollbar is not visible, scroll page to reveal it
        self._driver.execute_script("arguments[0].scrollIntoView(true);", scrollbar)

        # Click below scrollbar to scroll down
        actions = ActionChains(self._driver)
        actions.move_to_element_with_offset(scrollbar, xoffset=0, yoffset=39)
        actions.click().pause(0.5)
        actions.perform()

    # Scrape each cell in a row into a list of strings
    def _scrape_table_row(self, row: WebElement) -> list[str]:
        cells = row.find_elements(By.CSS_SELECTOR, ROW_DATA_CELL_CSS_SELECTOR)
        cell_data = [cell.text for cell in cells]
        return cell_data

    def _get_row_index(self, row: WebElement) -> int:
        # row_index = row.get_attribute("row-index") # may make page non-interactive
        # Manually get row-index attribute using javascript
        row_index = int(
            self._driver.execute_script(  # type: ignore
                f"return arguments[0].getAttribute('{ROW_INDEX_ATTRIBUTE}');", row
            )
        )

        return row_index

    def _uncheck_filter(self):
        logger.debug("Unchecking filter...")
        filter = self._driver.find_element(By.CSS_SELECTOR, FILTER_CSS_SELECTOR)

        # Temporary change the wait time to 0 (there may not be any checked elements, so we dont want to wait for them to appear)
        self._driver.implicitly_wait(0)
        prev_last_el = None
        ACTION_WAIT = 0.1

        while True:
            logger.debug("Finding visible checkboxes...")
            checked_elements = filter.find_elements(
                By.CSS_SELECTOR, 'div[aria-checked="true"]'
            )
            unchecked_elements = filter.find_elements(
                By.CSS_SELECTOR, 'div[aria-checked="false"]'
            )
            all_elements = checked_elements + unchecked_elements

            logger.debug(f"Found visible checkboxes: {len(all_elements)}")

            actions = ActionChains(self._driver)

            for checked_element in checked_elements:
                actions.click(checked_element).pause(ACTION_WAIT)
                logger.debug(f"Will uncheck checkbox with text: {checked_element.text}")

            # Move to last visible element and scroll down using down key to load more elements
            last_el = all_elements[-1]
            actions.move_to_element(last_el).pause(ACTION_WAIT).send_keys(
                Keys.ARROW_DOWN
            ).pause(ACTION_WAIT).perform()
            logger.debug(f"Scrolled to last visible checkbox with text: {last_el.text}")

            # If we have scrolled to the same element twice, we have reached the end of the list
            if last_el and prev_last_el == last_el:
                logger.debug("Reached end of list. All checkboxes unchecked.")
                break

            prev_last_el = last_el

        # Restore the wait time
        self._driver.implicitly_wait(DEFAULT_WAIT)
        logger.debug("Filter unchecked")

    def _load_page(self):
        PAGE_LOADED_CSS_SELECTOR = "transform.bringToFront"

        logger.debug("Loading page...")
        self._driver.get(self._options.url)
        self._wait.until(
            EC.presence_of_element_located(  # Do not use visibility_of_element_located, as it may make the page non-interactive
                (By.CSS_SELECTOR, PAGE_LOADED_CSS_SELECTOR)
            )  # Present when page is loaded
        )
        sleep(1)  # For good measure
        logger.debug("Page loaded")

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
        # Driver will wait for X seconds for elements to appear before throwing an exception (default is 0)
        driver.implicitly_wait(DEFAULT_WAIT)
        return driver
