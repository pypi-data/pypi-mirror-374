"""
Command Parser - Converts natural language to actionable intents
Part of VibeQ's AI-native architecture
"""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    """Parsed command intent"""
    verb: str  # click, type, navigate, etc.
    target: str  # element description
    value: Optional[str] = None  # text to type, URL to navigate
    modifiers: Dict[str, Any] = None  # additional context

class CommandParser:
    """Parse natural language commands into structured intents"""
    
    def __init__(self):
        self.verb_patterns = {
            'click': ['click', 'press', 'tap', 'select', 'choose'],
            'type': ['type', 'enter', 'input', 'fill'],
            'navigate': ['go to', 'navigate to', 'open', 'visit'],
            'wait': ['wait for', 'wait until'],
            'verify': ['check', 'verify', 'ensure', 'confirm']
        }
    
    def parse(self, command: str) -> Intent:
        """Parse a natural language command into an Intent"""
        command_lower = command.lower().strip()
        
        # Extract verb
        verb = self._extract_verb(command_lower)
        
        # Extract target and value based on verb
        if verb == 'type':
            target, value = self._parse_type_command(command, command_lower)
        elif verb == 'navigate':
            target, value = self._parse_navigate_command(command, command_lower)
        elif verb == 'click':
            target, value = self._parse_click_command(command, command_lower)
        else:
            target = command
            value = None
        
        return Intent(
            verb=verb,
            target=target,
            value=value,
            modifiers={}
        )
    
    def _extract_verb(self, command_lower: str) -> str:
        """Determine the primary action verb"""
        for verb, patterns in self.verb_patterns.items():
            if any(pattern in command_lower for pattern in patterns):
                return verb
        return 'click'  # default
    
    def _parse_type_command(self, command: str, command_lower: str) -> tuple:
        """Parse typing commands like 'type X into Y'"""
        if ' into ' in command_lower:
            parts = command.split(' into ', 1)
            value = parts[0].split(' ', 1)[1].strip().strip("'\"")  # Remove 'type' prefix
            target = parts[1].strip()
            return target, value
        elif ' in ' in command_lower:
            parts = command.split(' in ', 1) 
            value = parts[0].split(' ', 1)[1].strip().strip("'\"")
            target = parts[1].strip()
            return target, value
        else:
            # Simple type command
            words = command.split()
            if len(words) > 1:
                value = ' '.join(words[1:]).strip("'\"")
                return "input field", value
            return "input field", ""
    
    def _parse_navigate_command(self, command: str, command_lower: str) -> tuple:
        """Parse navigation commands"""
        for pattern in self.verb_patterns['navigate']:
            if pattern in command_lower:
                url = command.split(pattern, 1)[1].strip()
                return "page", url
        return "page", command
    
    def _parse_click_command(self, command: str, command_lower: str) -> tuple:
        """Parse click commands"""
        # Handle add to cart specially
        if 'add to cart' in command_lower or 'add to bag' in command_lower:
            if ' for ' in command_lower:
                product = command.split(' for ', 1)[1].strip()
                return f"add to cart for {product}", None
            else:
                return "add to cart", None
        
        # Remove click prefix to get target
        for pattern in self.verb_patterns['click']:
            if command_lower.startswith(pattern + ' '):
                target = command[len(pattern):].strip()
                return target, None
        
        return command, None
    
    def break_into_steps(self, command: str) -> List[str]:
        """Break complex commands into simple steps"""
        steps = []
        command_lower = command.lower()
        
        # Handle connectors
        if ' and then ' in command or ' then ' in command:
            parts = command.replace(' and then ', ' | ').replace(' then ', ' | ').split(' | ')
            return [part.strip() for part in parts if part.strip()]
        
        if ' and ' in command:
            parts = command.split(' and ')
            return [part.strip() for part in parts if part.strip()]
        
        return [command]
