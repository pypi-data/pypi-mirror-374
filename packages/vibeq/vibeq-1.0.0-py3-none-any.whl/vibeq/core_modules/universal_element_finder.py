"""
Universal Element Finder - AI-native element discovery for ANY website
Eliminates all hardcoded patterns and site-specific logic with caching for reliability
"""
import logging
import json
from typing import Optional, List, Dict, Any, Tuple
from .command_parser import Intent
from ..selector_cache import SelectorCache

logger = logging.getLogger(__name__)

# Placeholder classes that will be implemented properly
class PatternDatabase:
    """Simple pattern database for learning successful selectors"""
    def __init__(self):
        self.patterns = {}
    
    def get_patterns(self, intent_type: str) -> List[str]:
        return self.patterns.get(intent_type, [])
    
    def add_pattern(self, intent_type: str, selector: str, confidence: float):
        if intent_type not in self.patterns:
            self.patterns[intent_type] = []
        self.patterns[intent_type].append((selector, confidence))

class VisualElementAnalyzer:
    """Visual element analysis for UI automation"""
    def __init__(self, browser):
        self.browser = browser
    
    def find_by_visual_cues(self, intent) -> Optional[str]:
        # Placeholder for visual analysis
        return None

class UniversalElementFinder:
    """Universal element finder that works on ANY website without hardcoded patterns"""
    
    def __init__(self, browser, intelligence=None):
        self.browser = browser
        self.intelligence = intelligence
        self.pattern_database = PatternDatabase()
        self.visual_analyzer = VisualElementAnalyzer(browser) if browser else None
        
        # Reliability approach: Cache working selectors
        self.selector_cache = SelectorCache()
    
    def execute_javascript(self, script: str, args: list = None) -> Any:
        """Execute JavaScript in the browser context"""
        try:
            # Handle VibeQ's browser adapter wrapper
            browser_instance = self.browser
            
            # Unwrap if it's a browser adapter
            if hasattr(browser_instance, 'page'):
                # Playwright style
                page = browser_instance.page
                if hasattr(page, 'evaluate'):
                    if args:
                        return page.evaluate(f"(args) => {{ {script} }}", args)
                    else:
                        return page.evaluate(f"() => {{ {script} }}")
            elif hasattr(browser_instance, 'driver'):
                # Selenium WebDriver style
                driver = browser_instance.driver
                if hasattr(driver, 'execute_script'):
                    if args:
                        return driver.execute_script(script, *args)
                    else:
                        return driver.execute_script(script)
            elif hasattr(browser_instance, 'evaluate'):
                # Direct Playwright
                if args:
                    return browser_instance.evaluate(f"(args) => {{ {script} }}", args)
                else:
                    return browser_instance.evaluate(f"() => {{ {script} }}")
            elif hasattr(browser_instance, 'execute_script'):
                # Direct Selenium
                if args:
                    return browser_instance.execute_script(script, *args)
                else:
                    return browser_instance.execute_script(script)
            else:
                logger.error(f"No JavaScript execution method found on {type(browser_instance)}")
                return None
                
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return None
    
    def find_for_intent(self, intent: Intent) -> Optional[str]:
        """Find the best selector for a given intent using cached-first approach"""
        logger.info(f"🌐 Universal search for: {intent.verb} '{intent.target}'")
        
        # Get current page context for caching
        page_url = self._get_current_url()
        page_context = self._get_page_context()
        command = f"{intent.verb} {intent.target}".strip()
        
        # Strategy 0: Check cache first (RELIABILITY FIRST!)
        cached_result = self.selector_cache.get_cached_selector(command, page_url, page_context)
        if cached_result:
            selector, confidence = cached_result
            # Validate cached selector still works
            if self._validate_selector(selector):
                logger.info(f"🎯 Using cached selector: {selector}")
                return selector
            else:
                # Mark as failed and continue to fresh discovery
                self.selector_cache.mark_selector_failed(command, page_url, selector, page_context)
        
        # Strategy 1: AI Intelligence (Primary)
        if self.intelligence:
            selector = self._try_ai_discovery(intent)
            if selector:
                logger.info(f"🤖 AI discovered: {selector}")
                # Cache successful AI discovery
                self.selector_cache.cache_successful_selector(command, page_url, selector, 0.9, page_context)
                return selector
        
        # Strategy 2: Dynamic DOM Analysis
        selector = self._try_dom_analysis(intent)
        if selector:
            logger.info(f"🔍 DOM analysis found: {selector}")
            self.selector_cache.cache_successful_selector(command, page_url, selector, 0.8, page_context)
            return selector
        
        # Strategy 3: Visual Element Recognition
        if self.visual_analyzer:
            selector = self._try_visual_recognition(intent)
            if selector:
                logger.info(f"👁️ Visual recognition found: {selector}")
                self.selector_cache.cache_successful_selector(command, page_url, selector, 0.7, page_context)
                return selector
        
        # Strategy 4: Semantic Web Standards
        selector = self._try_semantic_standards(intent)
        if selector:
            logger.info(f"📝 Semantic standards found: {selector}")
            self.selector_cache.cache_successful_selector(command, page_url, selector, 0.6, page_context)
            return selector
        
        # Strategy 5: Pattern Learning from Database
        selector = self._try_learned_patterns(intent)
        if selector:
            logger.info(f"📚 Learned pattern found: {selector}")
            self.selector_cache.cache_successful_selector(command, page_url, selector, 0.5, page_context)
            return selector
        
        logger.warning(f"⚠️ No selector found for: {intent.verb} '{intent.target}'")
        return None
        
        # Strategy 1: AI Intelligence (Primary)
        if self.intelligence:
            selector = self._try_ai_discovery(intent)
            if selector:
                logger.info(f"🤖 AI discovered: {selector}")
                return selector
        
        # Strategy 2: Dynamic DOM Analysis
        selector = self._try_dom_analysis(intent)
        if selector:
            logger.info(f"🔍 DOM analysis found: {selector}")
            return selector
        
        # Strategy 3: Visual Element Recognition
        if self.visual_analyzer:
            selector = self._try_visual_recognition(intent)
            if selector:
                logger.info(f"👁️ Visual recognition found: {selector}")
                return selector
        
        # Strategy 4: Semantic Web Standards
        selector = self._try_semantic_standards(intent)
        if selector:
            logger.info(f"📝 Semantic standards found: {selector}")
            return selector
        
        # Strategy 5: Pattern Learning from Database
        selector = self._try_learned_patterns(intent)
        if selector:
            logger.info(f"📚 Learned pattern found: {selector}")
            return selector
        
        logger.warning(f"⚠️ No selector found for: {intent.verb} '{intent.target}'")
        return None
    
    def _try_ai_discovery(self, intent: Intent) -> Optional[str]:
        """Use AI to dynamically discover element selectors"""
        try:
            # Get rich page context
            page_context = self._get_comprehensive_page_context()
            command = self._intent_to_command(intent)
            
            # Use AI with enhanced context
            selector, confidence, source = self.intelligence.find_selector(
                command, 
                page_context,
                context_type="universal"
            )
            
            if selector and confidence > 0.4:  # Lower threshold for universal use
                # Record successful pattern for learning
                self._record_pattern_success(intent, selector, confidence, "ai")
                return selector
            
        except Exception as e:
            logger.debug(f"AI discovery failed: {e}")
        
        return None
    
    def _try_dom_analysis(self, intent: Intent) -> Optional[str]:
        """Analyze DOM structure dynamically to find elements"""
        try:
            if not self.browser.page:
                return None
            
            # Get all interactive elements
            elements = self._extract_interactive_elements()
            
            # Analyze each element for intent match
            best_match = self._find_best_element_match(intent, elements)
            
            if best_match:
                selector = best_match.get('selector')
                confidence = best_match.get('confidence', 0.0)
                
                if confidence > 0.5:
                    self._record_pattern_success(intent, selector, confidence, "dom")
                    return selector
            
        except Exception as e:
            logger.debug(f"DOM analysis failed: {e}")
        
        return None
    
    def _try_visual_recognition(self, intent: Intent) -> Optional[str]:
        """Use visual analysis to identify elements"""
        if not self.visual_analyzer:
            return None
        
        try:
            # Take screenshot and analyze
            visual_elements = self.visual_analyzer.find_elements_by_intent(intent)
            
            if visual_elements:
                best_element = visual_elements[0]  # Highest confidence
                selector = best_element.get('selector')
                confidence = best_element.get('confidence', 0.0)
                
                if confidence > 0.6:
                    self._record_pattern_success(intent, selector, confidence, "visual")
                    return selector
            
        except Exception as e:
            logger.debug(f"Visual recognition failed: {e}")
        
        return None
    
    def _try_semantic_standards(self, intent: Intent) -> Optional[str]:
        """Use web standards and accessibility patterns"""
        try:
            # Generate semantic selectors based on web standards
            semantic_selectors = self._generate_semantic_selectors(intent)
            
            for selector in semantic_selectors:
                if self._test_selector_validity(selector):
                    confidence = self._calculate_semantic_confidence(intent, selector)
                    if confidence > 0.4:
                        self._record_pattern_success(intent, selector, confidence, "semantic")
                        return selector
            
        except Exception as e:
            logger.debug(f"Semantic standards failed: {e}")
        
        return None
    
    def _try_learned_patterns(self, intent: Intent) -> Optional[str]:
        """Use patterns learned from other websites"""
        try:
            # Get similar patterns from database
            similar_patterns = self.pattern_database.get_patterns_for_intent(intent)
            
            for pattern in similar_patterns:
                selector = pattern.get('selector')
                if self._test_selector_validity(selector):
                    confidence = pattern.get('confidence', 0.0) * 0.8  # Reduce for cross-site
                    if confidence > 0.3:
                        self._record_pattern_success(intent, selector, confidence, "learned")
                        return selector
            
        except Exception as e:
            logger.debug(f"Learned patterns failed: {e}")
        
        return None
    
    def _get_comprehensive_page_context(self) -> str:
        """Get comprehensive page context for AI analysis"""
        try:
            if not self.browser.page:
                return ""
            
            # Extract key page information
            context_parts = []
            
            # Page metadata
            title = self.browser.page.title()
            url = self.browser.page.url
            context_parts.append(f"Title: {title}")
            context_parts.append(f"URL: {url}")
            
            # Extract interactive elements with rich context
            interactive_html = self._extract_interactive_html()
            context_parts.append(f"Interactive Elements:\n{interactive_html}")
            
            # Page structure analysis
            structure = self._analyze_page_structure()
            context_parts.append(f"Structure: {structure}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.debug(f"Page context extraction failed: {e}")
            return ""
    
    def _extract_interactive_elements(self) -> List[Dict]:
        """Extract all interactive elements with their properties"""
        elements = []
        
        try:
            page = self.browser.page
            if not page:
                return elements
            
            # Query all interactive element types
            interactive_selectors = [
                'input', 'button', 'a[href]', 'select', 'textarea',
                '[role="button"]', '[role="link"]', '[role="textbox"]',
                '[onclick]', '[data-testid]', '[data-test]'
            ]
            
            for selector in interactive_selectors:
                try:
                    elements_found = page.query_selector_all(selector)
                    for elem in elements_found:
                        element_info = self._extract_element_info(elem, selector)
                        if element_info:
                            elements.append(element_info)
                except Exception:
                    continue
            
        except Exception as e:
            logger.debug(f"Interactive elements extraction failed: {e}")
        
        return elements
    
    def _extract_element_info(self, element, base_selector: str) -> Optional[Dict]:
        """Extract comprehensive information about an element"""
        try:
            # Get all attributes
            attrs = {}
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'aria-label', 
                        'data-testid', 'data-test', 'value', 'href', 'role']:
                try:
                    value = element.get_attribute(attr)
                    if value:
                        attrs[attr] = value
                except:
                    continue
            
            # Get text content
            try:
                text = element.text_content() or element.inner_text()
                text = text.strip() if text else ""
            except:
                text = ""
            
            # Get computed selector
            selector = self._generate_optimal_selector(attrs, base_selector)
            
            return {
                'selector': selector,
                'attributes': attrs,
                'text': text,
                'tag': base_selector.split('[')[0],
                'visible': self._is_element_visible(element),
                'interactable': self._is_element_interactable(element)
            }
            
        except Exception:
            return None
    
    def _find_best_element_match(self, intent: Intent, elements: List[Dict]) -> Optional[Dict]:
        """Find the best element match for the given intent"""
        best_match = None
        best_confidence = 0.0
        
        for element in elements:
            confidence = self._calculate_element_confidence(intent, element)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = element.copy()
                best_match['confidence'] = confidence
        
        return best_match if best_confidence > 0.3 else None
    
    def _calculate_element_confidence(self, intent: Intent, element: Dict) -> float:
        """Calculate confidence score for element matching intent"""
        confidence = 0.0
        target_lower = intent.target.lower()
        verb = intent.verb.lower()
        
        # Text content matching (highest weight)
        text = element.get('text', '').lower()
        if target_lower in text:
            confidence += 0.4
        
        # Attribute matching
        attrs = element.get('attributes', {})
        
        # Placeholder matching
        placeholder = attrs.get('placeholder', '').lower()
        if target_lower in placeholder:
            confidence += 0.3
        
        # Name/ID matching
        name = attrs.get('name', '').lower()
        elem_id = attrs.get('id', '').lower()
        if target_lower in name or target_lower in elem_id:
            confidence += 0.25
        
        # Aria-label matching
        aria_label = attrs.get('aria-label', '').lower()
        if target_lower in aria_label:
            confidence += 0.2
        
        # Data attributes matching
        for key, value in attrs.items():
            if key.startswith('data-') and target_lower in value.lower():
                confidence += 0.15
        
        # Verb-specific matching
        if verb == 'type':
            if element.get('tag') in ['input', 'textarea']:
                confidence += 0.2
        elif verb == 'click':
            if element.get('tag') in ['button', 'a'] or attrs.get('role') == 'button':
                confidence += 0.2
        
        # Visibility and interactability
        if element.get('visible', False):
            confidence += 0.1
        if element.get('interactable', False):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_semantic_selectors(self, intent: Intent) -> List[str]:
        """Generate semantic selectors based on web standards"""
        selectors = []
        target = intent.target.lower()
        verb = intent.verb.lower()
        
        # Universal patterns based on semantic meaning
        if verb == 'type':
            # Input field patterns
            selectors.extend([
                f'input[placeholder*="{target}" i]',
                f'input[name*="{target}" i]',
                f'input[id*="{target}" i]',
                f'textarea[placeholder*="{target}" i]',
                f'[aria-label*="{target}" i]'
            ])
        
        elif verb == 'click':
            # Clickable element patterns
            selectors.extend([
                f'button:has-text("{intent.target}"):visible',
                f'a:has-text("{intent.target}"):visible',
                f'[role="button"]:has-text("{intent.target}"):visible',
                f'input[value*="{target}" i]',
                f'[aria-label*="{target}" i]'
            ])
        
        # Data attribute patterns (universal)
        selectors.extend([
            f'[data-testid*="{target.replace(" ", "-")}" i]',
            f'[data-test*="{target.replace(" ", "-")}" i]',
            f'[data-automation-id*="{target.replace(" ", "-")}" i]'
        ])
        
        return selectors
    
    def _test_selector_validity(self, selector: str) -> bool:
        """Test if selector is valid and finds elements"""
        try:
            if not self.browser.page:
                return False
            
            count = self.browser.page.locator(selector).count()
            return count > 0
            
        except Exception:
            return False
    
    def _calculate_semantic_confidence(self, intent: Intent, selector: str) -> float:
        """Calculate confidence for semantic selectors"""
        base_confidence = 0.5
        
        # Boost for specific attributes
        if 'data-testid' in selector or 'data-test' in selector:
            base_confidence += 0.2
        
        # Boost for has-text selectors
        if ':has-text' in selector:
            base_confidence += 0.15
        
        # Boost for aria-label
        if 'aria-label' in selector:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _record_pattern_success(self, intent: Intent, selector: str, confidence: float, source: str):
        """Record successful pattern for future learning"""
        try:
            pattern = {
                'intent_verb': intent.verb,
                'intent_target': intent.target,
                'selector': selector,
                'confidence': confidence,
                'source': source,
                'website': self.browser.page.url if self.browser.page else 'unknown'
            }
            self.pattern_database.record_success(pattern)
        except Exception as e:
            logger.debug(f"Pattern recording failed: {e}")
    
    def _intent_to_command(self, intent: Intent) -> str:
        """Convert intent to command string"""
        command = f"{intent.verb} {intent.target}"
        if intent.value:
            command += f" {intent.value}"
        return command
    
    def _extract_interactive_html(self) -> str:
        """Extract HTML of interactive elements only"""
        try:
            if not self.browser.page:
                return ""
            
            # Get visible interactive elements
            interactive_html = []
            selectors = ['input:visible', 'button:visible', 'a:visible', 'select:visible']
            
            for selector in selectors:
                try:
                    elements = self.browser.page.query_selector_all(selector)[:10]  # Limit for context
                    for elem in elements:
                        try:
                            html = elem.outer_HTML()[:200]  # Limit length
                            interactive_html.append(html)
                        except:
                            continue
                except:
                    continue
            
            return '\n'.join(interactive_html[:20])  # Limit total elements
            
        except Exception:
            return ""
    
    def _analyze_page_structure(self) -> str:
        """Analyze overall page structure"""
        try:
            if not self.browser.page:
                return ""
            
            structure_info = []
            
            # Check for common frameworks/patterns
            frameworks = self._detect_frameworks()
            if frameworks:
                structure_info.append(f"Frameworks: {', '.join(frameworks)}")
            
            # Count element types
            element_counts = self._count_element_types()
            structure_info.append(f"Elements: {element_counts}")
            
            return ' | '.join(structure_info)
            
        except Exception:
            return ""
    
    def _detect_frameworks(self) -> List[str]:
        """Detect common web frameworks"""
        frameworks = []
        
        try:
            page = self.browser.page
            if not page:
                return frameworks
            
            # Check for framework indicators
            checks = {
                'React': ['[data-reactroot]', 'react', '__REACT_DEVTOOLS'],
                'Angular': ['ng-', '[ng-app]', 'angular'],
                'Vue': ['v-', '[v-app]', '__VUE__'],
                'Bootstrap': ['.container', '.btn', '.form-control']
            }
            
            for framework, indicators in checks.items():
                for indicator in indicators:
                    try:
                        if indicator.startswith('[') or indicator.startswith('.'):
                            if page.query_selector(indicator):
                                frameworks.append(framework)
                                break
                        else:
                            # JavaScript variable check
                            result = page.evaluate(f"typeof {indicator} !== 'undefined'")
                            if result:
                                frameworks.append(framework)
                                break
                    except:
                        continue
            
        except Exception:
            pass
        
        return frameworks
    
    def _count_element_types(self) -> str:
        """Count different types of elements"""
        try:
            page = self.browser.page
            if not page:
                return ""
            
            counts = {}
            element_types = ['input', 'button', 'a', 'form', 'select', 'textarea']
            
            for elem_type in element_types:
                try:
                    count = page.locator(elem_type).count()
                    if count > 0:
                        counts[elem_type] = count
                except:
                    continue
            
            return ', '.join([f"{k}:{v}" for k, v in counts.items()])
            
        except Exception:
            return ""
    
    def _generate_optimal_selector(self, attrs: Dict, base_selector: str) -> str:
        """Generate the most optimal selector for an element"""
        # Priority order: data-testid > id > name > class > generic
        
        # Highest priority: data attributes
        if attrs.get('data-testid'):
            return f'[data-testid="{attrs["data-testid"]}"]'
        if attrs.get('data-test'):
            return f'[data-test="{attrs["data-test"]}"]'
        
        # High priority: unique ID
        if attrs.get('id'):
            return f'#{attrs["id"]}'
        
        # Medium priority: name attribute
        if attrs.get('name'):
            return f'{base_selector}[name="{attrs["name"]}"]'
        
        # Lower priority: specific class combinations
        if attrs.get('class'):
            classes = attrs['class'].split()[:2]  # Use first 2 classes
            class_selector = '.' + '.'.join(classes)
            return f'{base_selector}{class_selector}'
        
        # Fallback: base selector with type
        if attrs.get('type'):
            return f'{base_selector}[type="{attrs["type"]}"]'
        
        return base_selector
    
    def _get_current_url(self) -> str:
        """Get current page URL for caching"""
        try:
            if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                return self.browser.page.url
        except Exception:
            pass
        return "unknown"
    
    def _get_page_context(self) -> str:
        """Get page context for cache key generation"""
        try:
            if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                # Get basic page structure info for context
                element_counts = self.browser.page.evaluate("""
                    () => {
                        return {
                            inputs: document.querySelectorAll('input').length,
                            buttons: document.querySelectorAll('button').length,
                            links: document.querySelectorAll('a').length,
                            forms: document.querySelectorAll('form').length
                        };
                    }
                """)
                return json.dumps(element_counts, sort_keys=True)
        except Exception:
            pass
        return ""
    
    def _validate_selector(self, selector: str) -> bool:
        """Validate that a cached selector still works on current page"""
        try:
            if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                # For comma-separated selectors, try the first one
                first_selector = selector.split(',')[0].strip()
                element = self.browser.page.query_selector(first_selector)
                return element is not None
        except Exception:
            pass
        return False
    
    def _is_element_visible(self, element) -> bool:
        """Check if element is visible"""
        try:
            return element.is_visible()
        except:
            return False
    
    def _is_element_interactable(self, element) -> bool:
        """Check if element is interactable"""
        try:
            return element.is_enabled()
        except:
            return False


class PatternDatabase:
    """Database for learning and storing successful patterns across websites"""
    
    def __init__(self):
        self.patterns = []  # In production, this would be a persistent database
    
    def record_success(self, pattern: Dict):
        """Record a successful pattern"""
        self.patterns.append(pattern)
    
    def get_patterns_for_intent(self, intent: Intent) -> List[Dict]:
        """Get similar patterns for the given intent"""
        similar = []
        for pattern in self.patterns:
            if (pattern.get('intent_verb') == intent.verb and 
                intent.target.lower() in pattern.get('intent_target', '').lower()):
                similar.append(pattern)
        
        # Sort by confidence
        return sorted(similar, key=lambda x: x.get('confidence', 0), reverse=True)[:5]


class VisualElementAnalyzer:
    """Analyze elements visually using computer vision techniques"""
    
    def __init__(self, browser):
        self.browser = browser
    
    def find_elements_by_intent(self, intent: Intent) -> List[Dict]:
        """Find elements using visual analysis"""
        # Placeholder for visual analysis
        # In production, this would use CV libraries like OpenCV, PIL
        # to analyze screenshots and identify UI elements
        return []
