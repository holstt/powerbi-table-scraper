# pyright: reportUnknownMemberType=false

import logging
from time import sleep
from typing import Optional

import pandas as pd
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)

# CSS selectors
TABLE_CSS_SELECTOR = ".tableEx"
HEADER_ROW_CSS_SELECTOR = "div.main-cell[role='columnheader']"
DATA_CONTAINER_CSS_SELECTOR = ".mid-viewport > div:nth-child(1)"
ROWS_CSS_SELECTOR = "div[role='row'][row-index]"
ROW_INDEX_ATTRIBUTE = "row-index"
ROW_DATA_CELL_CSS_SELECTOR = ".main-cell"
TABLE_SCROLLBAR_CSS_SELECTOR = "div.scroll-bar-part-bar"


class TableScraper:
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def execute(self, max_rows: Optional[int] = None) -> pd.DataFrame:
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
        iteration = 0

        while has_new_rows:
            iteration += 1
            has_new_rows = False
            rows = data_container.find_elements(By.CSS_SELECTOR, ROWS_CSS_SELECTOR)
            # logger.debug(f"Found {len(rows)} rows in current table view")

            # Process current rows
            skipped_rows = 0
            for row in rows:
                if max_rows and len(processed_row_indicies) >= max_rows:
                    logger.debug(f"Reached max rows: {max_rows}")
                    break

                row_index = self._get_row_index(row)

                # Skip row if already processed
                if row_index in processed_row_indicies:
                    # logger.debug(f"Skipping row {row_index} as already processed")
                    skipped_rows += 1
                    continue

                has_new_rows = True
                # logger.debug(f"Processing row {row_index}...")
                row_data = self._scrape_table_row(row)
                table_rows.append(row_data)
                processed_row_indicies.add(row_index)
                logger.debug(f"Processed row {row_index}, first cell: {row_data[0]}")
                # comma = ", ".join(row_data)
                # print(f"Scraped row {scrape_row_index}: {comma}")

            if skipped_rows:
                logger.debug(
                    f"Skipped {skipped_rows} of {len(rows)} rows as already processed"
                )
            # After the first iteration, we expect to find some overlap of rows between iterations. If all rows are unseen, we might be scrolling too far down for each iteration.
            elif iteration > 1:
                logger.warning(
                    "Found no already processed rows in current table view. Ensure that scraper is not scrolling too far down."
                )

            # Scroll down to load more rows
            logger.debug("Scrolling down to load more rows...")
            self._scroll_with_key(rows[-1])
            # self._scroll_with_bar() # XXX: Option to choose scroll method?

        logger.debug("Reached end of table. No new rows found.")
        logger.debug(
            f"Scraping complete. Rows: {len(table_rows)}, Columns: {len(column_headers)}"
        )

        return pd.DataFrame(table_rows, columns=column_headers)

    # Using key down to scroll - this seems to be more reliable across different table types than using the scrollbar.
    # NB: This may be a slow method for tables that only scroll down 1 row for every key press. However, other tables will scroll down multiple rows per key press.
    def _scroll_with_key(self, last_table_el: WebElement):
        actions = ActionChains(self._driver)
        ACTION_WAIT = 0.1

        actions.move_to_element(last_table_el).pause(ACTION_WAIT).send_keys(
            Keys.ARROW_DOWN
        ).pause(ACTION_WAIT).perform()

    # TODO: Make it work with different table sizes
    # Using scrollbar and is able to reveal multiple new rows for each scroll, but unreliable across different table types.
    def _scroll_with_bar(self):
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
