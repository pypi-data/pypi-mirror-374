"""
Offline Intelligence Engine - Local fallback when AI providers fail
Essential for production deployment with reliable fallback strategies
"""
import logging
import re
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class OfflineIntelligenceEngine:
    """Local intelligence that works without AI API calls"""
    
    def __init__(self):
        self.heuristic_patterns = self._load_heuristic_patterns()
        self.common_selectors = self._load_common_selectors()
        self.framework_patterns = self._load_framework_patterns()
        self.success_cache = {}  # Cache successful patterns
        
        logger.info("🧠 Offline Intelligence Engine initialized")
    
    def find_selector(self, command: str, page_context: str) -> Tuple[str, float, str]:
        """Find selector using offline heuristics - NO AI API calls"""
        
        try:
            # Parse command intent
            intent = self._parse_command_intent(command)
            domain = self._extract_domain(page_context)
            
            # Strategy 1: Check success cache first
            cached_selector = self._check_success_cache(domain, command)
            if cached_selector:
                return cached_selector, 0.9, "cache"
            
            # Strategy 2: Framework-specific patterns
            framework = self._detect_framework(page_context)
            if framework:
                selector = self._try_framework_patterns(intent, framework, page_context)
                if selector:
                    return selector, 0.8, f"framework_{framework}"
            
            # Strategy 3: Universal heuristic patterns
            selector = self._try_heuristic_patterns(intent, page_context)
            if selector:
                return selector, 0.7, "heuristic"
            
            # Strategy 4: Common selector fallbacks
            selector = self._try_common_selectors(intent)
            if selector:
                return selector, 0.5, "common"
            
            logger.warning(f"Offline intelligence failed for: {command}")
            return None, 0.0, "failed"
            
        except Exception as e:
            logger.error(f"Offline intelligence error: {e}")
            return None, 0.0, "error"
    
    def record_success(self, domain: str, command: str, selector: str, confidence: float):
        """Record successful selector for future use"""
        cache_key = f"{domain}:{command.lower()}"
        self.success_cache[cache_key] = selector
        logger.debug(f"Cached successful pattern: {cache_key} -> {selector}")
    
    def _parse_command_intent(self, command: str) -> Dict[str, str]:
        """Parse command to extract intent without AI"""
        command_lower = command.lower().strip()
        
        # Verb detection
        verb = "unknown"
        if any(word in command_lower for word in ["click", "press", "tap"]):
            verb = "click"
        elif any(word in command_lower for word in ["type", "enter", "input", "fill"]):
            verb = "type"
        elif any(word in command_lower for word in ["navigate", "goto", "visit"]):
            verb = "navigate"
        elif any(word in command_lower for word in ["select", "choose", "pick"]):
            verb = "select"
        
        # Target extraction (simple heuristics)
        target = ""
        if "'" in command or '"' in command:
            # Extract quoted text
            quotes = re.findall(r"['\"]([^'\"]*)['\"]", command)
            if quotes:
                target = quotes[0]
        else:
            # Extract key phrases
            words = command_lower.split()
            if verb == "click":
                # Look for button/link indicators
                for i, word in enumerate(words):
                    if word in ["button", "link", "login", "submit", "cart", "checkout"]:
                        target = word
                        break
            elif verb == "type":
                # Look for field indicators  
                for word in words:
                    if word in ["username", "password", "email", "name", "search"]:
                        target = word
                        break
        
        return {
            "verb": verb,
            "target": target,
            "original": command
        }
    
    def _extract_domain(self, page_context: str) -> str:
        """Extract domain from page context"""
        try:
            url_match = re.search(r'URL: https?://([^/\n]+)', page_context)
            if url_match:
                return url_match.group(1)
        except:
            pass
        return "unknown"
    
    def _check_success_cache(self, domain: str, command: str) -> Optional[str]:
        """Check if we have a cached successful selector"""
        cache_key = f"{domain}:{command.lower()}"
        return self.success_cache.get(cache_key)
    
    def _detect_framework(self, page_context: str) -> Optional[str]:
        """Detect web framework from page context"""
        context_lower = page_context.lower()
        
        # Framework detection patterns
        if 'data-reactroot' in context_lower or 'react' in context_lower:
            return "react"
        elif 'ng-' in context_lower or 'angular' in context_lower:
            return "angular"
        elif 'v-' in context_lower or 'vue' in context_lower:
            return "vue"
        elif 'bootstrap' in context_lower or 'btn btn-' in context_lower:
            return "bootstrap"
        elif 'material' in context_lower or 'mat-' in context_lower:
            return "material"
        
        return None
    
    def _try_framework_patterns(self, intent: Dict, framework: str, page_context: str) -> Optional[str]:
        """Try framework-specific patterns"""
        patterns = self.framework_patterns.get(framework, {})
        verb = intent["verb"]
        target = intent["target"]
        
        if verb in patterns:
            for pattern_name, selectors in patterns[verb].items():
                if target in pattern_name or pattern_name == "generic":
                    # Return first selector that might work
                    if isinstance(selectors, list):
                        return selectors[0]
                    else:
                        return selectors
        
        return None
    
    def _try_heuristic_patterns(self, intent: Dict, page_context: str) -> Optional[str]:
        """Try universal heuristic patterns"""
        verb = intent["verb"]
        target = intent["target"].lower()
        
        patterns = self.heuristic_patterns.get(verb, {})
        
        # Try specific target patterns first
        for pattern_key, selectors in patterns.items():
            if target and target in pattern_key.lower():
                if isinstance(selectors, list):
                    return selectors[0]
                return selectors
        
        # Try generic patterns
        generic_patterns = patterns.get("generic", [])
        if generic_patterns:
            return generic_patterns[0] if isinstance(generic_patterns, list) else generic_patterns
        
        return None
    
    def _try_common_selectors(self, intent: Dict) -> Optional[str]:
        """Try most common selector patterns"""
        verb = intent["verb"]
        target = intent["target"].lower()
        
        common = self.common_selectors.get(verb, [])
        if common:
            return common[0] if isinstance(common, list) else common
        
        return None
    
    def _load_heuristic_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load heuristic patterns for offline use"""
        return {
            "click": {
                "login": [
                    'button:has-text("Login")',
                    'input[value*="Login"]',
                    'a:has-text("Login")',
                    '[data-testid*="login"]',
                    '#login',
                    '.login-btn'
                ],
                "button": [
                    'button',
                    'input[type="submit"]',
                    '[role="button"]',
                    '.btn',
                    'a.button'
                ],
                "submit": [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    '#submit',
                    '.submit'
                ],
                "cart": [
                    '[data-testid*="cart"]',
                    '.cart',
                    '#cart',
                    'a:has-text("Cart")',
                    '.shopping-cart'
                ],
                "checkout": [
                    'button:has-text("Checkout")',
                    '[data-testid*="checkout"]',
                    '.checkout',
                    '#checkout'
                ],
                "generic": [
                    'button',
                    'a[href]',
                    '[role="button"]',
                    'input[type="submit"]'
                ]
            },
            "type": {
                "username": [
                    'input[name*="user"]',
                    'input[id*="user"]',
                    'input[placeholder*="user"]',
                    '#username',
                    '.username'
                ],
                "password": [
                    'input[type="password"]',
                    'input[name*="pass"]',
                    'input[id*="pass"]',
                    '#password'
                ],
                "email": [
                    'input[type="email"]',
                    'input[name*="email"]',
                    'input[id*="email"]',
                    '#email'
                ],
                "search": [
                    'input[type="search"]',
                    'input[name*="search"]',
                    'input[placeholder*="search"]',
                    '#search',
                    '.search'
                ],
                "name": [
                    'input[name*="name"]',
                    'input[id*="name"]',
                    'input[placeholder*="name"]'
                ],
                "generic": [
                    'input[type="text"]',
                    'input:not([type])',
                    'textarea'
                ]
            },
            "select": {
                "dropdown": [
                    'select',
                    '[role="combobox"]',
                    '.dropdown select'
                ],
                "generic": [
                    'select'
                ]
            }
        }
    
    def _load_common_selectors(self) -> Dict[str, List[str]]:
        """Load most common selectors as final fallback"""
        return {
            "click": [
                'button',
                'a',
                '[role="button"]',
                'input[type="submit"]',
                '.btn'
            ],
            "type": [
                'input[type="text"]',
                'input:not([type])',
                'textarea'
            ],
            "select": [
                'select'
            ]
        }
    
    def _load_framework_patterns(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """Load framework-specific patterns"""
        return {
            "react": {
                "click": {
                    "button": ['button[class*="btn"]', '.btn', '[role="button"]'],
                    "login": ['button:has-text("Login")', '[data-testid*="login"]']
                },
                "type": {
                    "input": ['input[class*="input"]', '.form-control', 'input']
                }
            },
            "bootstrap": {
                "click": {
                    "button": ['.btn', '.btn-primary', 'button.btn'],
                    "login": ['.btn:has-text("Login")', 'input.btn[value*="Login"]']
                },
                "type": {
                    "input": ['.form-control', 'input.form-control']
                }
            },
            "material": {
                "click": {
                    "button": ['.mat-button', '.mat-raised-button', 'button[mat-button]']
                },
                "type": {
                    "input": ['.mat-input-element', 'input.mat-input-element']
                }
            }
        }


class HybridIntelligence:
    """Combines AI and offline intelligence for maximum reliability"""
    
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
        self.offline_engine = OfflineIntelligenceEngine()
        self.fallback_count = 0
        
    def find_selector(self, command: str, page_context: str) -> Tuple[str, float, str]:
        """Try AI first, fallback to offline intelligence"""
        
        # Try AI provider first if available
        if self.ai_provider:
            try:
                selector, confidence, source = self.ai_provider.find_selector(command, page_context)
                if selector and confidence > 0.4:
                    logger.info(f"🤖 AI success: {selector} (confidence: {confidence:.2f})")
                    return selector, confidence, source
                else:
                    logger.warning(f"⚠️ AI low confidence ({confidence:.2f}), falling back to offline")
            except Exception as e:
                logger.warning(f"⚠️ AI provider failed ({e}), falling back to offline")
                self.fallback_count += 1
        
        # Fallback to offline intelligence
        logger.info("🧠 Using offline intelligence")
        selector, confidence, source = self.offline_engine.find_selector(command, page_context)
        
        if selector:
            logger.info(f"✅ Offline success: {selector} (confidence: {confidence:.2f})")
        else:
            logger.error("❌ Both AI and offline intelligence failed")
        
        return selector, confidence, f"offline_{source}"
    
    def record_success(self, domain: str, command: str, selector: str, confidence: float):
        """Record success in offline cache"""
        self.offline_engine.record_success(domain, command, selector, confidence)
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get statistics on fallback usage"""
        return {
            "offline_fallbacks": self.fallback_count,
            "cached_patterns": len(self.offline_engine.success_cache)
        }


# Factory function for production use
def create_production_intelligence(ai_provider=None):
    """Create hybrid intelligence for production deployment"""
    return HybridIntelligence(ai_provider)
