import json
import openai
from .base import LLMProvider, LLMResponse, ToolCall

DEFAULT_MODEL = "gpt-4o"


class OpenAIProvider(LLMProvider):
    """GPT models via the OpenAI API."""

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        self._client: openai.OpenAI | None = None

    def _get_client(self) -> openai.OpenAI:
        if self._client is None:
            self._client = openai.OpenAI()
        return self._client

    def complete(self, system, messages, tools, max_tokens=2048) -> LLMResponse:
        native_messages = [{"role": "system", "content": system}]
        native_messages += _to_openai_messages(messages)

        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            messages=native_messages,
        )
        if tools:
            kwargs["tools"] = [_anthropic_tool_to_openai(t) for t in tools]

        response = self._get_client().chat.completions.create(**kwargs)
        return _from_openai_response(response)


# ── translation helpers ───────────────────────────────────────────────────────

def _to_openai_messages(messages: list[dict]) -> list[dict]:
    result = []
    for msg in messages:
        if msg["role"] == "user":
            result.append({"role": "user", "content": msg["content"]})

        elif msg["role"] == "assistant":
            m = {"role": "assistant", "content": msg.get("content") or None}
            if msg.get("tool_calls"):
                m["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["input"]),
                        },
                    }
                    for tc in msg["tool_calls"]
                ]
            result.append(m)

        elif msg["role"] == "tool":
            result.append({
                "role": "tool",
                "tool_call_id": msg["tool_call_id"],
                "content": msg["content"],
            })

    return result


def _anthropic_tool_to_openai(tool: dict) -> dict:
    """Convert Anthropic tool schema to OpenAI function tool schema."""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


def _from_openai_response(response) -> LLMResponse:
    choice = response.choices[0]
    message = choice.message

    text = message.content
    tool_calls = []
    if message.tool_calls:
        for tc in message.tool_calls:
            tool_calls.append(ToolCall(
                id=tc.id,
                name=tc.function.name,
                input=json.loads(tc.function.arguments),
            ))

    stop_reason = "tool_use" if choice.finish_reason == "tool_calls" else "end_turn"
    return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason)
