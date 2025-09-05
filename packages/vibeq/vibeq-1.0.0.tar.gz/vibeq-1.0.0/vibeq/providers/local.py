"""Local AI provider for VibeQ - supports Ollama, LM Studio, and other local models."""

import json
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalProvider:
    """Provider for local AI models (Ollama, LM Studio, etc.)"""
    
    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.2:latest"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self._validate_connection()
    
    def _validate_connection(self):
        """Validate connection to local AI service"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Local AI service responded with {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to local AI service at {self.base_url}: {e}")
    
    def generate_selectors(self, command: str, page_context: str = "") -> List[str]:
        """Generate CSS selectors for a natural language command using local AI"""
        try:
            prompt = self._build_selector_prompt(command, page_context)
            response = self._call_local_model(prompt)
            
            # Parse selectors from response
            selectors = self._parse_selectors_response(response)
            if selectors:
                logger.info(f"🤖 Local AI ({self.model}): {', '.join(selectors[:3])}")
                return selectors
            
            # Fallback to basic selectors if AI fails
            return self._fallback_selectors(command)
            
        except Exception as e:
            logger.warning(f"Local AI failed: {e}")
            return self._fallback_selectors(command)
    
    def _call_local_model(self, prompt: str) -> str:
        """Make API call to local model"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert web automation assistant. Generate CSS selectors for user commands."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 200
        }
        
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        
        raise Exception("No response from local model")
    
    def _build_selector_prompt(self, command: str, context: str = "") -> str:
        """Build prompt for selector generation"""
        return f"""Generate CSS selectors for this web automation command: "{command}"

Context: {context if context else "Standard web page"}

Return 3-5 CSS selectors in order of reliability, one per line. Examples:
button[type="submit"]
.login-button
#submit-btn
input[value*="Submit"]
form button:last-child

Command: {command}
Selectors:"""
    
    def _parse_selectors_response(self, response: str) -> List[str]:
        """Parse CSS selectors from AI response"""
        selectors = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # Clean up common prefixes
                if line.startswith('- '):
                    line = line[2:]
                if line.startswith('* '):
                    line = line[2:]
                if line and len(line) < 200:  # Reasonable selector length
                    selectors.append(line)
        return selectors[:5]  # Limit to top 5
    
    def _fallback_selectors(self, command: str) -> List[str]:
        """Generate basic fallback selectors when AI fails"""
        cmd_lower = command.lower()
        
        if 'login' in cmd_lower:
            return ['button[type="submit"]', '.login-btn', '#login', 'input[value*="Login"]']
        elif 'submit' in cmd_lower:
            return ['button[type="submit"]', 'input[type="submit"]', '.submit-btn', '#submit']
        elif 'click' in cmd_lower:
            return ['button', '.btn', 'a', 'input[type="button"]']
        elif 'type' in cmd_lower or 'input' in cmd_lower:
            return ['input[type="text"]', 'input[type="email"]', 'input[type="password"]', 'textarea']
        else:
            return ['button', 'a', 'input', '.btn']
    
    def get_confidence_score(self) -> float:
        """Return confidence score for this provider"""
        return 0.7  # Local models typically less reliable than cloud APIs
    
    def check_element_visibility(self, selector: str, page_context: str) -> bool:
        """Simple visibility check - local models may not have vision capabilities"""
        # Local models typically don't have vision, so we return True
        # and rely on browser-based visibility checks
        return True
    
    def __str__(self):
        return f"LocalProvider(model={self.model}, endpoint={self.base_url})"
