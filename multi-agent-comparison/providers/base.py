"""
Shared data types and abstract base class for all LLM providers.

Normalized message format (used throughout all agents):
  user:      {"role": "user",      "content": "text"}
  assistant: {"role": "assistant", "content": "text or None",
              "tool_calls": [{"id": "...", "name": "...", "input": {...}}]}
  tool:      {"role": "tool", "tool_call_id": "...", "content": "result text"}

Each provider's complete() translates from/to this format internally.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"   # "end_turn" | "tool_use"


class LLMProvider(ABC):
    """Abstract LLM provider. Accepts normalized messages, returns LLMResponse."""

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def complete(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Send a completion request.

        Args:
            system:    System prompt string.
            messages:  Normalized message list (see module docstring).
            tools:     Tool definitions in Anthropic schema format.
                       Each provider translates these to its own format.
            max_tokens: Maximum tokens in the response.

        Returns:
            LLMResponse with normalized text, tool_calls, and stop_reason.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"
