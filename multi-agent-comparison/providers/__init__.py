"""
Provider registry with lazy imports — each SDK is only loaded when that
provider is actually requested, so missing optional dependencies don't break
the other providers.
"""
from .base import LLMProvider, LLMResponse, ToolCall

PROVIDERS = {
    "anthropic": ("claude-opus-4-6",    "providers.anthropic_provider", "AnthropicProvider"),
    "openai":    ("gpt-4o",             "providers.openai_provider",    "OpenAIProvider"),
    "gemini":    ("gemini-1.5-pro",     "providers.gemini_provider",    "GeminiProvider"),
}

ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai":    "OPENAI_API_KEY",
    "gemini":    "GOOGLE_API_KEY",
}


def get_provider(name: str, model: str | None = None) -> LLMProvider:
    """
    Factory — lazily imports and returns the requested provider.

    Args:
        name:  "anthropic" | "openai" | "gemini"
        model: Override the default model. Defaults per provider:
               anthropic → claude-opus-4-6
               openai    → gpt-4o
               gemini    → gemini-1.5-pro
    """
    if name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{name}'. "
            f"Choose from: {', '.join(PROVIDERS)}"
        )
    default_model, module_path, class_name = PROVIDERS[name]
    import importlib
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        pkg = {"anthropic": "anthropic", "openai": "openai",
               "gemini": "google-generativeai"}[name]
        raise ImportError(
            f"Cannot load '{name}' provider. "
            f"Install the SDK with: pip install {pkg}"
        ) from e
    cls = getattr(module, class_name)
    return cls(model or default_model)


__all__ = [
    "LLMProvider", "LLMResponse", "ToolCall",
    "get_provider", "PROVIDERS", "ENV_VARS",
]
