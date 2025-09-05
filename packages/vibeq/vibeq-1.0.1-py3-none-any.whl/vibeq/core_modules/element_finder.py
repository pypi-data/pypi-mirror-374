"""
Element Finder - AI-native element discovery and selection
Part of VibeQ's intelligent automation engine
"""
import logging
import time
from typing import Optional, List, Dict, Any
from .command_parser import Intent

logger = logging.getLogger(__name__)

class ElementFinder:
    """Find elements on web pages using AI-native approaches"""
    
    def __init__(self, browser, intelligence=None):
        self.browser = browser
        self.intelligence = intelligence
    
    def find_for_intent(self, intent: Intent) -> Optional[str]:
        """Find the best selector for a given intent"""
        logger.info(f"🔍 Finding element for: {intent.verb} '{intent.target}'")
        
        # Try AI intelligence first if available
        if self.intelligence:
            page_context = self._get_page_context()
            command = f"{intent.verb} {intent.target}"
            if intent.value:
                command += f" {intent.value}"
                
            selector, confidence, source = self.intelligence.find_selector(command, page_context)
            
            if selector and confidence > 0.3:
                logger.info(f"🎯 AI found selector: '{selector}' (confidence: {confidence:.2f})")
                return selector
            else:
                logger.warning(f"⚠️ AI confidence low ({confidence:.2f}) for: '{command}'")
        
        # Fallback to semantic approaches
        return self._semantic_find(intent)
    
    def _semantic_find(self, intent: Intent) -> Optional[str]:
        """Use semantic patterns to find elements"""
        if intent.verb == 'type':
            return self._find_input_field(intent.target)
        elif intent.verb == 'click':
            return self._find_clickable_element(intent.target)
        elif intent.verb == 'navigate':
            return None  # Navigation doesn't need selectors
        
        return None
    
    def _find_input_field(self, field_description: str) -> Optional[str]:
        """Find input fields by description"""
        field_lower = field_description.lower()
        
        # Common input field patterns
        patterns = {
            'username': ['input[name*="user"]', 'input[id*="user"]', 'input[placeholder*="user"]'],
            'password': ['input[type="password"]', 'input[name*="pass"]', 'input[id*="pass"]'],
            'email': ['input[type="email"]', 'input[name*="email"]', 'input[id*="email"]'],
            'first name': ['input[name*="first"]', 'input[id*="first"]'],
            'last name': ['input[name*="last"]', 'input[id*="last"]'],
            'postal code': ['input[name*="postal"]', 'input[name*="zip"]'],
            'phone': ['input[type="tel"]', 'input[name*="phone"]'],
            'search': ['input[type="search"]', 'input[placeholder*="search"]']
        }
        
        # Find matching pattern
        for field_type, selectors in patterns.items():
            if field_type in field_lower:
                return selectors[0]  # Return first selector
        
        # Generic input fallback
        return 'input[type="text"], input:not([type]), textarea'
    
    def _find_clickable_element(self, element_description: str) -> Optional[str]:
        """Find clickable elements by description"""
        desc_lower = element_description.lower()
        
        # Handle add to cart specially - return None to force semantic handling
        if 'add to cart' in desc_lower or 'add to bag' in desc_lower:
            return None  # Let semantic handler deal with this
        
        # Button patterns
        if any(word in desc_lower for word in ['button', 'btn', 'click', 'submit']):
            return 'button, input[type="submit"], [role="button"]'
        
        # Link patterns  
        if any(word in desc_lower for word in ['link', 'navigate']):
            return 'a[href]'
        
        # Cart icon patterns (not add-to-cart buttons)
        if 'cart' in desc_lower and 'add' not in desc_lower:
            return '[data-test="shopping-cart-link"], .shopping_cart_link'
        
        # Login patterns
        if 'login' in desc_lower:
            return '[data-test="login-button"], input[value="Login"], button:has-text("Login")'
        
        # Checkout patterns
        if 'checkout' in desc_lower:
            return '[data-test="checkout"], button:has-text("Checkout")'
        
        # Continue patterns
        if 'continue' in desc_lower:
            return '[data-test="continue"], button:has-text("Continue")'
        
        # Finish patterns
        if 'finish' in desc_lower:
            return '[data-test="finish"], button:has-text("Finish")'
        
        # Generic clickable
        return 'button, a, [role="button"], [onclick], input[type="submit"]'
    
    def _get_page_context(self) -> str:
        """Get current page context for AI"""
        try:
            if hasattr(self.browser, 'page') and self.browser.page:
                title = self.browser.page.title()
                url = self.browser.page.url
                return f"Page: {title} | URL: {url}"
        except Exception:
            pass
        return "Unknown page"
