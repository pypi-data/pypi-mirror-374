"""Abstract browser adapter interface for VibeQ.

This defines the contract that all browser adapters (Playwright, BiDi, etc.) 
must implement to work with VibeQ core.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BrowserAdapter(ABC):
    """Abstract base class for all browser adapters."""
    
    def __init__(self, headless: bool = True, device: str = "desktop"):
        self.headless = headless
        self.device = device
    
    @abstractmethod
    def launch(self):
        """Initialize and start the browser session."""
        pass
    
    @abstractmethod 
    def goto(self, url: str):
        """Navigate to the given URL."""
        pass
    
    @abstractmethod
    def click(self, selector: str):
        """Click element matching the selector."""
        pass
    
    @abstractmethod
    def click_by_text(self, text: str):
        """Click element containing the given text."""
        pass
    
    @abstractmethod
    def fill(self, selector: str, value: str):
        """Fill input field matching selector with value."""
        pass
    
    @abstractmethod
    def is_visible(self, selector: str) -> bool:
        """Check if element matching selector is visible."""
        pass
    
    @abstractmethod
    def get_page_content(self) -> str:
        """Get current page HTML content."""
        pass
    
    @abstractmethod
    def get_page_url(self) -> str:
        """Get current page URL."""
        pass
    
    @abstractmethod
    def derive_element_key(self, value: str) -> str:
        """Derive stable element key for healing purposes."""
        pass
    
    @abstractmethod
    def wait_for_load(self):
        """Wait for page to finish loading."""
        pass
    
    @abstractmethod
    def screenshot(self, path: str):
        """Take screenshot and save to path."""
        pass
    
    @abstractmethod
    def close(self):
        """Close browser and cleanup resources."""
        pass

def get_browser_adapter(browser_type: str = "playwright", headless: bool = True):
    """Factory function to get the appropriate browser adapter"""
    if browser_type.lower() == "playwright":
        from .browser_playwright import PlaywrightAdapter
        return PlaywrightAdapter(headless=headless)
    else:
        raise ValueError(f"Unsupported browser type: {browser_type}")
