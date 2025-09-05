"""
Action Executor - Execute actions on web elements
Part of VibeQ's modular automation architecture
"""
import logging
import time
from typing import Optional, Dict, Any
from .command_parser import Intent

logger = logging.getLogger(__name__)

class ActionExecutor:
    """Execute actions on web elements"""
    
    def __init__(self, browser):
        self.browser = browser
    
    def execute(self, intent: Intent, selector: Optional[str] = None) -> bool:
        """Execute an intent with optional selector"""
        logger.info(f"⚡ Executing: {intent.verb} '{intent.target}'")
        
        try:
            if intent.verb == 'navigate':
                return self._navigate(intent.value or intent.target)
            elif intent.verb == 'type':
                return self._type_text(selector, intent.value, intent.target)
            elif intent.verb == 'click':
                return self._click_element(selector, intent.target)
            elif intent.verb == 'wait':
                return self._wait_for(intent.target)
            else:
                logger.warning(f"Unknown verb: {intent.verb}")
                return False
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return False
    
    def _navigate(self, url: str) -> bool:
        """Navigate to a URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                elif '.' in url:
                    url = 'https://' + url
            
            logger.info(f"🌐 Navigating to: {url}")
            self.browser.goto(url)  # Use goto instead of navigate
            time.sleep(2)  # Wait for page load
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def _type_text(self, selector: Optional[str], text: str, field_description: str) -> bool:
        """Type text into an input field"""
        if not selector:
            logger.error(f"No selector provided for typing into: {field_description}")
            return False
        
        if not text:
            logger.warning(f"No text provided for typing")
            return False
        
        try:
            logger.info(f"⌨️ Typing '{text}' into {field_description}")
            
            # Wait for element to be visible
            if hasattr(self.browser.page, 'locator'):
                locator = self.browser.page.locator(selector)
                locator.wait_for(state='visible', timeout=5000)
                locator.click()  # Focus the field
                locator.fill('')  # Clear existing text
                locator.fill(text)
            else:
                # Fallback for other browser types
                self.browser.click(selector)
                self.browser.clear_field(selector)  # Use clear_field
                self.browser.fill(selector, text)
            
            time.sleep(0.3)
            logger.info(f"✅ Successfully typed into {field_description}")
            return True
            
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False
    
    def _click_element(self, selector: Optional[str], element_description: str) -> bool:
        """Click an element"""
        if not selector:
            # Try semantic clicking without selector
            return self._semantic_click(element_description)
        
        try:
            logger.info(f"🖱️ Clicking: {element_description}")
            
            if hasattr(self.browser.page, 'locator'):
                locator = self.browser.page.locator(selector)
                locator.wait_for(state='visible', timeout=5000)
                locator.click()
            else:
                # Fallback for other browser types
                self.browser.click(selector)
            
            time.sleep(0.5)
            logger.info(f"✅ Successfully clicked: {element_description}")
            return True
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def _semantic_click(self, element_description: str) -> bool:
        """Try to click elements using semantic patterns"""
        desc_lower = element_description.lower()
        
        try:
            page = self.browser.page
            
            # Handle add to cart specially
            if 'add to cart' in desc_lower:
                return self._semantic_add_to_cart(element_description)
            
            # Common button text patterns
            button_texts = [
                element_description,  # Try exact text first
                desc_lower,
                *desc_lower.split()  # Try individual words
            ]
            
            for text in button_texts:
                # Try buttons with this text
                buttons = page.locator('button, [role="button"], input[type="submit"]')
                count = buttons.count()
                
                for i in range(count):
                    try:
                        btn = buttons.nth(i)
                        btn_text = (btn.inner_text() or '').lower()
                        
                        if text in btn_text:
                            logger.info(f"🎯 Found semantic match: '{btn_text}' for '{text}'")
                            btn.click()
                            return True
                    except Exception:
                        continue
            
            logger.warning(f"❌ Could not find semantic match for: {element_description}")
            return False
            
        except Exception as e:
            logger.error(f"Semantic click failed: {e}")
            return False
    
    def _semantic_add_to_cart(self, description: str) -> bool:
        """Handle add to cart functionality"""
        try:
            page = self.browser.page
            
            # Extract product name if specified
            product = None
            desc_lower = description.lower()
            if ' for ' in desc_lower:
                product = description.split(' for ', 1)[1].strip()
            
            if product:
                logger.info(f"🛒 Looking for add-to-cart button for: {product}")
                
                # First try: Find specific data-test attribute for the product
                # Convert product name to expected data-test format
                product_slug = product.lower().replace(' ', '-').replace('sauce labs ', 'sauce-labs-')
                data_test_selector = f'[data-test="add-to-cart-{product_slug}"]'
                
                logger.info(f"🎯 Trying specific selector: {data_test_selector}")
                specific_button = page.locator(data_test_selector)
                
                if specific_button.count() > 0:
                    logger.info(f"✅ Found specific add-to-cart button for: {product}")
                    specific_button.first.click()
                    return True
                
                # Second try: Find product containers and look for buttons inside
                containers = page.locator('.inventory_item, .product, .item, [data-product]')
                count = containers.count()
                logger.info(f"🔍 Searching {count} product containers")
                
                for i in range(min(count, 10)):  # Limit search
                    container = containers.nth(i)
                    try:
                        text = (container.inner_text() or '').lower()
                        if product.lower() in text:
                            logger.info(f"🎯 Found matching product container: {product}")
                            # Look for add-to-cart button specifically in this container
                            btn = container.locator('button:has-text("Add to cart"), button[data-test*="add-to-cart"]')
                            if btn.count() > 0:
                                logger.info(f"🎯 Clicking add-to-cart button for: {product}")
                                btn.first.click()
                                return True
                    except Exception as e:
                        logger.debug(f"Container {i} error: {e}")
                        continue
                
                logger.warning(f"❌ Could not find add-to-cart button for specific product: {product}")
                return False
            
            # Fallback: find any add-to-cart button (no specific product)
            logger.info("🛒 Looking for any add-to-cart button")
            buttons = page.locator('button:has-text("Add to cart"), button[data-test*="add-to-cart"]')
            if buttons.count() > 0:
                logger.info("🛒 Clicking first add-to-cart button found")
                buttons.first.click()
                return True
            
            logger.warning("❌ No add-to-cart buttons found")
            return False
            
        except Exception as e:
            logger.error(f"Add to cart failed: {e}")
            return False
    
    def _wait_for(self, condition: str) -> bool:
        """Wait for a condition"""
        # Simple implementation - could be expanded
        logger.info(f"⏳ Waiting for: {condition}")
        time.sleep(2)
        return True
