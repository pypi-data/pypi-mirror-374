"""
VibeQ - AI-Native Browser Automation
Production-ready with WebDriver compatibility
"""
import os
from pathlib import Path

def _load_dotenv_early():
	try:
		# Try project root and CWD
		candidates = []
		try:
			here = Path(__file__).resolve()
			candidates.append(here.parents[1] / ".env")
			candidates.append(here.parents[2] / ".env")
		except Exception:
			pass
		candidates.append(Path.cwd() / ".env")
		for env_path in candidates:
			if env_path and env_path.exists():
				for line in env_path.read_text(encoding="utf-8").splitlines():
					line = line.strip()
					if not line or line.startswith('#') or '=' not in line:
						continue
					k, v = line.split('=', 1)
					k = k.strip(); v = v.strip().strip('"').strip("'")
					if k and v and k not in os.environ:
						os.environ[k] = v
				break
		# Normalize Bearer prefix if present
		for key_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROK_API_KEY", "XAI_API_KEY"):
			v = os.environ.get(key_name)
			if v and v.lower().startswith('bearer '):
				os.environ[key_name] = v[len('bearer '):].strip()
	except Exception:
		pass

_load_dotenv_early()

"""
VibeQ - Universal AI-Native Test Automation
Enhanced with advanced AI-powered element detection and WebDriver compatibility
"""

from .core import VibeQCore

class VibeQ(VibeQCore):
    """
    VibeQ - AI-Native Browser Automation
    
    Usage:
    Auto-detect AI provider:
        vq = VibeQ()  # Auto-detects from environment
        vq = VibeQ(ai_provider="auto")  # Explicit auto-detect
    
    Specific AI providers:
        vq = VibeQ(ai_provider="openai")     # OpenAI GPT-4
        vq = VibeQ(ai_provider="anthropic")  # Claude
        vq = VibeQ(ai_provider="grok")       # Grok
        vq = VibeQ(ai_provider="local")      # Local model (Ollama)
    
    Custom configurations:
        vq = VibeQ(ai_provider="custom", ai_endpoint="http://localhost:1234/v1")
        vq = VibeQ(ai_provider="openai", api_key="custom-key")
    
    WebDriver Compatible:
        vq.launch_browser()
        vq.execute_script("window.scrollTo(0, 500)")
        vq.wait_until("button is clickable")
    """
    
    def __init__(self, provider: str = "auto", ai_provider: str = None, **kwargs):
        """Initialize VibeQ with flexible AI provider auto-detection"""
        
        # Handle legacy parameter names and new flexible options
        if ai_provider:
            provider = ai_provider
        
        # Auto-detect best available provider if requested
        if provider == "auto":
            provider = self._auto_detect_provider()
        
        super().__init__(provider=provider, **kwargs)
    
    def _auto_detect_provider(self) -> str:
        """Auto-detect the best available AI provider from environment"""
        import os
        
        # Check for API keys in order of preference
        if os.getenv('OPENAI_API_KEY'):
            return "openai"
        elif os.getenv('ANTHROPIC_API_KEY'):
            return "anthropic"
        elif os.getenv('GROK_API_KEY'):
            return "grok"
        elif self._check_local_model():
            return "local"
        else:
            # Fallback to openai and let user know they need to set API key
            print("⚠️  No AI provider detected. Please set OPENAI_API_KEY or other provider API key.")
            print("   Run 'vibeq setup' for configuration help.")
            return "openai"
    
    def _check_local_model(self) -> bool:
        """Check if local AI model is available (Ollama, LM Studio, etc.)"""
        import requests
        try:
            # Check common local AI endpoints
            endpoints = [
                "http://localhost:11434",  # Ollama
                "http://localhost:1234",   # LM Studio
                "http://localhost:8000",   # Common local AI
            ]
            for endpoint in endpoints:
                response = requests.get(f"{endpoint}/api/tags", timeout=1)
                if response.status_code == 200:
                    return True
        except:
            pass
        return False
    
    # Alias methods for different naming conventions
    def start(self, **kwargs):
        """Alias for launch_browser - backward compatibility"""
        return self.launch_browser(**kwargs)
    
    def navigate_to(self, url: str):
        """Alias for go_to - WebDriver style"""
        return self.go_to(url)
    
    def find_element(self, selector: str):
        """WebDriver style element finding"""
        return self.do(f"find {selector}")
    
    def send_keys(self, element: str, text: str):
        """WebDriver style text input"""
        return self.do(f"type {text} in {element}")
    
    def click_element(self, element: str):
        """WebDriver style clicking"""
        return self.do(f"click {element}")
    
    # Screenshot methods
    def take_screenshot(self, filename: str = None) -> bool:
        """Take screenshot - enhanced from core"""
        if not hasattr(self, 'webdriver') or not self.webdriver:
            return False
            
        if filename:
            return self.webdriver.save_screenshot(filename)
        else:
            # Auto-generate filename with timestamp
            import time
            filename = f"vibeq_screenshot_{int(time.time())}.png"
            return self.webdriver.save_screenshot(filename)
    
    def save_screenshot(self, filename: str) -> bool:
        """WebDriver compatible screenshot method"""
        return self.take_screenshot(filename)


# Aliases for different import styles  
WebDriver = VibeQ  # For Selenium migrants
Browser = VibeQ     # For Playwright migrants
Automation = VibeQ  # Generic alias

__version__ = "1.0.0"
__all__ = ["VibeQ"]
