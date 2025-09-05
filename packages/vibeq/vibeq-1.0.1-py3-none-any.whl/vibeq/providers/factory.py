"""Provider factory and failover logic for VibeQ AI providers."""

import os
import logging
from typing import Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .grok import GrokProvider


class ProviderFactory:
    """Factory for creating AI providers with automatic failover."""
    
    @staticmethod
    def _load_dotenv_if_present():
        """Minimal .env loader (no external deps). Does not overwrite existing env vars."""
        try:
            # Search workspace root (two levels up from this file) and CWD
            candidates = []
            try:
                here = Path(__file__).resolve()
                candidates.append(here.parents[2] / ".env")  # project root
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
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v and k not in os.environ:
                            os.environ[k] = v
                    break
        except Exception:
            pass

    @staticmethod
    def _normalize_key(key: Optional[str]) -> Optional[str]:
        if not key:
            return key
        k = key.strip()
        if k.lower().startswith('bearer '):
            k = k[len('bearer '):].strip()
        return k
    
    @staticmethod
    def create_provider(
        provider_name: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        ai_endpoint: Optional[str] = None
    ) -> Union[OpenAIProvider, AnthropicProvider, GrokProvider]:
        """Create appropriate provider based on name and available keys."""
        # Load .env once to populate env vars if not already set
        ProviderFactory._load_dotenv_if_present()

        if provider_name == "auto":
            # Auto-detect based on available environment variables
            if api_key:
                # Use provided key, detect provider type
                api_key = ProviderFactory._normalize_key(api_key)
                if api_key and "sk-" in api_key:
                    provider_name = "openai"
                elif api_key and ("claude" in api_key.lower() or "anthropic" in api_key.lower()):
                    provider_name = "anthropic"
                else:
                    provider_name = "grok"
            else:
                # Check environment variables in priority order
                if os.getenv("OPENAI_API_KEY"):
                    provider_name = "openai"
                    api_key = os.getenv("OPENAI_API_KEY")
                elif os.getenv("ANTHROPIC_API_KEY"):
                    provider_name = "anthropic"
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                elif os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY"):
                    provider_name = "grok"
                    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
                elif ProviderFactory._check_local_model():
                    provider_name = "local"
                    api_key = "local"  # Placeholder for local models
                else:
                    raise RuntimeError("No AI provider detected. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, GROK_API_KEY, or run a local model")
        
        # Handle special providers
        if provider_name.lower() in ("local", "custom"):
            return ProviderFactory._create_local_provider(provider_name, ai_endpoint, model)
        
        # If provider specified but no API key provided, try to get from environment
        if not api_key:
            if provider_name.lower() == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider_name.lower() in ("anthropic", "claude"):
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider_name.lower() in ("grok", "xai"):
                api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        
        api_key = ProviderFactory._normalize_key(api_key)

        if not api_key:
            raise ValueError(f"API key required for {provider_name} provider")
            
        if provider_name.lower() == "openai":
            return OpenAIProvider(
                api_key=api_key,
                model=model or "gpt-4o-mini",
                base_url=ai_endpoint  # Allow custom OpenAI-compatible endpoints
            )
        elif provider_name.lower() in ("anthropic", "claude"):
            return AnthropicProvider(
                api_key=api_key,
                model=model or "claude-3-haiku-20240307"
            )
        elif provider_name.lower() in ("grok", "xai"):
            return GrokProvider(
                api_key=api_key,
                model=model or "grok-beta"
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    @staticmethod
    def _check_local_model() -> bool:
        """Check if local AI model is available"""
        import requests
        try:
            endpoints = [
                "http://localhost:11434",  # Ollama
                "http://localhost:1234",   # LM Studio  
                "http://localhost:8000",   # Common local AI
                "http://localhost:5000",   # Alternative port
            ]
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{endpoint}/api/tags", timeout=2)
                    if response.status_code == 200:
                        return True
                except:
                    # Try alternative health check endpoints
                    try:
                        response = requests.get(f"{endpoint}/v1/models", timeout=2)
                        if response.status_code == 200:
                            return True
                    except:
                        continue
        except:
            pass
        return False
    
    @staticmethod  
    def _create_local_provider(provider_name: str, endpoint: Optional[str] = None, model: Optional[str] = None):
        """Create provider for local models"""
        from .local import LocalProvider  # Import here to avoid circular imports
        
        if not endpoint:
            # Auto-detect local endpoint
            endpoints = [
                "http://localhost:11434/v1",  # Ollama
                "http://localhost:1234/v1",   # LM Studio
                "http://localhost:8000/v1",   # Common
            ]
            for ep in endpoints:
                try:
                    import requests
                    response = requests.get(f"{ep}/models", timeout=2)
                    if response.status_code == 200:
                        endpoint = ep
                        break
                except:
                    continue
            
            if not endpoint:
                raise RuntimeError("No local AI model endpoint detected. Please specify ai_endpoint parameter.")
        
        return LocalProvider(
            base_url=endpoint,
            model=model or "llama3.2:latest"  # Common default
        )


class MultiProvider:
    """Multi-provider with automatic failover."""
    
    def __init__(self, primary_provider: str = "auto", fallback_providers: list = None):
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or ["openai", "anthropic", "grok"]
        self._providers = {}
        
    def analyze(self, prompt: str) -> str:
        """Analyze with primary provider, fall back to others on failure."""
        
        # Try primary provider first
        try:
            if self.primary_provider not in self._providers:
                self._providers[self.primary_provider] = ProviderFactory.create_provider(
                    self.primary_provider
                )
            return self._providers[self.primary_provider].analyze(prompt)
        except Exception as e:
            logger.warning(f"Primary provider {self.primary_provider} failed: {e}")
            
        # Try fallback providers
        for provider_name in self.fallback_providers:
            if provider_name == self.primary_provider:
                continue  # Already tried
                
            try:
                if provider_name not in self._providers:
                    self._providers[provider_name] = ProviderFactory.create_provider(
                        provider_name
                    )
                result = self._providers[provider_name].analyze(prompt)
                logger.info(f"Fallback provider {provider_name} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Fallback provider {provider_name} failed: {e}")
                continue
                
        raise RuntimeError("All AI providers failed")
