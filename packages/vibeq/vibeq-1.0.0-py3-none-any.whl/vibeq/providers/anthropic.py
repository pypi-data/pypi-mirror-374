"""Production Anthropic/Claude provider adapter for VibeQ."""

import requests
import json
import time
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Production Anthropic Claude provider with retry logic and safety."""
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    def analyze(self, prompt: str) -> str:
        """Analyze prompt with Claude, including retry logic."""
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "content" in data and len(data["content"]) > 0:
                        return data["content"][0].get("text", "")
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Anthropic API error: {response.status_code} {response.text}")
                    
            except Exception as e:
                logger.error(f"Anthropic request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                    
        raise RuntimeError("Failed to get response from Anthropic after retries")

    def generate_selector(self, command: str, page_context: str) -> Dict:
        """Generate a CSS selector for the given command and page context."""
        prompt = self._create_selector_prompt(command, page_context)
        
        try:
            response = self.analyze(prompt)
            return self._parse_selector_response(response, command)
        except Exception as e:
            return {"selector": None, "confidence": 0.0, "error": str(e)}

    def _create_selector_prompt(self, command: str, page_context: str) -> str:
        """Create a focused prompt for selector generation."""
        return f"""You are a web automation expert specializing in CSS selectors.

TASK: Generate a robust CSS selector for this automation command.
COMMAND: {command}

PAGE CONTEXT (HTML snippet):
{page_context[:1000] if page_context else 'No HTML context available'}

INSTRUCTIONS:
1. Analyze the command to understand the intended action
2. Generate a CSS selector that targets the correct element
3. Provide multiple fallback selectors separated by commas
4. Assign a confidence score (0.0-1.0) based on specificity and reliability

RESPONSE FORMAT - Return valid JSON only:
{{
    "selector": "primary-selector, fallback-selector",
    "confidence": 0.85,
    "reasoning": "Selected button with product name and buy functionality"
}}

SELECTOR EXAMPLES:
- Login button: "button[type='submit'], .login-btn, [data-testid*='login']"
- Search input: "input[type='search'], input[placeholder*='search'], .search-box"
- Product link: "a[href*='product'], [data-product-id], .product-title"
- Add to cart: "button[class*='cart'], button[class*='buy'], .add-to-cart"

Focus on reliability and specificity. Use data attributes and semantic selectors when possible."""

    def _parse_selector_response(self, response: str, command: str) -> Dict:
        """Parse AI response to extract selector and confidence."""
        try:
            # Try to parse as JSON first
            if '{' in response and '}' in response:
                json_match = re.search(r'\{[^}]*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return {
                        "selector": parsed.get("selector", ""),
                        "confidence": float(parsed.get("confidence", 0.5)),
                        "reasoning": parsed.get("reasoning", "AI generated")
                    }
            
            # Fallback: extract selector from text
            selector = self._extract_selector_from_text(response, command)
            return {
                "selector": selector,
                "confidence": 0.6 if selector else 0.0,
                "reasoning": "Extracted from text response"
            }
            
        except Exception as e:
            return {"selector": None, "confidence": 0.0, "error": f"Parse error: {e}"}

    def _extract_selector_from_text(self, response: str, command: str) -> Optional[str]:
        """Extract CSS selector from free-form text response."""
        # Look for quoted selectors
        selector_patterns = [
            r'["\'`]([^"\'`]+)["\'`]',  # Quoted selectors
            r'selector:\s*([^\n]+)',    # selector: pattern
        ]
        
        for pattern in selector_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                selector = match.strip()
                if self._is_valid_selector(selector):
                    return selector
        
        return self._generate_fallback_selector(command)

    def _is_valid_selector(self, selector: str) -> bool:
        """Basic validation of CSS selector."""
        if not selector or len(selector) < 1:
            return False
        
        # Basic CSS selector validation
        try:
            # Check for valid characters and basic structure
            return bool(re.match(r'^[a-zA-Z0-9\[\]#\.\-_:*=\s,>+~()\'"]+$', selector))
        except:
            return False

    def _generate_fallback_selector(self, command: str) -> str:
        """Generate a basic selector based on command keywords."""
        command_lower = command.lower()
        
        if "login" in command_lower:
            return "button[type='submit'], .login-btn, [data-testid*='login']"
        elif "buy" in command_lower or "purchase" in command_lower:
            return "button[class*='buy'], button[class*='add-to-cart'], .buy-now"
        elif "search" in command_lower:
            return "input[type='search'], input[placeholder*='search'], button[class*='search']"
        elif "iphone" in command_lower:
            return "a[href*='iphone'], [data-product*='iphone'], .product[title*='iPhone']"
        elif "click" in command_lower:
            return "button, a, [role='button'], .clickable"
        elif "type" in command_lower:
            return "input, textarea"
        else:
            return "button, a, input"
