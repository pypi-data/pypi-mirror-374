"""Enhanced element waiting strategies for VibeQ.

Provides Selenium-style explicit waits and conditions for robust element interaction.
"""

import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class WebDriverWait:
    """Wait for conditions with timeout and polling."""
    
    def __init__(self, browser_adapter, timeout: float = 30, poll_frequency: float = 0.5):
        self.browser_adapter = browser_adapter
        self.timeout = timeout
        self.poll_frequency = poll_frequency
    
    def until(self, condition: Callable[[Any], bool], message: str = "") -> bool:
        """Wait until condition returns True or timeout."""
        start_time = time.time()
        
        while True:
            try:
                if condition(self.browser_adapter):
                    return True
            except Exception as e:
                logger.debug(f"Condition check failed: {e}")
                
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Condition not met within {self.timeout}s: {message}")
                
            time.sleep(self.poll_frequency)


class ExpectedConditions:
    """Common wait conditions for element states."""
    
    @staticmethod
    def element_to_be_visible(selector: str):
        """Wait for element to be visible."""
        def condition(browser):
            return browser.is_visible(selector)
        return condition
    
    @staticmethod
    def element_to_be_clickable(selector: str):
        """Wait for element to be clickable."""
        def condition(browser):
            try:
                if browser.is_visible(selector):
                    # Additional check: element should not be disabled
                    if hasattr(browser, 'page') and browser.page:
                        element = browser.page.query_selector(selector)
                        if element:
                            return not element.is_disabled()
                    return True
            except Exception:
                pass
            return False
        return condition
    
    @staticmethod
    def url_contains(text: str):
        """Wait for URL to contain specific text."""
        def condition(browser):
            current_url = browser.get_page_url()
            return text in current_url
        return condition
    
    @staticmethod
    def title_contains(text: str):
        """Wait for page title to contain specific text."""
        def condition(browser):
            try:
                if hasattr(browser, 'page') and browser.page:
                    title = browser.page.title()
                    return text.lower() in title.lower()
                elif hasattr(browser, '_driver') and browser._driver:
                    title = browser._driver.title
                    return text.lower() in title.lower()
            except Exception:
                pass
            return False
        return condition
