import anthropic
from .base import LLMProvider, LLMResponse, ToolCall

DEFAULT_MODEL = "claude-opus-4-6"


class AnthropicProvider(LLMProvider):
    """Claude via the Anthropic API."""

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        self._client = anthropic.Anthropic()

    def complete(self, system, messages, tools, max_tokens=2048) -> LLMResponse:
        native_messages = _to_anthropic_messages(messages)
        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=native_messages,
        )
        if tools:
            kwargs["tools"] = tools  # already in Anthropic format

        response = self._client.messages.create(**kwargs)
        return _from_anthropic_response(response)


# ── translation helpers ───────────────────────────────────────────────────────

def _to_anthropic_messages(messages: list[dict]) -> list[dict]:
    """
    Convert normalized messages to Anthropic's format.

    Tricky parts:
    - assistant tool_calls → content blocks of type tool_use
    - consecutive tool results → merged into a single user message as tool_result blocks
    """
    result = []
    i = 0
    while i < len(messages):
        msg = messages[i]

        if msg["role"] == "user":
            result.append({"role": "user", "content": msg["content"]})
            i += 1

        elif msg["role"] == "assistant":
            content_blocks = []
            if msg.get("content"):
                content_blocks.append({"type": "text", "text": msg["content"]})
            for tc in msg.get("tool_calls", []):
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                })
            result.append({"role": "assistant", "content": content_blocks})
            i += 1

        elif msg["role"] == "tool":
            # Collect all consecutive tool results into one user message
            tool_blocks = []
            while i < len(messages) and messages[i]["role"] == "tool":
                t = messages[i]
                tool_blocks.append({
                    "type": "tool_result",
                    "tool_use_id": t["tool_call_id"],
                    "content": t["content"],
                })
                i += 1
            result.append({"role": "user", "content": tool_blocks})

        else:
            i += 1

    return result


def _from_anthropic_response(response) -> LLMResponse:
    text = None
    tool_calls = []
    for block in response.content:
        if block.type == "text":
            text = block.text
        elif block.type == "tool_use":
            tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))

    stop_reason = "tool_use" if response.stop_reason == "tool_use" else "end_turn"
    return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason)
