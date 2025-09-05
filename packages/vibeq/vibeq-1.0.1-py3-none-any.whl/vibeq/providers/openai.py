"""Lightweight OpenAI provider adapter (requests-based)

This is intentionally tiny; for production use, swap in the official `openai` SDK and add retries.
"""

import os
import requests
import json
import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class OpenAIProvider:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None):
        if not api_key:
            raise ValueError("OpenAI API key required")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        
        # Remove trailing slash for consistency
        self.base_url = self.base_url.rstrip('/')

    def analyze(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
        r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    def generate_selector(self, command: str, page_context: str) -> Dict:
        """
        Universal AI intelligence - works on ANY website
        Revolutionary approach: Understand the page like a human would
        """
        try:
            # Build universal intelligence prompt
            prompt = f"""
You are a UNIVERSAL web automation AI that understands websites like a human tester.

LIVE PAGE CONTENT:
{page_context}

USER WANTS TO: "{command}"

Your mission: Analyze the ACTUAL page content above and find the best elements for this action.

UNIVERSAL INTELLIGENCE APPROACH:
1. READ the page content - what elements actually exist right now?
2. UNDERSTAND user intent - what would a human do to accomplish this?
3. MATCH intent to visible elements using natural language understanding
4. GENERATE robust selectors that will work reliably

HUMAN-LIKE ANALYSIS:
• For "login" → Look for Login text, Sign In buttons, account links
• For "search" → Look for search boxes, input fields with search context  
• For "mobile/phone" → Look for INPUT elements with type='text', maxlength='10', or classes that suggest mobile input (like r4vIwl, phone-input, mobile-field)
• For "click X" → Find buttons/links with text X or similar meaning
• For "fill/type X" → Find input fields that would accept this data type

**MOBILE INPUT DETECTION**: Look for inputs with:
- maxlength="10" (Indian mobile numbers)
- type="text" with no placeholder or mobile-related placeholder
- CSS classes that contain mobile/phone patterns
- First visible text input in a login form

🚫 DO NOT use site-wide search boxes for phone/mobile commands. Avoid any input whose placeholder/name/id/class suggests "search". Prefer inputs within or near text like "Email/Mobile" and near a "Request OTP" button.

UNIVERSAL SELECTOR STRATEGIES (in priority order):
1. **EXACT CSS CLASSES**: Use the actual classes you see in the page content (e.g., input.r4vIwl, .BV+Dqf)
2. **TEXT-BASED**: :has-text('exact text'), :has-text('partial') for buttons and links
3. **SEMANTIC**: input[type='tel'], input[type='email'], button[type='submit']
4. **ATTRIBUTES**: [placeholder*='keyword'], [aria-label*='keyword'], [maxlength='10']
5. **COMBINATIONS**: Combine class + type + attributes for precision

**CRITICAL**: Always prioritize the ACTUAL CSS classes and IDs you see in the page content!
If you see INPUT with class="r4vIwl BV+Dqf", use: input.r4vIwl.BV\\+Dqf or input[class*='r4vIwl']
If you see BUTTON with class="_2KpZ6l _279oD5", use: button._2KpZ6l._279oD5 or button[class*='_2KpZ6l']

GENERATE 3-5 fallback selectors using comma separation, starting with the most specific:
- First: Exact classes from page content
- Second: Partial class matching  
- Third: Semantic attributes
- Fourth: Generic fallback

ANALYZE the page content and respond in JSON:
{{
    "selector": "best-selector, fallback1, fallback2, fallback3",
    "confidence": 0.85,
    "reasoning": "Found [specific elements] in page content that match user intent",
    "element_type": "button|input|link|generic"
}}

BE SMART - work with what actually exists on this page!"""

            # Use the requests-based API call
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a universal web automation expert who can intelligently understand any website structure and user intent."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
                "temperature": 0.1
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} {response.text}")
                return self._generate_universal_fallback(command)
                
            response_data = response.json()
            content = response_data['choices'][0]['message']['content'].strip()
            
            # Parse JSON response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    
                    # Validate and clean up the result
                    selector = result.get('selector', '').strip()
                    confidence = float(result.get('confidence', 0.6))
                    reasoning = result.get('reasoning', 'Universal AI analysis')
                    element_type = result.get('element_type', 'generic')
                    
                    # Ensure confidence is in valid range
                    confidence = max(0.0, min(1.0, confidence))
                    
                    logger.info(f"Universal AI found: {selector} (confidence: {confidence})")
                    
                    return {
                        "selector": selector,
                        "confidence": confidence,
                        "reasoning": f"Universal AI: {reasoning}",
                        "element_type": element_type,
                        "source": "universal_ai"
                    }
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback parsing if JSON fails
            lines = content.split('\n')
            selector = None
            confidence = 0.6
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['selector:', 'element:', 'target:']):
                    selector = line.split(':', 1)[1].strip().strip('"\'')
                    break
            
            if selector:
                return {
                    "selector": selector,
                    "confidence": confidence,
                    "reasoning": "Universal AI (fallback parsing)",
                    "element_type": "generic",
                    "source": "universal_ai_fallback"
                }
            
            # Last resort - generate intelligent fallback
            return self._generate_universal_fallback(command)
            
        except Exception as e:
            logger.error(f"Universal AI error: {e}")
            return self._generate_universal_fallback(command)
    
    def _analyze_page_dom(self, page_context: str) -> Dict:
        """Analyze the current page DOM structure to understand available elements."""
        # This would ideally get real DOM data from the browser
        # For now, we'll simulate intelligent page understanding
        return {
            "page_type": "e-commerce" if "flipkart" in page_context.lower() else "general",
            "likely_elements": self._predict_page_elements(page_context)
        }
    
    def _predict_page_elements(self, page_context: str) -> List[str]:
        """Predict what elements are likely present on this type of page."""
        context_lower = page_context.lower()
        
        if "flipkart" in context_lower:
            return [
                "Login button: a._1_3w1N, button[data-testid='login-btn'], .zWJnce",
                "Search box: input._3704LK, input[name='q'], input[placeholder*='Search']",
                "Mobile input: input.r4vIwl, input[type='text'][maxlength='10']",
                "OTP button: button._2KpZ6l, button[type='submit'], button:has-text('Request OTP')",
                "Add to cart: button._2KpZ6l, button:has-text('ADD TO CART')"
            ]
        elif "amazon" in context_lower:
            return [
                "Login: a#nav-link-accountList, .nav-signin-tt",
                "Search: input#twotabsearchtextbox, input[name='field-keywords']",
                "Add to cart: input#add-to-cart-button, button[name='submit.add-to-cart']"
            ]
        else:
            return [
                "Generic login: button:has-text('Login'), a:has-text('Sign In')",
                "Generic search: input[type='search'], input[placeholder*='search' i]",
                "Generic button: button, input[type='submit']"
            ]

    def _create_intelligent_selector_prompt(self, command: str, page_context: str, dom_analysis: Dict) -> str:
        """Create an intelligent prompt that analyzes the page like a human tester would."""
        
        page_type = dom_analysis.get("page_type", "general")
        likely_elements = dom_analysis.get("likely_elements", [])
        
        return f"""You are an expert web automation specialist with the intelligence of advanced testing tools. 
Your mission: Find elements on web pages as naturally as a human QA tester would.

COMMAND: "{command}"
PAGE CONTEXT: {page_context}
PAGE TYPE: {page_type}

🧠 INTELLIGENT ANALYSIS:
Based on the page context, these elements are likely present:
{chr(10).join('• ' + elem for elem in likely_elements)}

Think like a smart QA engineer:
1. What is the USER trying to do? 
2. What TYPE of element would accomplish this?
3. What VISUAL CUES would a human look for?
4. What are the MOST RELIABLE selectors for this site?

🎯 COMMAND ANALYSIS:
{self._analyze_command_intent(command)}

🔍 SELECTOR STRATEGY (in order of reliability):
1. TEXT-BASED: Elements with exact visible text (highest confidence)
2. DATA ATTRIBUTES: data-testid, data-automation-id (very reliable)  
3. SEMANTIC HTML: Proper input types, button elements (reliable)
4. STABLE CLASSES: Site-specific known selectors (good)
5. VISUAL SELECTORS: Placeholder text, labels (moderate)

For FLIPKART specifically, use these proven selectors:
• Login: a._1_3w1N, ._3NFO0d, a:has-text('Login')
• Search: input._3704LK, input[name='q'], input[placeholder*='Search']
• Mobile Input: input.r4vIwl, input[maxlength='10'], input[type='text']:first-of-type, input[placeholder*='Enter Mobile'], .r4vIwl
• OTP Request: button._2KpZ6l, button:has-text('Request OTP'), button[type='submit']
• Buttons: button._2KpZ6l, button[type='submit']

For ANY SITE, prioritize:
• :has-text() for visible text matching
• [placeholder*='keyword'] for inputs
• button:has-text('text') for buttons
• Multiple fallbacks separated by commas

Generate 3-5 fallback selectors, ordered by reliability.

Respond in JSON:
{{
    "selector": "primary-selector, fallback1, fallback2, fallback3",
    "confidence": 0.85,
    "reasoning": "Human-readable explanation of why these selectors work",
    "element_type": "button|input|link|generic",
    "strategies": ["text-based", "semantic", "data-attrs"]
}}

Make it bulletproof like a human tester who knows the site!"""
    
    def _analyze_command_intent(self, command: str) -> str:
        """Analyze what the user is trying to accomplish."""
        command_lower = command.lower()
        
        if "login" in command_lower:
            return "🔐 USER INTENT: Access account → LOOK FOR: Login button/link, likely in top navigation"
        elif "search" in command_lower:
            return "🔍 USER INTENT: Find products → LOOK FOR: Search input box, typically prominent on page"
        elif "mobile" in command_lower or "phone" in command_lower or "fill mobile" in command_lower:
            return "📱 USER INTENT: Enter phone number → LOOK FOR: First visible text input on login page, usually has maxlength=10 for Indian mobile numbers"
        elif "otp" in command_lower:
            return "📨 USER INTENT: Request/verify OTP → LOOK FOR: Button to trigger OTP or verify code"
        elif "cart" in command_lower:
            return "🛒 USER INTENT: Add item to shopping cart → LOOK FOR: 'Add to Cart' button on product page"
        elif "navigate" in command_lower or "go to" in command_lower:
            return "🌐 USER INTENT: Navigate to URL → ACTION: Direct browser navigation, no element needed"
        else:
            return f"🤔 USER INTENT: Generic action → ANALYZE: '{command}' for action type and target"

    def _parse_selector_response(self, response: str, command: str) -> Dict:
        """Parse AI response to extract selector and confidence."""
        try:
            # Try to parse as JSON first
            if '{' in response and '}' in response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
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
        # Look for common CSS selector patterns
        css_patterns = [
            r'["\'`]([a-zA-Z0-9\[\]#\.\-_:*=\s,>+~\(\)]+)["\'`]',  # Quoted selectors
            r'selector:\s*([a-zA-Z0-9\[\]#\.\-_:*=\s,>+~\(\)]+)',   # selector: pattern
            r'^([a-zA-Z0-9\[\]#\.\-_:*=\s,>+~\(\)]+)$'             # Plain selector
        ]
        
        for pattern in css_patterns:
            matches = re.findall(pattern, response, re.MULTILINE)
            if matches:
                selector = matches[0].strip()
                if self._is_valid_selector(selector):
                    return selector
        
        # Generate basic selector based on command
        return self._generate_fallback_selector(command)

    def _is_valid_selector(self, selector: str) -> bool:
        """Basic validation of CSS selector."""
        if not selector or len(selector) < 1:
            return False
        
        # Check for common CSS selector characters
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[]#.-_:*=,>+~() ')
        return all(char in valid_chars for char in selector)

    def _generate_fallback_selector(self, command: str) -> str:
        """Generate a basic selector based on command keywords."""
        command_lower = command.lower()
        
        if "button" in command_lower or "click" in command_lower:
            if "login" in command_lower:
                return "button[type='submit'], .login-btn, [data-testid*='login']"
            elif "buy" in command_lower or "purchase" in command_lower:
                return "button[class*='buy'], button[class*='add-to-cart'], .buy-now"
            elif "search" in command_lower:
                return "button[type='submit'], .search-btn, [data-testid*='search']"
            else:
                return "button, .btn, [role='button']"
        
        elif "type" in command_lower or "enter" in command_lower:
            if "email" in command_lower:
                return "input[type='email'], input[name*='email']"
            elif "password" in command_lower:
                return "input[type='password'], input[name*='password']"
            elif "search" in command_lower:
                return "input[type='search'], input[placeholder*='search'], .search-input"
            else:
                return "input, textarea"
        
        elif "select" in command_lower:
            return "select, .dropdown, [role='combobox']"
        
        else:
            return "*"

    def _generate_universal_fallback(self, command: str) -> Dict:
        """Generate intelligent fallback selectors that work on any website."""
        command_lower = command.lower()
        
        # Universal patterns that work across websites
        if "login" in command_lower:
            selector = "button:has-text('Login'), a:has-text('Login'), button:has-text('Sign In'), a:has-text('Sign In'), [aria-label*='login' i], input[type='submit'][value*='Login' i]"
            
        elif "search" in command_lower:
            selector = "input[type='search'], input[placeholder*='search' i], input[name*='search' i], [aria-label*='search' i], input[role='searchbox']"
            
        elif "mobile" in command_lower or "phone" in command_lower:
            selector = "input[type='tel'], input[maxlength='10'], input[placeholder*='phone' i], input[placeholder*='mobile' i], input[name*='phone' i], input[name*='mobile' i]"
            
        elif "email" in command_lower:
            selector = "input[type='email'], input[placeholder*='email' i], input[name*='email' i], [aria-label*='email' i]"
            
        elif "otp" in command_lower:
            selector = "button:has-text('OTP'), button:has-text('Verify'), button:has-text('Send OTP'), input[type='submit']"
            
        elif "submit" in command_lower or "continue" in command_lower:
            selector = "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Continue')"
            
        elif "click" in command_lower:
            # Extract what to click on
            import re
            text_match = re.search(r'click (?:on )?(.+)', command_lower)
            if text_match:
                target_text = text_match.group(1).strip()
                selector = f"button:has-text('{target_text}'), a:has-text('{target_text}'), [aria-label*='{target_text}' i], [title*='{target_text}' i]"
            else:
                selector = "button, a, [role='button'], [onclick]"
                
        else:
            # Generic fallback
            selector = "button, a, input, [role='button']"
        
        return {
            "selector": selector,
            "confidence": 0.5,
            "reasoning": f"Universal fallback for: {command}",
            "element_type": "generic",
            "source": "universal_fallback"
        }
