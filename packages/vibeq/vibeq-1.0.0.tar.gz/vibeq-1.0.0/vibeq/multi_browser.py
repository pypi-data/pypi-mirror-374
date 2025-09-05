"""
Multi-Browser Support
Support Chrome, Firefox, Safari, Edge for enterprise deployment
"""
import logging
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from abc import ABC, abstractmethod
import os
import platform

logger = logging.getLogger(__name__)

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox" 
    SAFARI = "safari"
    EDGE = "edge"
    WEBKIT = "webkit"  # Safari on macOS/iOS

class BrowserCapability(Enum):
    HEADLESS = "headless"
    MOBILE_EMULATION = "mobile_emulation"
    EXTENSIONS = "extensions"
    DOWNLOADS = "downloads"
    PROXY = "proxy"
    SCREENSHOT = "screenshot"
    GEOLOCATION = "geolocation"
    PERMISSIONS = "permissions"

class BrowserAdapter(ABC):
    """Abstract base class for browser adapters"""
    
    def __init__(self, browser_type: BrowserType):
        self.browser_type = browser_type
        self.browser_instance = None
        self.page = None
        self.context = None
    
    @abstractmethod
    def launch(self, **options) -> bool:
        """Launch browser with options"""
        pass
    
    @abstractmethod
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """Navigate to URL"""
        pass
    
    @abstractmethod
    def find_element(self, selector: str, timeout: int = 10):
        """Find element by selector"""
        pass
    
    @abstractmethod
    def click(self, selector: str, timeout: int = 10) -> bool:
        """Click element"""
        pass
    
    @abstractmethod
    def type_text(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Type text in element"""
        pass
    
    @abstractmethod
    def get_text(self, selector: str) -> Optional[str]:
        """Get element text"""
        pass
    
    @abstractmethod
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot"""
        pass
    
    @abstractmethod
    def close(self):
        """Close browser"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[BrowserCapability]:
        """Get supported capabilities"""
        pass

class PlaywrightChromeAdapter(BrowserAdapter):
    """Chrome adapter using Playwright"""
    
    def __init__(self):
        super().__init__(BrowserType.CHROME)
        self.playwright = None
        
    def launch(self, **options) -> bool:
        """Launch Chrome browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            
            launch_options = {
                'headless': options.get('headless', False),
                'slow_mo': options.get('slow_mo', 0),
                'args': options.get('args', [])
            }
            
            # Add Chrome-specific args
            chrome_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            if 'args' in launch_options:
                launch_options['args'].extend(chrome_args)
            else:
                launch_options['args'] = chrome_args
            
            self.browser_instance = self.playwright.chromium.launch(**launch_options)
            
            context_options = {
                'viewport': options.get('viewport', {'width': 1280, 'height': 720}),
                'user_agent': options.get('user_agent')
            }
            
            self.context = self.browser_instance.new_context(**{k: v for k, v in context_options.items() if v is not None})
            self.page = self.context.new_page()
            
            logger.info(f"Chrome launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}")
            return False
    
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """Navigate to URL"""
        try:
            self.page.goto(url, timeout=timeout * 1000)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element(self, selector: str, timeout: int = 10):
        """Find element by selector - supports multiple fallback selectors"""
        try:
            # Handle multiple fallback selectors separated by commas
            if ',' in selector and not selector.startswith('"') and not selector.startswith("'"):
                selectors = [s.strip() for s in selector.split(',')]
                for sel in selectors:
                    try:
                        # Reduce timeout for each fallback to avoid long waits
                        element = self.page.wait_for_selector(sel, timeout=min(timeout * 1000, 3000))
                        if element:
                            logger.debug(f"Found element with fallback selector: {sel}")
                            return element
                    except Exception:
                        continue
                return None
            else:
                # Single selector
                return self.page.wait_for_selector(selector, timeout=timeout * 1000)
        except Exception as e:
            logger.debug(f"Element not found with selector {selector}: {e}")
            return None
    
    def click(self, selector: str, timeout: int = 10) -> bool:
        """Click element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Type text in element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.fill(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to type in {selector}: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """Get element text"""
        try:
            element = self.find_element(selector)
            return element.text_content() if element else None
        except Exception as e:
            logger.debug(f"Failed to get text from {selector}: {e}")
            return None
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot"""
        try:
            if not path:
                import time
                timestamp = int(time.time())
                path = f"screenshot_chrome_{timestamp}.png"
            
            self.page.screenshot(path=path)
            return path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def close(self):
        """Close browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser_instance:
                self.browser_instance.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing Chrome: {e}")
    
    def get_capabilities(self) -> List[BrowserCapability]:
        """Get Chrome capabilities"""
        return [
            BrowserCapability.HEADLESS,
            BrowserCapability.MOBILE_EMULATION,
            BrowserCapability.EXTENSIONS,
            BrowserCapability.DOWNLOADS,
            BrowserCapability.PROXY,
            BrowserCapability.SCREENSHOT,
            BrowserCapability.GEOLOCATION,
            BrowserCapability.PERMISSIONS
        ]

class PlaywrightFirefoxAdapter(BrowserAdapter):
    """Firefox adapter using Playwright"""
    
    def __init__(self):
        super().__init__(BrowserType.FIREFOX)
        self.playwright = None
        
    def launch(self, **options) -> bool:
        """Launch Firefox browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            
            launch_options = {
                'headless': options.get('headless', False),
                'slow_mo': options.get('slow_mo', 0),
                'args': options.get('args', [])
            }
            
            # Add Firefox-specific args
            firefox_args = [
                '--disable-blink-features=AutomationControlled'
            ]
            
            if 'args' in launch_options:
                launch_options['args'].extend(firefox_args)
            else:
                launch_options['args'] = firefox_args
            
            self.browser_instance = self.playwright.firefox.launch(**launch_options)
            
            context_options = {
                'viewport': options.get('viewport', {'width': 1280, 'height': 720}),
                'user_agent': options.get('user_agent')
            }
            
            self.context = self.browser_instance.new_context(**{k: v for k, v in context_options.items() if v is not None})
            self.page = self.context.new_page()
            
            logger.info(f"Firefox launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch Firefox: {e}")
            return False
    
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """Navigate to URL"""
        try:
            self.page.goto(url, timeout=timeout * 1000)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element(self, selector: str, timeout: int = 10):
        """Find element by selector"""
        try:
            return self.page.wait_for_selector(selector, timeout=timeout * 1000)
        except Exception as e:
            logger.debug(f"Element not found with selector {selector}: {e}")
            return None
    
    def click(self, selector: str, timeout: int = 10) -> bool:
        """Click element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Type text in element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.fill(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to type in {selector}: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """Get element text"""
        try:
            element = self.find_element(selector)
            return element.text_content() if element else None
        except Exception as e:
            logger.debug(f"Failed to get text from {selector}: {e}")
            return None
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot"""
        try:
            if not path:
                import time
                timestamp = int(time.time())
                path = f"screenshot_firefox_{timestamp}.png"
            
            self.page.screenshot(path=path)
            return path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def close(self):
        """Close browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser_instance:
                self.browser_instance.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing Firefox: {e}")
    
    def get_capabilities(self) -> List[BrowserCapability]:
        """Get Firefox capabilities"""
        return [
            BrowserCapability.HEADLESS,
            BrowserCapability.DOWNLOADS,
            BrowserCapability.PROXY,
            BrowserCapability.SCREENSHOT,
            BrowserCapability.GEOLOCATION,
            BrowserCapability.PERMISSIONS
        ]

class PlaywrightSafariAdapter(BrowserAdapter):
    """Safari adapter using Playwright WebKit"""
    
    def __init__(self):
        super().__init__(BrowserType.SAFARI)
        self.playwright = None
        
    def launch(self, **options) -> bool:
        """Launch Safari/WebKit browser"""
        try:
            # Safari only available on macOS
            if platform.system() != 'Darwin':
                logger.error("Safari/WebKit only supported on macOS")
                return False
                
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            
            launch_options = {
                'headless': options.get('headless', False),
                'slow_mo': options.get('slow_mo', 0)
            }
            
            self.browser_instance = self.playwright.webkit.launch(**launch_options)
            
            context_options = {
                'viewport': options.get('viewport', {'width': 1280, 'height': 720}),
                'user_agent': options.get('user_agent')
            }
            
            self.context = self.browser_instance.new_context(**{k: v for k, v in context_options.items() if v is not None})
            self.page = self.context.new_page()
            
            logger.info(f"Safari/WebKit launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch Safari/WebKit: {e}")
            return False
    
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """Navigate to URL"""
        try:
            self.page.goto(url, timeout=timeout * 1000)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element(self, selector: str, timeout: int = 10):
        """Find element by selector"""
        try:
            return self.page.wait_for_selector(selector, timeout=timeout * 1000)
        except Exception as e:
            logger.debug(f"Element not found with selector {selector}: {e}")
            return None
    
    def click(self, selector: str, timeout: int = 10) -> bool:
        """Click element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Type text in element"""
        try:
            element = self.find_element(selector, timeout)
            if element:
                element.fill(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to type in {selector}: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """Get element text"""
        try:
            element = self.find_element(selector)
            return element.text_content() if element else None
        except Exception as e:
            logger.debug(f"Failed to get text from {selector}: {e}")
            return None
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot"""
        try:
            if not path:
                import time
                timestamp = int(time.time())
                path = f"screenshot_safari_{timestamp}.png"
            
            self.page.screenshot(path=path)
            return path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def close(self):
        """Close browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser_instance:
                self.browser_instance.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing Safari/WebKit: {e}")
    
    def get_capabilities(self) -> List[BrowserCapability]:
        """Get Safari/WebKit capabilities"""
        return [
            BrowserCapability.SCREENSHOT,
            BrowserCapability.GEOLOCATION,
            BrowserCapability.PERMISSIONS
        ]

class BrowserManager:
    """Universal browser management - multi-browser compatibility"""
    
    def __init__(self):
        self.supported_browsers = {
            BrowserType.CHROME: PlaywrightChromeAdapter,
            BrowserType.FIREFOX: PlaywrightFirefoxAdapter,
            BrowserType.SAFARI: PlaywrightSafariAdapter,
            BrowserType.WEBKIT: PlaywrightSafariAdapter,  # Alias
            BrowserType.EDGE: PlaywrightChromeAdapter  # Edge uses Chromium
        }
        self.current_adapter: Optional[BrowserAdapter] = None
        
    def get_available_browsers(self) -> List[BrowserType]:
        """Get list of available browsers on current platform"""
        available = []
        
        try:
            # Always available with Playwright
            available.extend([BrowserType.CHROME, BrowserType.FIREFOX])
            
            # Safari only on macOS
            if platform.system() == 'Darwin':
                available.extend([BrowserType.SAFARI, BrowserType.WEBKIT])
            
            # Edge available on Windows and some other platforms
            if platform.system() in ['Windows', 'Darwin', 'Linux']:
                available.append(BrowserType.EDGE)
                
        except Exception as e:
            logger.error(f"Error detecting available browsers: {e}")
            
        return available
    
    def launch_browser(self, browser_type: BrowserType = None, **options) -> BrowserAdapter:
        """Launch browser with automatic fallback"""
        
        # Auto-detect best browser if not specified
        if not browser_type:
            browser_type = self._get_best_browser()
        
        try:
            # Create adapter instance
            adapter_class = self.supported_browsers.get(browser_type)
            if not adapter_class:
                raise ValueError(f"Unsupported browser: {browser_type}")
            
            adapter = adapter_class()
            
            # Launch browser
            if adapter.launch(**options):
                self.current_adapter = adapter
                logger.info(f"Successfully launched {browser_type.value}")
                return adapter
            else:
                raise RuntimeError(f"Failed to launch {browser_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to launch {browser_type.value}: {e}")
            
            # Try fallback browser
            fallback = self._get_fallback_browser(browser_type)
            if fallback and fallback != browser_type:
                logger.info(f"Trying fallback browser: {fallback.value}")
                return self.launch_browser(fallback, **options)
            
            raise RuntimeError(f"No browsers available for launch")
    
    def _get_best_browser(self) -> BrowserType:
        """Get best browser for current platform"""
        
        available = self.get_available_browsers()
        
        if not available:
            raise RuntimeError("No browsers available")
        
        # Preference order by platform
        if platform.system() == 'Darwin':  # macOS
            preference = [BrowserType.CHROME, BrowserType.SAFARI, BrowserType.FIREFOX, BrowserType.EDGE]
        elif platform.system() == 'Windows':
            preference = [BrowserType.CHROME, BrowserType.EDGE, BrowserType.FIREFOX]
        else:  # Linux and others
            preference = [BrowserType.CHROME, BrowserType.FIREFOX]
        
        # Return first available from preference list
        for browser in preference:
            if browser in available:
                return browser
        
        # Fallback to first available
        return available[0]
    
    def _get_fallback_browser(self, failed_browser: BrowserType) -> Optional[BrowserType]:
        """Get fallback browser when primary fails"""
        
        available = self.get_available_browsers()
        fallback_map = {
            BrowserType.CHROME: BrowserType.FIREFOX,
            BrowserType.FIREFOX: BrowserType.CHROME,
            BrowserType.SAFARI: BrowserType.CHROME,
            BrowserType.EDGE: BrowserType.CHROME
        }
        
        fallback = fallback_map.get(failed_browser)
        if fallback and fallback in available:
            return fallback
        
        # Return any available browser except the failed one
        for browser in available:
            if browser != failed_browser:
                return browser
        
        return None
    
    def get_browser_info(self, browser_type: BrowserType) -> Dict[str, Any]:
        """Get information about browser capabilities"""
        
        adapter_class = self.supported_browsers.get(browser_type)
        if not adapter_class:
            return {}
        
        # Create temporary adapter to get capabilities
        temp_adapter = adapter_class()
        capabilities = temp_adapter.get_capabilities()
        
        return {
            'type': browser_type.value,
            'available': browser_type in self.get_available_browsers(),
            'capabilities': [cap.value for cap in capabilities],
            'platform_support': self._get_platform_support(browser_type)
        }
    
    def _get_platform_support(self, browser_type: BrowserType) -> Dict[str, bool]:
        """Get platform support for browser"""
        
        support_matrix = {
            BrowserType.CHROME: {'Windows': True, 'macOS': True, 'Linux': True},
            BrowserType.FIREFOX: {'Windows': True, 'macOS': True, 'Linux': True},
            BrowserType.SAFARI: {'Windows': False, 'macOS': True, 'Linux': False},
            BrowserType.EDGE: {'Windows': True, 'macOS': True, 'Linux': True},
            BrowserType.WEBKIT: {'Windows': False, 'macOS': True, 'Linux': False}
        }
        
        return support_matrix.get(browser_type, {})
    
    def get_current_browser(self) -> Optional[BrowserAdapter]:
        """Get current active browser adapter"""
        return self.current_adapter
    
    def close_current_browser(self):
        """Close current browser"""
        if self.current_adapter:
            self.current_adapter.close()
            self.current_adapter = None
            logger.info("Browser closed successfully")

# Convenience function for easy browser creation
def create_browser(browser_type: BrowserType = None, **options) -> BrowserAdapter:
    """Create and launch browser with automatic fallback"""
    manager = BrowserManager()
    return manager.launch_browser(browser_type, **options)
