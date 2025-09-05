"""
Universal AI Provider - Works with ANY website without hardcoded patterns
Eliminates site-specific logic and uses pure AI intelligence
"""
import json
import logging
from typing import Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)

class UniversalAIProvider:
    """AI provider that works universally across all websites"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def find_selector(self, command: str, page_context: str, context_type: str = "universal") -> Tuple[str, float, str]:
        """Find selector using universal AI approach without any hardcoded patterns"""
        
        try:
            # Create universal prompt that works for any website
            prompt = self._create_universal_prompt(command, page_context, context_type)
            
            # Call AI with universal approach
            response = self._call_ai_api(prompt)
            
            if response:
                selector = response.get('selector', '')
                confidence = response.get('confidence', 0.0)
                reasoning = response.get('reasoning', '')
                
                logger.info(f"🤖 Universal AI: {selector} (confidence: {confidence:.2f})")
                logger.debug(f"Reasoning: {reasoning}")
                
                return selector, confidence, "universal_ai"
            
        except Exception as e:
            logger.error(f"Universal AI provider failed: {e}")
        
        return None, 0.0, "failed"
    
    def _create_universal_prompt(self, command: str, page_context: str, context_type: str) -> str:
        """Create a universal prompt that works for any website architecture"""
        
        # Check if this is a product-specific command
        product_context = ""
        if "add" in command.lower() and "to cart" in command.lower():
            # Extract product name for context-aware selection
            add_pos = command.lower().find('add')
            cart_pos = command.lower().find('to cart')
            if add_pos < cart_pos:
                product_name = command[add_pos+3:cart_pos].strip()
                product_context = f"""
🛍️ **PRODUCT-SPECIFIC COMMAND DETECTED**:
- Product: "{product_name}"
- Action: Add to cart
- Strategy: Find the "Add to Cart" button specifically for "{product_name}"
- Look for: Product containers/cards containing "{product_name}" text, then find the associated add-to-cart button
- Avoid: Generic "Add to Cart" buttons that might be for other products
"""
        
        return f"""You are an expert web automation specialist who can work with ANY website architecture. Your job is to analyze the page and find the best selector for the given command.

🎯 **COMMAND TO EXECUTE**: {command}
{product_context}

📄 **CURRENT PAGE ANALYSIS**:
{page_context[:3000]}  

🧠 **UNIVERSAL APPROACH PRINCIPLES**:

1. **ANALYZE FIRST**: Study the page structure, framework patterns, and naming conventions
2. **ADAPT TO SITE**: Each site has unique patterns - discover them from the HTML
3. **PRODUCT-SPECIFIC SELECTION**: When dealing with product commands, find the specific product container FIRST, then locate the action button within that context
4. **PRIORITY ORDER**: 
   - Product-specific selectors (for e-commerce commands)
   - Exact visible text matches (highest reliability)
   - Data attributes (data-testid, data-test, data-automation-id)
   - Semantic HTML attributes (name, id, aria-label, placeholder)
   - Class patterns that match site conventions
   - CSS combinations for precision

5. **UNIVERSAL STRATEGIES**:
   - For PRODUCT COMMANDS: Use standard CSS selectors and data attributes - avoid :has() and :contains() 
   - For FIRST/LAST COMMANDS: Use :first-child, :last-child, :nth-child(), :nth-of-type()
   - For INPUTS: Look for name, placeholder, aria-label, surrounding labels
   - For BUTTONS: Prioritize visible text, then data attributes, then classes
   - For LINKS: Use href patterns and text content
   - For ANY ELEMENT: Use text() for visible text matching in XPath style

6. **CROSS-BROWSER COMPATIBILITY**:
   - Avoid :has() and :contains() pseudo-selectors (not universally supported)
   - Use standard CSS selectors: class, id, attributes, nth-child
   - For text-based selection, use data attributes or specific class/id patterns
   - For positional selection, use :first-child, :nth-child(1), :nth-of-type(1)
   - Generate multiple fallback strategies using different approaches

7. **FRAMEWORK DETECTION**: 
   - React apps: Look for data-testid, className patterns
   - Angular: Look for ng-*, data-cy attributes  
   - Vue: Look for v-* attributes, scoped styling
   - E-commerce sites: Look for product-specific data attributes and container patterns
   - Corporate sites: Look for accessibility attributes

🔍 **ANALYSIS PROCESS**:
1. What type of website is this? (e-commerce, corporate, SaaS, etc.)
2. What framework patterns do you see in the HTML?
3. What naming conventions does this site use?
4. Which elements match the command intent?
5. What's the most reliable selector strategy for THIS specific site?

🛍️ **E-COMMERCE SPECIFIC PATTERNS**:
- Product containers: Usually .product, .item, .card with child elements
- For "first product" commands: Use container:first-child element-within-container
- For "add to cart" buttons: Look for .btn + cart/inventory related classes
- Example: .inventory_item:first-child .btn_inventory (container first, then button inside)

⚡ **OUTPUT REQUIREMENTS**:
- Generate 3-5 fallback selectors separated by commas
- Start with the MOST RELIABLE selector for this specific site
- NO HARDCODED ASSUMPTIONS - adapt to what you see
- Consider element visibility and interaction capability

Respond in JSON format:
{{
    "selector": "primary-selector, fallback1, fallback2, fallback3",
    "confidence": 0.85,
    "reasoning": "Detailed explanation of why these selectors work for THIS specific site based on the HTML analysis",
    "site_type": "detected site type (e-commerce/corporate/saas/etc)",
    "framework": "detected framework or 'vanilla'",
    "strategy": "primary strategy used (text-based/data-attrs/semantic/class-based)"
}}

🚫 **AVOID**:
- Generic assumptions about how sites "should" work
- Hardcoded selectors from other sites
- One-size-fits-all approaches

✅ **FOCUS ON**:
- What's actually in THIS page's HTML
- THIS site's specific patterns and conventions
- Maximum reliability for THIS particular website"""

    def _call_ai_api(self, prompt: str) -> Optional[Dict]:
        """Call AI API with universal approach"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a universal web automation expert who analyzes each website individually and adapts to its specific patterns. Never use hardcoded assumptions. Always provide the EXACT same response for identical inputs for test reliability."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.0,  # Zero temperature for 100% deterministic responses
                "max_tokens": 1000,
                "seed": 42  # Fixed seed for reproducible results
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError:
                    # Try to extract JSON from text
                    return self._extract_json_from_text(content)
            else:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
        
        return None
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        try:
            # Look for JSON blocks
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                return json.loads(json_text)
        except Exception:
            pass
        
        return None
    
    def analyze_page_for_learning(self, page_context: str) -> Dict[str, Any]:
        """Analyze page to learn patterns for future use"""
        
        prompt = f"""Analyze this webpage to understand its architecture and patterns for future automation tasks.

PAGE CONTENT:
{page_context[:2000]}

Provide analysis in JSON format:
{{
    "site_type": "e-commerce|corporate|saas|blog|news|social|other",
    "framework": "react|angular|vue|jquery|vanilla|unknown",
    "ui_library": "bootstrap|material-ui|ant-design|custom|unknown",
    "naming_patterns": {{
        "data_attributes": ["common data-* patterns found"],
        "class_conventions": ["class naming patterns"],
        "id_patterns": ["id patterns found"]
    }},
    "interaction_elements": {{
        "buttons": ["common button patterns"],
        "inputs": ["common input patterns"],
        "links": ["common link patterns"]
    }},
    "reliability_score": 0.85,
    "notes": "Key observations about this site's automation patterns"
}}"""

        try:
            response = self._call_ai_api(prompt)
            return response if response else {}
        except Exception as e:
            logger.error(f"Page analysis failed: {e}")
            return {}


class UniversalIntelligenceProvider:
    """Intelligence provider that adapts to any website"""
    
    def __init__(self, ai_provider):
        self.ai_provider = ai_provider
        self.site_patterns = {}  # Cache for site-specific patterns
    
    def find_selector(self, command: str, page_context: str, context_type: str = "universal") -> Tuple[str, float, str]:
        """Find selector with universal intelligence"""
        
        # Extract site domain for pattern caching
        site_domain = self._extract_domain_from_context(page_context)
        
        # Check if we have learned patterns for this site
        if site_domain in self.site_patterns:
            logger.info(f"📚 Using learned patterns for {site_domain}")
            enhanced_context = self._enhance_context_with_patterns(page_context, site_domain)
        else:
            enhanced_context = page_context
        
        # Use AI provider with enhanced context
        selector, confidence, source = self.ai_provider.find_selector(
            command, enhanced_context, context_type
        )
        
        # Learn from successful interactions
        if selector and confidence > 0.6:
            self._learn_pattern(site_domain, command, selector, confidence)
        
        return selector, confidence, source
    
    def _extract_domain_from_context(self, context: str) -> str:
        """Extract domain from page context"""
        try:
            import re
            url_match = re.search(r'URL: https?://([^/\n]+)', context)
            if url_match:
                return url_match.group(1)
        except Exception:
            pass
        return "unknown"
    
    def _enhance_context_with_patterns(self, context: str, domain: str) -> str:
        """Enhance context with learned patterns for the site"""
        patterns = self.site_patterns.get(domain, {})
        
        enhancement = f"""

LEARNED PATTERNS FOR {domain}:
Framework: {patterns.get('framework', 'unknown')}
Common Selectors: {patterns.get('successful_selectors', [])}
Naming Patterns: {patterns.get('naming_patterns', {})}
Reliability Notes: {patterns.get('notes', 'None')}
"""
        
        return context + enhancement
    
    def _learn_pattern(self, domain: str, command: str, selector: str, confidence: float):
        """Learn successful patterns for future use"""
        if domain not in self.site_patterns:
            self.site_patterns[domain] = {
                'successful_selectors': [],
                'command_patterns': {},
                'framework': 'unknown',
                'naming_patterns': {}
            }
        
        # Store successful selector
        self.site_patterns[domain]['successful_selectors'].append({
            'selector': selector,
            'command': command,
            'confidence': confidence
        })
        
        # Keep only top 10 patterns per site
        self.site_patterns[domain]['successful_selectors'] = sorted(
            self.site_patterns[domain]['successful_selectors'],
            key=lambda x: x['confidence'],
            reverse=True
        )[:10]


# Factory function for universal AI
def create_universal_intelligence(ai_provider="openai", api_key=None):
    """Create universal intelligence provider"""
    
    if ai_provider == "openai" and api_key:
        ai = UniversalAIProvider(api_key)
        return UniversalIntelligenceProvider(ai)
    
    return None
