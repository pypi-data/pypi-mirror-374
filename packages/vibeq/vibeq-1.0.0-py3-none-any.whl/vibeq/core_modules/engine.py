"""
VibeQ Core Engine - Universal orchestration for any website
Coordinates CommandParser, UniversalElementFinder, and ActionExecutor
"""
import logging
from typing import Optional, Dict, Any
from .command_parser import CommandParser
from .universal_element_finder import UniversalElementFinder
from .action_executor import ActionExecutor

logger = logging.getLogger(__name__)
import logging
import time
from typing import Optional, List

from .command_parser import CommandParser, Intent
from .element_finder import ElementFinder
from .action_executor import ActionExecutor

logger = logging.getLogger(__name__)

class VibeQCore:
    """Core engine that orchestrates universal automation"""
    
    def __init__(self, browser, intelligence=None):
        self.browser = browser
        self.intelligence = intelligence
        
        # Initialize universal components
        self.command_parser = CommandParser()
        self.element_finder = UniversalElementFinder(browser, intelligence)
        self.action_executor = ActionExecutor(browser)
        
        logger.info("🚀 VibeQCore initialized with universal components")
    
    def execute_command(self, command: str) -> bool:
        """Execute a natural language command"""
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        start_time = time.time()
        logger.info(f"📝 EXECUTING: {command}")
        
        try:
            # Step 1: Parse command into intent
            intent = self.parser.parse(command)
            logger.info(f"🧠 Parsed intent: {intent.verb} '{intent.target}'")
            
                        # Step 2: Find element selector
            selector = self.element_finder.find_for_intent(intent)
            if selector:
                logger.info(f"🎯 Found selector: {selector}")
            
            # Step 3: Execute the action
            success = self.action_executor.execute(intent, selector)
            
            # Record outcome for AI learning
            if self.intelligence:
                page_context = self.element_finder._get_page_context()
                self.intelligence.record_outcome(command, page_context, success=success)
            
            # Analytics tracking (removed - not available in universal version)
            execution_time = time.time() - start_time
            logger.debug(f"⏱️ Execution time: {execution_time:.2f}s")
            
            if success:
                logger.info(f"✅ Command completed successfully")
            else:
                logger.error(f"❌ Command failed")
                
                if self.screenshot_on_failure:
                    self._take_failure_screenshot()
            
            return success
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            if self.screenshot_on_failure:
                self._take_failure_screenshot()
            return False
    
    def execute_multi_step(self, command: str) -> bool:
        """Execute commands that might have multiple steps"""
        steps = self.command_parser.break_into_steps(command)
        
        if len(steps) == 1:
            return self.execute_command(command)
        
        logger.info(f"🔄 Multi-step command: {len(steps)} steps")
        for i, step in enumerate(steps, 1):
            logger.info(f"📝 Step {i}: {step}")
            if not self.execute_command(step):
                logger.error(f"❌ Step {i} failed, stopping execution")
                return False
        
        logger.info("✅ All steps completed successfully")
        return True
    
    def check_condition(self, condition: str) -> bool:
        """Check if a condition is met on the page"""
        try:
            # Simple implementation - could be expanded with AI
            if "visible" in condition.lower():
                text_to_find = condition.split("'")[1] if "'" in condition else ""
                if text_to_find and hasattr(self.browser, 'page'):
                    elements = self.browser.page.locator(f"text={text_to_find}")
                    return elements.count() > 0
            return False
        except Exception as e:
            logger.error(f"Condition check failed: {e}")
            return False
    
    def _take_failure_screenshot(self):
        """Take a screenshot on failure"""
        try:
            if hasattr(self.browser, 'screenshot'):
                filename = f"failure_{int(time.time())}.png"
                path = self.browser.screenshot(filename)
                logger.info(f"📸 Failure screenshot: {path}")
        except Exception as e:
            logger.debug(f"Screenshot failed: {e}")
    
    def get_page_info(self) -> dict:
        """Get current page information"""
        try:
            if hasattr(self.browser, 'page') and self.browser.page:
                return {
                    'url': self.browser.page.url,
                    'title': self.browser.page.title(),
                    'ready_state': 'complete'
                }
        except Exception:
            pass
        return {'url': 'unknown', 'title': 'unknown', 'ready_state': 'unknown'}
