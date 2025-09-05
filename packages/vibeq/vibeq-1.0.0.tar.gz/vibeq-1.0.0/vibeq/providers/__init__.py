"""Provider adapters for AI services (OpenAI, Anthropic, Grok).

OpenAI provider exists; placeholders for others are provided to make the
API stable for consumers.
"""

from .openai import OpenAIProvider

try:
    from .anthropic import AnthropicProvider  # type: ignore
except Exception:  # pragma: no cover
    AnthropicProvider = None

try:
    from .grok import GrokProvider  # type: ignore
except Exception:  # pragma: no cover
    GrokProvider = None

__all__ = ["OpenAIProvider", "AnthropicProvider", "GrokProvider"]
