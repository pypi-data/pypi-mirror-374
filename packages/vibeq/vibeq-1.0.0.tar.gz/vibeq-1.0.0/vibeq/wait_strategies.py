"""
Advanced Wait Strategies for VibeQ
Selenium-compatible explicit waits with AI enhancement
"""
import time
from typing import Callable, Any, Optional


class TimeoutException(Exception):
    """Timeout exception for wait operations"""
    pass


class WebDriverWait:
    """Selenium-compatible WebDriverWait for VibeQ"""
    
    def __init__(self, vibeq_instance, timeout: float = 10, poll_frequency: float = 0.5):
        self.vibeq = vibeq_instance
        self.timeout = timeout
        self.poll_frequency = poll_frequency
    
    def until(self, method: Callable, message: str = "") -> Any:
        """Wait until method returns a truthy value"""
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            try:
                value = method(self.vibeq)
                if value:
                    return value
            except Exception:
                pass
            
            time.sleep(self.poll_frequency)
        
        raise TimeoutException(f"Timed out after {self.timeout}s: {message}")
    
    def until_not(self, method: Callable, message: str = "") -> Any:
        """Wait until method returns a falsy value"""
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            try:
                value = method(self.vibeq)
                if not value:
                    return True
            except Exception:
                pass
            
            time.sleep(self.poll_frequency)
        
        raise TimeoutException(f"Timed out after {self.timeout}s: {message}")


class ExpectedConditions:
    """Selenium-compatible expected conditions for VibeQ"""
    
    @staticmethod
    def element_to_be_clickable(locator: str):
        """Wait for element to be clickable"""
        def _predicate(vibeq):
            return vibeq.check(f"{locator} is clickable")
        return _predicate
    
    @staticmethod
    def presence_of_element_located(locator: str):
        """Wait for element to be present in DOM"""
        def _predicate(vibeq):
            return vibeq.check(f"{locator} exists")
        return _predicate
    
    @staticmethod
    def visibility_of_element_located(locator: str):
        """Wait for element to be visible"""
        def _predicate(vibeq):
            return vibeq.check(f"{locator} is visible")
        return _predicate
    
    @staticmethod
    def invisibility_of_element_located(locator: str):
        """Wait for element to be invisible"""
        def _predicate(vibeq):
            return not vibeq.check(f"{locator} is visible")
        return _predicate
    
    @staticmethod
    def text_to_be_present_in_element(locator: str, text: str):
        """Wait for text to be present in element"""
        def _predicate(vibeq):
            return vibeq.check(f"text '{text}' is in {locator}")
        return _predicate
    
    @staticmethod
    def title_is(title: str):
        """Wait for page title to be exact value"""
        def _predicate(vibeq):
            return vibeq.get_title() == title
        return _predicate
    
    @staticmethod
    def title_contains(title: str):
        """Wait for page title to contain text"""
        def _predicate(vibeq):
            return title in vibeq.get_title()
        return _predicate
    
    @staticmethod
    def url_contains(url: str):
        """Wait for URL to contain text"""
        def _predicate(vibeq):
            return url in vibeq.get_current_url()
        return _predicate
    
    @staticmethod
    def url_to_be(url: str):
        """Wait for URL to be exact value"""
        def _predicate(vibeq):
            return vibeq.get_current_url() == url
        return _predicate


# Aliases for easy importing
EC = ExpectedConditions
Wait = WebDriverWait
