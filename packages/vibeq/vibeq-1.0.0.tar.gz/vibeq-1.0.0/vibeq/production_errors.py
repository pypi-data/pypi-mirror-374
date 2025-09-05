"""
Production Error Handling - Enterprise Grade
Never leave users hanging with cryptic errors - always provide actionable guidance
"""
import logging
import traceback
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    RECOVERABLE = "recoverable"
    DEGRADED = "degraded" 
    CRITICAL = "critical"

@dataclass
class VibeQSuggestion:
    """Actionable suggestion for users when automation fails"""
    title: str
    description: str
    code_example: str
    confidence: float
    auto_fix: Optional[Callable] = None

@dataclass 
class VibeQErrorContext:
    """Rich context for debugging automation failures"""
    command: str
    page_url: str
    page_title: str
    visible_elements: List[str]
    similar_elements: List[str]
    screenshot_path: Optional[str] = None

class VibeQException(Exception):
    """Base exception with rich context and recovery suggestions"""
    
    def __init__(self, message: str, severity: ErrorSeverity, context: VibeQErrorContext, 
                 suggestions: List[VibeQSuggestion] = None):
        self.message = message
        self.severity = severity  
        self.context = context
        self.suggestions = suggestions or []
        super().__init__(self._format_user_message())
    
    def _format_user_message(self) -> str:
        """Format user-friendly error message with suggestions"""
        lines = [
            f"🚨 VibeQ Automation Error: {self.message}",
            "",
            f"📍 Context:",
            f"   Command: '{self.context.command}'",
            f"   Page: {self.context.page_title} ({self.context.page_url})",
            ""
        ]
        
        if self.suggestions:
            lines.append("💡 Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"   {i}. {suggestion.title} (confidence: {suggestion.confidence:.0%})")
                lines.append(f"      {suggestion.description}")
                lines.append(f"      Try: {suggestion.code_example}")
                if suggestion.auto_fix:
                    lines.append(f"      Auto-fix available: call error.auto_fix_{i}()")
                lines.append("")
        
        if self.context.visible_elements:
            lines.append("👀 Visible elements on page:")
            for element in self.context.visible_elements[:5]:  # Show top 5
                lines.append(f"   • {element}")
            lines.append("")
        
        lines.append("🔍 Debug commands:")
        lines.append("   vq.debug_page() - Show all interactive elements") 
        lines.append("   vq.take_screenshot() - Take screenshot for inspection")
        lines.append("   vq.get_page_source() - View page HTML")
        
        return "\n".join(lines)
    
    def auto_fix_1(self):
        """Auto-fix using first suggestion"""
        if self.suggestions and self.suggestions[0].auto_fix:
            return self.suggestions[0].auto_fix()
        raise RuntimeError("No auto-fix available for first suggestion")
    
    def auto_fix_2(self):
        """Auto-fix using second suggestion"""
        if len(self.suggestions) > 1 and self.suggestions[1].auto_fix:
            return self.suggestions[1].auto_fix()
        raise RuntimeError("No auto-fix available for second suggestion")
    
    def auto_fix_3(self):
        """Auto-fix using third suggestion"""
        if len(self.suggestions) > 2 and self.suggestions[2].auto_fix:
            return self.suggestions[2].auto_fix()
        raise RuntimeError("No auto-fix available for third suggestion")

class ElementNotFoundError(VibeQException):
    """Element not found with intelligent suggestions"""
    pass

class ActionFailedError(VibeQException):
    """Action execution failed with recovery options"""
    pass

class PageLoadError(VibeQException):
    """Page loading issues with diagnostic info"""
    pass

class ProductionErrorHandler:
    """Enterprise error handling - always helpful, never cryptic"""
    
    def __init__(self, browser, pattern_db=None):
        self.browser = browser
        self.pattern_db = pattern_db
        self.error_history = []
        
    def handle_element_not_found(self, command: str, selector: str = None) -> ElementNotFoundError:
        """Handle element not found with intelligent suggestions"""
        
        context = self._build_error_context(command)
        suggestions = self._generate_element_suggestions(command, context)
        
        error_msg = f"Could not find element for command: '{command}'"
        if selector:
            error_msg += f" (tried selector: {selector})"
        
        error = ElementNotFoundError(
            message=error_msg,
            severity=ErrorSeverity.RECOVERABLE,
            context=context,
            suggestions=suggestions
        )
        
        self._log_error(error)
        return error
    
    def handle_action_failed(self, command: str, selector: str, reason: str) -> ActionFailedError:
        """Handle action execution failure with recovery options"""
        
        context = self._build_error_context(command)
        suggestions = self._generate_action_suggestions(command, selector, reason, context)
        
        error = ActionFailedError(
            message=f"Action failed: {reason}",
            severity=ErrorSeverity.DEGRADED,
            context=context,
            suggestions=suggestions
        )
        
        self._log_error(error)
        return error
    
    def handle_page_load_error(self, url: str, timeout: int) -> PageLoadError:
        """Handle page loading issues with diagnostic suggestions"""
        
        context = VibeQErrorContext(
            command=f"navigate to {url}",
            page_url=url,
            page_title="Failed to load",
            visible_elements=[],
            similar_elements=[]
        )
        
        suggestions = [
            VibeQSuggestion(
                title="Increase timeout",
                description="Page might need more time to load",
                code_example=f"vq.set_page_load_timeout({timeout * 2})",
                confidence=0.8
            ),
            VibeQSuggestion(
                title="Check URL accessibility",
                description="Verify the URL is correct and accessible",
                code_example=f"vq.check_url_accessible('{url}')",
                confidence=0.7
            ),
            VibeQSuggestion(
                title="Wait for network idle",
                description="Wait for all network requests to complete",
                code_example="vq.wait_for_network_idle()",
                confidence=0.6
            )
        ]
        
        error = PageLoadError(
            message=f"Page failed to load within {timeout}s",
            severity=ErrorSeverity.CRITICAL,
            context=context,
            suggestions=suggestions
        )
        
        self._log_error(error)
        return error
    
    def _build_error_context(self, command: str) -> VibeQErrorContext:
        """Build rich error context for debugging"""
        
        try:
            page = self.browser.page if self.browser else None
            
            if page:
                url = page.url
                title = page.title()
                
                # Get visible interactive elements
                visible_elements = self._get_visible_elements()
                
                # Find similar elements that might be what user wanted
                similar_elements = self._find_similar_elements(command)
                
                # Take screenshot for debugging
                screenshot_path = self._take_debug_screenshot()
                
            else:
                url = "unknown"
                title = "No page loaded"
                visible_elements = []
                similar_elements = []
                screenshot_path = None
            
            return VibeQErrorContext(
                command=command,
                page_url=url,
                page_title=title,
                visible_elements=visible_elements,
                similar_elements=similar_elements,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            logger.error(f"Failed to build error context: {e}")
            return VibeQErrorContext(
                command=command,
                page_url="unknown",
                page_title="Error building context",
                visible_elements=[],
                similar_elements=[]
            )
    
    def _get_visible_elements(self) -> List[str]:
        """Get list of visible interactive elements on page"""
        
        try:
            if not self.browser.page:
                return []
            
            elements = []
            
            # Get buttons
            buttons = self.browser.page.query_selector_all("button:visible")
            for button in buttons[:10]:  # Limit to 10
                try:
                    text = button.text_content()
                    if text and text.strip():
                        elements.append(f"Button: '{text.strip()[:50]}'")
                except:
                    continue
            
            # Get links
            links = self.browser.page.query_selector_all("a:visible")
            for link in links[:10]:  # Limit to 10
                try:
                    text = link.text_content()
                    if text and text.strip():
                        elements.append(f"Link: '{text.strip()[:50]}'")
                except:
                    continue
            
            # Get inputs
            inputs = self.browser.page.query_selector_all("input:visible")
            for inp in inputs[:10]:  # Limit to 10
                try:
                    placeholder = inp.get_attribute("placeholder") or ""
                    input_type = inp.get_attribute("type") or "text"
                    name = inp.get_attribute("name") or ""
                    
                    if placeholder:
                        elements.append(f"Input: type='{input_type}', placeholder='{placeholder[:30]}'")
                    elif name:
                        elements.append(f"Input: type='{input_type}', name='{name[:30]}'")
                    else:
                        elements.append(f"Input: type='{input_type}'")
                except:
                    continue
            
            return elements[:20]  # Max 20 elements total
            
        except Exception as e:
            logger.debug(f"Failed to get visible elements: {e}")
            return []
    
    def _find_similar_elements(self, command: str) -> List[str]:
        """Find elements similar to what user is looking for"""
        
        try:
            if not self.browser.page:
                return []
            
            # Parse command to understand intent
            command_lower = command.lower()
            similar = []
            
            if "click" in command_lower:
                # Look for clickable elements with similar text
                target_text = self._extract_target_from_command(command)
                if target_text:
                    # Find buttons/links with similar text
                    all_clickable = self.browser.page.query_selector_all("button, a, [role='button']")
                    for elem in all_clickable[:20]:
                        try:
                            text = elem.text_content()
                            if text and self._text_similarity(target_text, text) > 0.5:
                                similar.append(f"Similar: '{text.strip()[:40]}'")
                        except:
                            continue
            
            elif "type" in command_lower:
                # Look for input fields with similar attributes
                target_field = self._extract_target_from_command(command)
                if target_field:
                    inputs = self.browser.page.query_selector_all("input, textarea")
                    for inp in inputs[:10]:
                        try:
                            placeholder = inp.get_attribute("placeholder") or ""
                            name = inp.get_attribute("name") or ""
                            
                            if (placeholder and target_field.lower() in placeholder.lower()) or \
                               (name and target_field.lower() in name.lower()):
                                similar.append(f"Similar field: placeholder='{placeholder[:30]}', name='{name[:20]}'")
                        except:
                            continue
            
            return similar[:5]  # Max 5 similar elements
            
        except Exception as e:
            logger.debug(f"Failed to find similar elements: {e}")
            return []
    
    def _generate_element_suggestions(self, command: str, context: VibeQErrorContext) -> List[VibeQSuggestion]:
        """Generate intelligent suggestions for element not found errors"""
        
        suggestions = []
        
        # Suggestion 1: Try similar elements found on page
        if context.similar_elements:
            similar_text = context.similar_elements[0].split("'")[1] if "'" in context.similar_elements[0] else ""
            if similar_text:
                suggestions.append(VibeQSuggestion(
                    title="Try similar element found on page",
                    description=f"Found element with similar text: {similar_text[:30]}",
                    code_example=f"vq.do(\"click '{similar_text}'\")",
                    confidence=0.8,
                    auto_fix=lambda: self._try_similar_element(command, similar_text)
                ))
        
        # Suggestion 2: Wait for element to appear
        suggestions.append(VibeQSuggestion(
            title="Wait for element to load",
            description="Element might still be loading or appear after interaction",
            code_example="vq.wait_for_element('your element', timeout=10)",
            confidence=0.7
        ))
        
        # Suggestion 3: Check if page is fully loaded
        suggestions.append(VibeQSuggestion(
            title="Ensure page is fully loaded",
            description="Page content might still be loading",
            code_example="vq.wait_for_page_load(); vq.do('your command')",
            confidence=0.6
        ))
        
        # Suggestion 4: Use debug mode to explore
        suggestions.append(VibeQSuggestion(
            title="Debug page elements",
            description="Explore what elements are available on the page",
            code_example="vq.debug_page()",
            confidence=0.9
        ))
        
        # Suggestion 5: Try alternative phrasing
        alt_command = self._suggest_alternative_phrasing(command)
        if alt_command:
            suggestions.append(VibeQSuggestion(
                title="Try alternative phrasing",
                description="Sometimes different wording works better",
                code_example=f"vq.do(\"{alt_command}\")",
                confidence=0.5
            ))
        
        return suggestions
    
    def _generate_action_suggestions(self, command: str, selector: str, reason: str, 
                                   context: VibeQErrorContext) -> List[VibeQSuggestion]:
        """Generate suggestions for action execution failures"""
        
        suggestions = []
        
        # Suggestion 1: Wait and retry
        suggestions.append(VibeQSuggestion(
            title="Wait and retry",
            description="Element might need time to become interactive",
            code_example="time.sleep(2); vq.do('your command')",
            confidence=0.7
        ))
        
        # Suggestion 2: Scroll element into view
        suggestions.append(VibeQSuggestion(
            title="Scroll to element",
            description="Element might be outside viewport",
            code_example="vq.scroll_to_element('your element'); vq.do('your command')",
            confidence=0.8
        ))
        
        # Suggestion 3: Wait for element to be enabled
        if "disabled" in reason.lower():
            suggestions.append(VibeQSuggestion(
                title="Wait for element to be enabled",
                description="Element exists but is currently disabled",
                code_example="vq.wait_for_enabled('your element')",
                confidence=0.9
            ))
        
        return suggestions
    
    def _try_similar_element(self, original_command: str, similar_text: str):
        """Auto-fix by trying similar element"""
        # This would be implemented to actually try the similar element
        # For now, return suggestion for user to try
        return f"Try: vq.do(\"click '{similar_text}'\")"
    
    def _extract_target_from_command(self, command: str) -> str:
        """Extract target text from command"""
        import re
        
        # Look for quoted text first
        quotes = re.findall(r"['\"]([^'\"]*)['\"]", command)
        if quotes:
            return quotes[0]
        
        # Look for common patterns
        command_lower = command.lower()
        words = command_lower.split()
        
        # For "click login", "type username", etc.
        if len(words) >= 2:
            return words[-1]  # Last word is usually the target
        
        return ""
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity metric"""
        text1_lower = text1.lower().strip()
        text2_lower = text2.lower().strip()
        
        if text1_lower == text2_lower:
            return 1.0
        
        if text1_lower in text2_lower or text2_lower in text1_lower:
            return 0.8
        
        # Check word overlap
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union)
        
        return 0.0
    
    def _suggest_alternative_phrasing(self, command: str) -> Optional[str]:
        """Suggest alternative phrasing for command"""
        
        command_lower = command.lower()
        
        # Common alternatives
        alternatives = {
            "click login": "click sign in",
            "click sign in": "click login", 
            "click submit": "click send",
            "type username": "type user name",
            "type password": "type pass",
            "click cart": "click shopping cart",
            "click buy": "click purchase"
        }
        
        return alternatives.get(command_lower)
    
    def _take_debug_screenshot(self) -> Optional[str]:
        """Take screenshot for debugging"""
        try:
            if self.browser.page:
                import time
                timestamp = int(time.time())
                screenshot_path = f"vibeq_debug_{timestamp}.png"
                self.browser.page.screenshot(path=screenshot_path)
                return screenshot_path
        except Exception as e:
            logger.debug(f"Failed to take debug screenshot: {e}")
        
        return None
    
    def _log_error(self, error: VibeQException):
        """Log error for analytics and monitoring"""
        self.error_history.append({
            'timestamp': time.time(),
            'error_type': type(error).__name__,
            'command': error.context.command,
            'page_url': error.context.page_url,
            'severity': error.severity.value
        })
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        # Log to system logger
        logger.error(f"VibeQ Error: {error.message} | Command: {error.context.command} | Page: {error.context.page_url}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        if not self.error_history:
            return {'total_errors': 0}
        
        from collections import Counter
        
        error_types = Counter(e['error_type'] for e in self.error_history)
        severities = Counter(e['severity'] for e in self.error_history)
        
        return {
            'total_errors': len(self.error_history),
            'error_types': dict(error_types),
            'severities': dict(severities),
            'recent_errors': self.error_history[-5:]  # Last 5 errors
        }
