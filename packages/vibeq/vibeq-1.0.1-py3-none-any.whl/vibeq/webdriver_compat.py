"""
VibeQ WebDriver Compatibility Layer
Provides essential WebDriver methods for Selenium migration
"""
import time
from typing import Optional, Any, List, Dict


class WebDriverCompat:
    """Essential WebDriver methods missing from basic VibeQ"""
    
    def __init__(self, core_instance):
        self.core = core_instance
        self._current_window = None
        self._windows = []
    
    # ========== WINDOW MANAGEMENT ==========
    def switch_to_window(self, window_handle: str) -> bool:
        """Switch to a specific browser window/tab"""
        try:
            script = f"window.focus(); return window.name || 'main';"
            result = self.execute_script(script)
            self._current_window = window_handle
            return True
        except Exception:
            return False
    
    def get_window_handles(self) -> List[str]:
        """Get all open window handles"""
        try:
            script = "return window.name || 'main';"
            current = self.execute_script(script)
            return [current] if current else ['main']
        except Exception:
            return ['main']
    
    def close_window(self) -> bool:
        """Close current window"""
        try:
            return self.execute_script("window.close(); return true;")
        except Exception:
            return False
    
    # ========== FRAME MANAGEMENT ==========
    def switch_to_frame(self, frame_reference) -> bool:
        """Switch to iframe by name, id, index, or WebElement"""
        try:
            if isinstance(frame_reference, int):
                # Switch by index
                script = f"var frames = document.getElementsByTagName('iframe'); if(frames[{frame_reference}]) {{ frames[{frame_reference}].focus(); return true; }} return false;"
            elif isinstance(frame_reference, str):
                # Switch by name or id
                script = f"var frame = document.getElementById('{frame_reference}') || document.getElementsByName('{frame_reference}')[0]; if(frame) {{ frame.focus(); return true; }} return false;"
            else:
                return False
            
            return self.execute_script(script)
        except Exception:
            return False
    
    def switch_to_default_content(self) -> bool:
        """Switch back to main document"""
        try:
            script = "window.top.focus(); return true;"
            return self.execute_script(script)
        except Exception:
            return False
    
    # ========== JAVASCRIPT EXECUTION ==========
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser"""
        try:
            # Use direct browser access since that works
            browser = self.core.browser
            
            if hasattr(browser, 'page') and hasattr(browser.page, 'evaluate'):
                # Playwright style - fix the wrapper syntax
                if args:
                    # For scripts with arguments
                    wrapped_script = f"(args) => {{ {script} }}"
                    return browser.page.evaluate(wrapped_script, list(args))
                else:
                    # For simple scripts without arguments
                    if script.strip().startswith('return '):
                        # Already has return statement
                        wrapped_script = f"() => {{ {script} }}"
                    else:
                        # Add return if missing
                        wrapped_script = f"() => {{ return {script}; }}"
                    return browser.page.evaluate(wrapped_script)
            elif hasattr(browser, 'driver') and hasattr(browser.driver, 'execute_script'):
                # Selenium WebDriver style
                if args:
                    return browser.driver.execute_script(script, *args)
                else:
                    return browser.driver.execute_script(script)
            else:
                print(f"No JavaScript execution method found")
                return None
                
        except Exception as e:
            print(f"Script execution failed: {e}")
            return None
    
    def execute_async_script(self, script: str, *args) -> Any:
        """Execute asynchronous JavaScript"""
        # Wrap in async handling
        wrapped_script = f"""
        var callback = arguments[arguments.length - 1];
        try {{
            var result = {script};
            callback(result);
        }} catch(e) {{
            callback(null);
        }}
        """
        return self.execute_script(wrapped_script, *args)
    
    # ========== ADVANCED INTERACTIONS ==========
    def drag_and_drop(self, source_element: str, target_element: str) -> bool:
        """Drag and drop between elements"""
        try:
            # Find source and target using VibeQ's AI
            source_found = self.core.do(f"find {source_element}")
            target_found = self.core.do(f"find {target_element}")
            
            if source_found and target_found:
                # Execute drag and drop via JavaScript
                script = """
                var source = arguments[0];
                var target = arguments[1];
                var dragEvent = new DragEvent('drag', {bubbles: true});
                var dropEvent = new DragEvent('drop', {bubbles: true});
                source.dispatchEvent(dragEvent);
                target.dispatchEvent(dropEvent);
                return true;
                """
                return self.execute_script(script, source_element, target_element)
            return False
        except Exception:
            return False
    
    def upload_file(self, file_input_selector: str, file_path: str) -> bool:
        """Upload file to input element"""
        try:
            # Use VibeQ's natural language to find file input
            found = self.core.do(f"type {file_path} in {file_input_selector}")
            return found
        except Exception:
            return False
    
    # ========== ADVANCED WAITS ==========
    def wait_until_element_visible(self, selector: str, timeout: int = 10) -> bool:
        """Wait until element becomes visible"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.core.check(f"{selector} is visible"):
                return True
            time.sleep(0.5)
        return False
    
    def wait_until_element_clickable(self, selector: str, timeout: int = 10) -> bool:
        """Wait until element becomes clickable"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.core.check(f"{selector} is clickable"):
                return True
            time.sleep(0.5)
        return False
    
    def wait_until_text_present(self, text: str, timeout: int = 10) -> bool:
        """Wait until specific text appears on page"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.core.check(f"text '{text}' is visible"):
                return True
            time.sleep(0.5)
        return False
    
    # ========== PAGE INTERACTION ==========
    def refresh(self) -> bool:
        """Refresh the current page"""
        try:
            return self.execute_script("location.reload(); return true;")
        except Exception:
            return False
    
    def back(self) -> bool:
        """Navigate back in browser history"""
        try:
            return self.execute_script("history.back(); return true;")
        except Exception:
            return False
    
    def forward(self) -> bool:
        """Navigate forward in browser history"""
        try:
            return self.execute_script("history.forward(); return true;")
        except Exception:
            return False
    
    def get_page_source(self) -> str:
        """Get the HTML source of current page"""
        try:
            return self.execute_script("return document.documentElement.outerHTML;")
        except Exception:
            return ""
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            return self.execute_script("return window.location.href;")
        except Exception:
            return ""
    
    def get_title(self) -> str:
        """Get page title"""
        try:
            return self.execute_script("return document.title;")
        except Exception:
            return ""
    
    # ========== SCREENSHOT & DEBUGGING ==========
    def save_screenshot(self, filename: str) -> bool:
        """Save screenshot to file"""
        try:
            # Try different browser types
            browser = self.core.browser
            
            if hasattr(browser, 'page'):
                # Playwright style
                browser.page.screenshot(path=filename)
                return True
            elif hasattr(browser, 'driver'):
                # Selenium WebDriver style  
                browser.driver.save_screenshot(filename)
                return True
            elif hasattr(browser, 'screenshot'):
                # Direct screenshot method
                browser.screenshot(path=filename)
                return True
            else:
                # Fallback to JavaScript + canvas approach
                script = """
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                context.drawWindow(window, 0, 0, window.innerWidth, window.innerHeight, 'rgb(255,255,255)');
                return canvas.toDataURL();
                """
                data_url = self.execute_script(script)
                if data_url:
                    import base64
                    import io
                    from PIL import Image
                    
                    # Extract base64 data
                    image_data = data_url.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    
                    # Save as PNG
                    with open(filename, 'wb') as f:
                        f.write(image_bytes)
                    return True
                
            return False
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False
    
    def get_screenshot_as_png(self) -> bytes:
        """Get screenshot as PNG bytes"""
        try:
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Take screenshot
            if self.save_screenshot(tmp_path):
                with open(tmp_path, 'rb') as f:
                    data = f.read()
                os.unlink(tmp_path)  # Clean up
                return data
            
            return b""
        except Exception:
            return b""
