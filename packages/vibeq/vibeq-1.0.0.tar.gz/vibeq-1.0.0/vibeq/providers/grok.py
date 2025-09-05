"""Production Grok provider adapter for VibeQ."""

import requests
import json
import time
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class GrokProvider:
    """Production Grok (xAI) provider with retry logic and safety."""
    
    def __init__(self, api_key: str, model: str = "grok-beta", max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.base_url = "https://api.x.ai/v1/chat/completions"
        
    def analyze(self, prompt: str) -> str:
        """Analyze prompt with Grok, including retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1
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
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Grok API error: {response.status_code} {response.text}")
                    
            except Exception as e:
                logger.error(f"Grok request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
        raise RuntimeError("Failed to get response from Grok after retries")

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
        return f"""As a web automation expert, generate a CSS selector for this task.

COMMAND: {command}

PAGE HTML:
{page_context[:1000] if page_context else 'No HTML provided'}

Return JSON with selector and confidence:
{{
    "selector": "css-selector-here",
    "confidence": 0.85,
    "reasoning": "explanation"
}}

Guidelines:
- Use specific selectors with fallbacks: "button[class*='buy'], .add-to-cart, [data-action='purchase']"
- Higher confidence for specific attributes (data-*, id, class)
- Lower confidence for generic selectors (button, div, span)
- Consider text content, positioning, and semantic meaning"""

    def _parse_selector_response(self, response: str, command: str) -> Dict:
        """Parse AI response to extract selector and confidence."""
        try:
            # Extract JSON from response
            if '{' in response and '}' in response:
                json_match = re.search(r'\{[^}]*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return {
                        "selector": parsed.get("selector", ""),
                        "confidence": float(parsed.get("confidence", 0.5)),
                        "reasoning": parsed.get("reasoning", "AI generated")
                    }
            
            # Fallback parsing
            selector = self._extract_selector_from_text(response, command)
            return {
                "selector": selector,
                "confidence": 0.5 if selector else 0.0,
                "reasoning": "Text extraction fallback"
            }
            
        except Exception as e:
            return {"selector": None, "confidence": 0.0, "error": f"Parse error: {e}"}

    def _extract_selector_from_text(self, response: str, command: str) -> Optional[str]:
        """Extract CSS selector from text."""
        # Look for CSS selector patterns
        patterns = [
            r'["\'`]([^"\'`]+)["\'`]',
            r'selector:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                if self._is_valid_selector(match.strip()):
                    return match.strip()
        
        return self._generate_fallback_selector(command)

    def _is_valid_selector(self, selector: str) -> bool:
        """Validate CSS selector format."""
        if not selector:
            return False
        try:
            return bool(re.match(r'^[a-zA-Z0-9\[\]#\.\-_:*=\s,>+~()\'"]+$', selector))
        except:
            return False

    def _generate_fallback_selector(self, command: str) -> str:
        """Generate fallback selector based on command."""
        command_lower = command.lower()
        
        if "buy" in command_lower or "purchase" in command_lower:
            return "button[class*='buy'], .add-to-cart, [data-action*='purchase']"
        elif "login" in command_lower:
            return "button[type='submit'], .login-btn, [data-testid*='login']"
        elif "search" in command_lower:
            return "input[type='search'], .search-input, button[class*='search']"
        elif "click" in command_lower:
            return "button, a, [role='button']"
        elif "type" in command_lower:
            return "input, textarea"
        else:
            return "*"
