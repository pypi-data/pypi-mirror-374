"""Advanced Playwright adapter for VibeQ: Full Selenium/Playwright feature parity

This adapter provides enterprise-grade browser automation with:
- Advanced waits and conditions
- Shadow DOM support  
- iframes handling
- Multiple tabs/windows
- File uploads/downloads
- Network interception
- Mobile simulation
- Screenshots/video
- Drag & drop, hover, scroll
"""

from typing import Optional, Dict, List, Any, Union, Callable
from .browser import BrowserAdapter
import time
import os
from pathlib import Path

try:
    from playwright.sync_api import (
        sync_playwright, Page, Browser, BrowserContext, 
        ElementHandle, Locator, expect, TimeoutError as PlaywrightTimeoutError
    )
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False


class AdvancedWait:
    """Advanced wait conditions for enterprise automation."""
    
    def __init__(self, page: Page, timeout: int = 10000):
        self.page = page
        self.timeout = timeout
    
    def element_visible(self, selector: str) -> bool:
        """Wait until element is visible."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_visible(timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def element_clickable(self, selector: str) -> bool:
        """Wait until element is clickable (visible and enabled)."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_visible(timeout=self.timeout)
            expect(locator).to_be_enabled(timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def text_present(self, selector: str, text: str) -> bool:
        """Wait until element contains specific text."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_contain_text(text, timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def text_changes(self, selector: str, initial_text: str) -> bool:
        """Wait until element text changes from initial value."""
        try:
            locator = self.page.locator(selector)
            expect(locator).not_to_have_text(initial_text, timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def element_count(self, selector: str, count: int) -> bool:
        """Wait until specific number of elements are present."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_have_count(count, timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def url_contains(self, text: str) -> bool:
        """Wait until URL contains specific text."""
        try:
            expect(self.page).to_have_url(f"*{text}*", timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def page_loaded(self) -> bool:
        """Wait until page is fully loaded."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
    
    def custom_condition(self, condition_func: Callable[[], bool]) -> bool:
        """Wait for custom condition function to return True."""
        end_time = time.time() + (self.timeout / 1000)
        while time.time() < end_time:
            try:
                if condition_func():
                    return True
                time.sleep(0.1)
            except Exception:
                pass
        return False


class ShadowDOMHandler:
    """Handle Shadow DOM elements with ease."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def find_in_shadow(self, host_selector: str, shadow_selector: str) -> Optional[ElementHandle]:
        """Find element inside shadow DOM."""
        try:
            # Get the shadow host element
            host = self.page.query_selector(host_selector)
            if not host:
                return None
            
            # Access shadow root and query inside it
            shadow_element = host.evaluate_handle(
                f"(host) => host.shadowRoot.querySelector('{shadow_selector}')"
            )
            return shadow_element.as_element() if shadow_element else None
        except Exception:
            return None
    
    def find_all_in_shadow(self, host_selector: str, shadow_selector: str) -> List[ElementHandle]:
        """Find all elements inside shadow DOM."""
        try:
            host = self.page.query_selector(host_selector)
            if not host:
                return []
            
            elements = host.evaluate(
                f"""(host) => {{
                    const elements = Array.from(host.shadowRoot.querySelectorAll('{shadow_selector}'));
                    return elements;
                }}"""
            )
            return elements or []
        except Exception:
            return []
    
    def click_in_shadow(self, host_selector: str, shadow_selector: str) -> bool:
        """Click element inside shadow DOM."""
        try:
            element = self.find_in_shadow(host_selector, shadow_selector)
            if element:
                element.click()
                return True
            return False
        except Exception:
            return False


class PlaywrightAdapter(BrowserAdapter):
    """Enterprise browser adapter with full Selenium/Playwright feature parity."""
    
    def __init__(self, headless: bool = True, device: str = "desktop", slow_mo: int = 0):
        super().__init__(headless, device)
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._request_mocks = {}
        self._performance_metrics = {}
        
        # Advanced capabilities
        self.wait: Optional[AdvancedWait] = None
        self.shadow: Optional[ShadowDOMHandler] = None
        self._downloads: List[str] = []
        self._tabs: Dict[str, Page] = {}
        self._recording_path: Optional[str] = None

    def launch(self):
        """Launch browser with enterprise features."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Install with: pip install playwright && playwright install")

        self._playwright = sync_playwright().start()
        
        # Launch with advanced options
        self._browser = self._playwright.chromium.launch(
            headless=self.headless, 
            slow_mo=self.slow_mo,
            args=[
                "--disable-web-security",  # For testing
                "--disable-features=VizDisplayCompositor",  # Performance
                "--no-sandbox" if os.environ.get("CI") else ""  # CI environments
            ]
        )
        
        context_options = self._get_context_options()
        self._context = self._browser.new_context(**context_options)
        self.page = self._context.new_page()
        
        # Initialize advanced capabilities
        self.wait = AdvancedWait(self.page)
        self.shadow = ShadowDOMHandler(self.page)
        
        # Enable network interception for API mocking
        self.page.route("**/*", self._handle_route)
        
        # Monitor performance and downloads
        self.page.on("response", self._track_performance)
        self.page.on("download", self._handle_download)
        
        # Enable console logging for debugging
        self.page.on("console", lambda msg: print(f"🌐 Browser Console: {msg.text}"))

    def _get_context_options(self) -> Dict[str, Any]:
        """Get browser context options for different devices and scenarios."""
        opts = {
            "viewport": {"width": 1280, "height": 720},
            "ignore_https_errors": True,  # For testing
            "accept_downloads": True,  # Enable file downloads
            "record_video_dir": "./recordings" if self._recording_path else None,
        }
        
        # Device-specific configurations
        if self.device == "mobile":
            opts.update({
                "viewport": {"width": 375, "height": 667},
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
                "device_scale_factor": 2,
                "is_mobile": True,
                "has_touch": True
            })
        elif self.device == "tablet":
            opts.update({
                "viewport": {"width": 768, "height": 1024},
                "user_agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X)",
                "device_scale_factor": 2,
                "is_mobile": True,
                "has_touch": True
            })
        
        return opts

    def goto(self, url: str):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        return self.page.goto(url)

    def click(self, selector: str):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        
        # Handle multiple elements gracefully - click the first visible one
        try:
            # First try to find if there are multiple elements
            locator = self.page.locator(selector)
            count = locator.count()
            
            if count == 0:
                raise Exception(f"No elements found for selector: {selector}")
            elif count == 1:
                # Single element - use regular click
                return self.page.click(selector)
            else:
                # Multiple elements - click the first visible one
                print(f"⚠️ Multiple elements found ({count}), clicking first visible one")
                for i in range(count):
                    try:
                        element = locator.nth(i)
                        if element.is_visible():
                            element.click()
                            print(f"✅ Clicked element {i+1}/{count}")
                            return
                    except Exception as e:
                        print(f"Element {i+1} not clickable: {e}")
                        continue
                
                # If no visible elements found, try clicking the first one anyway
                locator.first.click()
                return
                        
        except Exception as e:
            # Fallback to original method if locator approach fails
            print(f"Locator approach failed, using original click: {e}")
            return self.page.click(selector)
    
    def type(self, selector: str, text: str):
        """Type text in an input field."""
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        return self.page.fill(selector, text)
    
    def is_element_present(self, selector: str) -> bool:
        """Check if element exists on the page."""
        if not self.page:
            return False
        try:
            element = self.page.query_selector(selector)
            return element is not None
        except Exception:
            return False
    
    def clear_field(self, selector: str):
        """Clear an input field."""
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        try:
            self.page.fill(selector, "")
        except Exception:
            # Fallback: select all and delete
            try:
                element = self.page.locator(selector)
                element.click()
                element.press("Control+a")
                element.press("Delete")
            except Exception:
                pass
    
    def press_key(self, selector: str, key: str):
        """Press a key on an element."""
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        element = self.page.locator(selector)
        element.press(key)

    def query_selector(self, selector: str):
        """Return the element handle if selector matches, else None"""
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        try:
            return self.page.query_selector(selector)
        except Exception:
            return None

    def is_visible(self, selector: str) -> bool:
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        try:
            el = self.page.query_selector(selector)
            return el is not None and el.is_visible()
        except Exception:
            return False

    def click_by_text(self, text: str):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        # prefer built-in text selector
        sel = f"text=\"{text}\""
        return self.page.click(sel)

    def get_page_url(self) -> str:
        if not self.page:
            return ""
        try:
            return self.page.url
        except Exception:
            return ""

    def get_page_content(self) -> str:
        if not self.page:
            return ""
        try:
            return self.page.content()
        except Exception:
            return ""

    def derive_element_key(self, value: str) -> str:
        """Try to derive a stable element key using page context and element attributes.

        Enhanced strategy with attribute prioritization for enterprise reliability.
        Priority: data-testid > id > name > aria-label > class > text content
        """
        if not self.page:
            return (value or "unknown").strip().lower()

        try:
            text = value.strip()
            
            # Priority-based selector search
            selectors_to_try = [
                f'[data-testid*="{text.lower()}"]',
                f'[data-test*="{text.lower()}"]', 
                f'#{text.lower().replace(" ", "-")}',
                f'[name*="{text.lower()}"]',
                f'[aria-label*="{text}"]',
                f'[placeholder*="{text}"]',
                f'text="{text}"'
            ]
            
            best_attrs = []
            for selector in selectors_to_try:
                try:
                    handle = self.page.query_selector(selector)
                    if handle:
                        # Extract multiple stable attributes
                        for attr in ("data-testid", "data-test", "id", "name", "aria-label", "class"):
                            try:
                                val = handle.get_attribute(attr)
                                if val and len(val) < 50:  # Reasonable length
                                    best_attrs.append(f"{attr}={val}")
                            except Exception:
                                continue
                        
                        # Found element, break with best attributes
                        if best_attrs:
                            break
                except Exception:
                    continue

            # Build composite key
            url = self.get_page_url() or "unknown"
            page_key = url.split('/')[-1] or url.split('//')[-1]
            
            if best_attrs:
                attr_key = "|".join(best_attrs[:3])  # Top 3 attributes
                return f"{page_key}::{attr_key}".strip().lower()
            else:
                return f"{page_key}::{text}".strip().lower()

        except Exception:
            return (value or "unknown").strip().lower()

    def mock_api_response(self, url_pattern: str, response_data: dict):
        """Mock API responses for testing."""
        self._request_mocks[url_pattern] = response_data
    
    def _handle_route(self, route):
        """Handle network interception for API mocking."""
        url = route.request.url
        
        # Check if this request should be mocked
        for pattern, mock_data in self._request_mocks.items():
            if pattern in url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=str(mock_data) if isinstance(mock_data, str) else str(mock_data)
                )
                return
                
        # Continue with real request
        route.continue_()
    
    def _track_performance(self, response):
        """Track page load performance."""
        url = response.url
        timing = response.request.timing
        
        if timing:
            self._performance_metrics[url] = {
                "response_time": timing.get("responseEnd", 0) - timing.get("requestStart", 0),
                "dns_time": timing.get("domainLookupEnd", 0) - timing.get("domainLookupStart", 0),
                "connect_time": timing.get("connectEnd", 0) - timing.get("connectStart", 0),
                "status": response.status,
                "timestamp": time.time()
            }
    
    def get_performance_metrics(self) -> dict:
        """Get page load performance data."""
        return self._performance_metrics.copy()
    
    def clear_performance_metrics(self):
        """Clear performance tracking data."""
        self._performance_metrics.clear()

    def wait_for_element(self, selector: str, timeout: int = 30) -> bool:
        """Wait for element with timeout."""
        from .wait import WebDriverWait, ExpectedConditions
        wait = WebDriverWait(self, timeout)
        try:
            wait.until(ExpectedConditions.element_to_be_visible(selector))
            return True
        except TimeoutError:
            return False

    def fill(self, selector: str, value: str):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        return self.page.fill(selector, value)

    def wait_for_load(self):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        self.page.wait_for_load_state("networkidle")

    def screenshot(self, path: str):
        if not self.page:
            raise RuntimeError("No page available; call launch() first")
        return self.page.screenshot(path=path)

    # ==================== ADVANCED BROWSER METHODS ====================
    # Full Selenium/Playwright feature parity for enterprise automation
    
    def wait_for_element_visible(self, selector: str, timeout: int = 10000) -> bool:
        """Wait until element becomes visible."""
        return self.wait.element_visible(selector) if self.wait else False
    
    def wait_for_element_clickable(self, selector: str, timeout: int = 10000) -> bool:
        """Wait until element is clickable (visible and enabled)."""
        return self.wait.element_clickable(selector) if self.wait else False
    
    def wait_for_text(self, selector: str, text: str, timeout: int = 10000) -> bool:
        """Wait until element contains specific text."""
        return self.wait.text_present(selector, text) if self.wait else False
    
    def wait_for_url_contains(self, text: str, timeout: int = 10000) -> bool:
        """Wait until URL contains specific text."""
        return self.wait.url_contains(text) if self.wait else False
    
    def wait_for_page_load(self, timeout: int = 30000) -> bool:
        """Wait until page is fully loaded (network idle)."""
        return self.wait.page_loaded() if self.wait else False
    
    def hover(self, selector: str) -> bool:
        """Hover over an element."""
        try:
            if not self.page:
                return False
            self.page.locator(selector).hover()
            return True
        except Exception:
            return False
    
    def drag_and_drop(self, source_selector: str, target_selector: str) -> bool:
        """Drag element from source to target."""
        try:
            if not self.page:
                return False
            self.page.locator(source_selector).drag_to(self.page.locator(target_selector))
            return True
        except Exception:
            return False
    
    def scroll_to_element(self, selector: str) -> bool:
        """Scroll element into view."""
        try:
            if not self.page:
                return False
            self.page.locator(selector).scroll_into_view_if_needed()
            return True
        except Exception:
            return False
    
    def scroll_page(self, direction: str = "down", pixels: int = 500) -> bool:
        """Scroll page in specified direction."""
        try:
            if not self.page:
                return False
            
            if direction.lower() == "down":
                self.page.evaluate(f"window.scrollBy(0, {pixels})")
            elif direction.lower() == "up":
                self.page.evaluate(f"window.scrollBy(0, -{pixels})")
            elif direction.lower() == "left":
                self.page.evaluate(f"window.scrollBy(-{pixels}, 0)")
            elif direction.lower() == "right":
                self.page.evaluate(f"window.scrollBy({pixels}, 0)")
            return True
        except Exception:
            return False
    
    def upload_file(self, selector: str, file_path: str) -> bool:
        """Upload file to file input element."""
        try:
            if not self.page or not os.path.exists(file_path):
                return False
            self.page.locator(selector).set_input_files(file_path)
            return True
        except Exception:
            return False
    
    def download_file(self, trigger_selector: str, download_path: str = "./downloads") -> Optional[str]:
        """Trigger download and return downloaded file path."""
        try:
            if not self.page:
                return None
            
            # Ensure download directory exists
            Path(download_path).mkdir(exist_ok=True)
            
            with self.page.expect_download() as download_info:
                self.page.locator(trigger_selector).click()
            
            download = download_info.value
            file_path = os.path.join(download_path, download.suggested_filename)
            download.save_as(file_path)
            self._downloads.append(file_path)
            return file_path
        except Exception:
            return None
    
    def switch_to_iframe(self, iframe_selector: str) -> bool:
        """Switch context to iframe."""
        try:
            if not self.page:
                return False
            
            iframe_element = self.page.query_selector(iframe_selector)
            if iframe_element:
                frame = iframe_element.content_frame()
                if frame:
                    # Store original page and switch to frame
                    self._original_page = self.page
                    self.page = frame
                    return True
            return False
        except Exception:
            return False
    
    def switch_to_default_content(self) -> bool:
        """Switch back to main page from iframe."""
        try:
            if hasattr(self, '_original_page') and self._original_page:
                self.page = self._original_page
                delattr(self, '_original_page')
                return True
            return False
        except Exception:
            return False
    
    def open_new_tab(self, url: str = None) -> str:
        """Open new tab and return tab ID."""
        try:
            if not self._context:
                return ""
            
            new_page = self._context.new_page()
            tab_id = f"tab_{len(self._tabs) + 1}"
            self._tabs[tab_id] = new_page
            
            if url:
                new_page.goto(url)
            
            return tab_id
        except Exception:
            return ""
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """Switch to specific tab."""
        try:
            if tab_id in self._tabs:
                self.page = self._tabs[tab_id]
                # Update wait and shadow handlers for new page
                self.wait = AdvancedWait(self.page) if self.page else None
                self.shadow = ShadowDOMHandler(self.page) if self.page else None
                return True
            return False
        except Exception:
            return False
    
    def close_tab(self, tab_id: str) -> bool:
        """Close specific tab."""
        try:
            if tab_id in self._tabs:
                self._tabs[tab_id].close()
                del self._tabs[tab_id]
                return True
            return False
        except Exception:
            return False
    
    def get_all_tabs(self) -> List[str]:
        """Get list of all tab IDs."""
        return list(self._tabs.keys())
    
    def execute_javascript(self, script: str, *args) -> Any:
        """Execute JavaScript in browser."""
        try:
            if not self.page:
                return None
            return self.page.evaluate(script, *args)
        except Exception:
            return None
    
    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get element attribute value."""
        try:
            if not self.page:
                return None
            return self.page.locator(selector).get_attribute(attribute)
        except Exception:
            return None
    
    def get_element_text(self, selector: str) -> Optional[str]:
        """Get element text content."""
        try:
            if not self.page:
                return None
            return self.page.locator(selector).text_content()
        except Exception:
            return None
    
    def get_element_count(self, selector: str) -> int:
        """Get count of elements matching selector."""
        try:
            if not self.page:
                return 0
            return self.page.locator(selector).count()
        except Exception:
            return 0
    
    def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        try:
            if not self.page:
                return False
            return self.page.locator(selector).is_visible()
        except Exception:
            return False
    
    def is_element_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        try:
            if not self.page:
                return False
            return self.page.locator(selector).is_enabled()
        except Exception:
            return False
    
    def take_element_screenshot(self, selector: str, path: str = None) -> Optional[bytes]:
        """Take screenshot of specific element."""
        try:
            if not self.page:
                return None
            return self.page.locator(selector).screenshot(path=path)
        except Exception:
            return None
    
    def start_video_recording(self, path: str = "./recordings") -> bool:
        """Start video recording (must be set before launch)."""
        self._recording_path = path
        return True
    
    def stop_video_recording(self) -> Optional[str]:
        """Stop video recording and return path."""
        try:
            if self.page and hasattr(self.page, 'video'):
                video_path = self.page.video.path()
                return video_path
            return None
        except Exception:
            return None
    
    def mock_api_response(self, url_pattern: str, response_data: Dict) -> None:
        """Mock API response for testing."""
        self._request_mocks[url_pattern] = response_data
    
    def clear_api_mocks(self) -> None:
        """Clear all API mocks."""
        self._request_mocks.clear()
    
    def get_network_logs(self) -> List[Dict]:
        """Get network request logs."""
        return list(self._performance_metrics.values())
    
    def simulate_device(self, device_name: str) -> bool:
        """Simulate specific device (iPhone, iPad, etc.)."""
        devices = {
            "iPhone 12": {"width": 390, "height": 844, "mobile": True, "touch": True},
            "iPhone SE": {"width": 375, "height": 667, "mobile": True, "touch": True},
            "iPad": {"width": 768, "height": 1024, "mobile": True, "touch": True},
            "Desktop": {"width": 1280, "height": 720, "mobile": False, "touch": False},
        }
        
        if device_name not in devices:
            return False
        
        try:
            if self.page:
                device_config = devices[device_name]
                self.page.set_viewport_size(device_config["width"], device_config["height"])
                return True
            return False
        except Exception:
            return False
    
    def get_downloads(self) -> List[str]:
        """Get list of downloaded files."""
        return self._downloads.copy()
    
    def clear_downloads(self) -> None:
        """Clear download history."""
        self._downloads.clear()
    
    def _handle_download(self, download) -> None:
        """Handle download events."""
        self._downloads.append(download.suggested_filename)
    
    # Shadow DOM methods (using the ShadowDOMHandler)
    def find_in_shadow_dom(self, host_selector: str, shadow_selector: str) -> Optional[ElementHandle]:
        """Find element inside Shadow DOM."""
        return self.shadow.find_in_shadow(host_selector, shadow_selector) if self.shadow else None
    
    def click_in_shadow_dom(self, host_selector: str, shadow_selector: str) -> bool:
        """Click element inside Shadow DOM."""
        return self.shadow.click_in_shadow(host_selector, shadow_selector) if self.shadow else False

    def close(self):
        """Close browser and cleanup resources."""
        try:
            # Close all additional tabs
            for tab in self._tabs.values():
                try:
                    tab.close()
                except Exception:
                    pass
            
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
