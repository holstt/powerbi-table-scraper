# pyright: reportUnknownMemberType=false

import logging

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

# CSS selectors
FILTER_CSS_SELECTOR = 'div[role="listbox"]'
CHECKED_FILTER_CSS_SELECTOR = 'div[aria-checked="true"]'
UNCHECKED_FILTER_CSS_SELECTOR = 'div[aria-checked="false"]'


class FilterScraper:
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def uncheck_filter(self):
        logger.debug("Unchecking filter...")
        filter = self._driver.find_element(By.CSS_SELECTOR, FILTER_CSS_SELECTOR)

        # Remember wait time
        wait_org = self._driver.timeouts.implicit_wait

        # Temporary change the wait time to 0 (there may not be any checked elements, so we dont want to wait for them to appear)
        self._driver.implicitly_wait(0)
        prev_last_el = None
        ACTION_WAIT = 0.1

        while True:
            logger.debug("Finding visible checkboxes...")
            checked_elements = filter.find_elements(
                By.CSS_SELECTOR, CHECKED_FILTER_CSS_SELECTOR
            )
            unchecked_elements = filter.find_elements(
                By.CSS_SELECTOR, UNCHECKED_FILTER_CSS_SELECTOR
            )
            all_elements = checked_elements + unchecked_elements

            logger.debug(f"Found visible checkboxes: {len(all_elements)}")

            actions = ActionChains(self._driver)

            for checked_element in checked_elements:
                # Click to uncheck
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
        self._driver.implicitly_wait(wait_org)
        logger.debug("Filter unchecked")
