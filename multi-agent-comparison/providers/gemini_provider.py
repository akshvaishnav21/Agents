import json
import google.generativeai as genai
from google.generativeai.types import content_types
from .base import LLMProvider, LLMResponse, ToolCall

DEFAULT_MODEL = "gemini-1.5-pro"


class GeminiProvider(LLMProvider):
    """Gemini models via the Google Generative AI API."""

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        # Reads GOOGLE_API_KEY from environment automatically

    def complete(self, system, messages, tools, max_tokens=2048) -> LLMResponse:
        gemini_tools = [_anthropic_tools_to_gemini(tools)] if tools else None

        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system,
            tools=gemini_tools,
        )

        history, last_user = _split_history_and_last(messages)
        chat = model.start_chat(history=history)

        response = chat.send_message(
            last_user,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
        )
        return _from_gemini_response(response)


# ── translation helpers ───────────────────────────────────────────────────────

def _anthropic_tools_to_gemini(tools: list[dict]) -> genai.protos.Tool:
    """Convert a list of Anthropic tool schemas to a single Gemini Tool object."""
    declarations = []
    for t in tools:
        schema = t.get("input_schema", {})
        # Gemini expects properties without additionalProperties
        properties = {}
        for name, prop in schema.get("properties", {}).items():
            properties[name] = genai.protos.Schema(
                type=_json_type(prop.get("type", "string")),
                description=prop.get("description", ""),
                enum=prop.get("enum", []) or [],
            )

        declarations.append(
            genai.protos.FunctionDeclaration(
                name=t["name"],
                description=t.get("description", ""),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties=properties,
                    required=schema.get("required", []),
                ),
            )
        )
    return genai.protos.Tool(function_declarations=declarations)


def _json_type(t: str) -> "genai.protos.Type":
    return {
        "string":  genai.protos.Type.STRING,
        "number":  genai.protos.Type.NUMBER,
        "integer": genai.protos.Type.INTEGER,
        "boolean": genai.protos.Type.BOOLEAN,
        "array":   genai.protos.Type.ARRAY,
        "object":  genai.protos.Type.OBJECT,
    }.get(t, genai.protos.Type.STRING)


def _split_history_and_last(messages: list[dict]) -> tuple[list, str]:
    """
    Gemini's start_chat() takes history (all but the last user message)
    and send_message() takes the final user content.
    """
    history = []
    i = 0
    while i < len(messages):
        msg = messages[i]

        if msg["role"] == "user":
            # Check if this is the last message
            if i == len(messages) - 1:
                return history, msg["content"]
            history.append({"role": "user", "parts": [msg["content"]]})
            i += 1

        elif msg["role"] == "assistant":
            parts = []
            if msg.get("content"):
                parts.append(msg["content"])
            for tc in msg.get("tool_calls", []):
                parts.append(genai.protos.Part(
                    function_call=genai.protos.FunctionCall(
                        name=tc["name"],
                        args=tc["input"],
                    )
                ))
            history.append({"role": "model", "parts": parts})
            i += 1

        elif msg["role"] == "tool":
            # Collect consecutive tool results as function_response parts
            parts = []
            while i < len(messages) and messages[i]["role"] == "tool":
                t = messages[i]
                parts.append(genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=t.get("name", "tool"),
                        response={"result": t["content"]},
                    )
                ))
                i += 1
            history.append({"role": "user", "parts": parts})

        else:
            i += 1

    # Fallback — should not normally be reached
    return history[:-1], history[-1]["parts"][0] if history else ""


def _from_gemini_response(response) -> LLMResponse:
    text = None
    tool_calls = []

    for part in response.parts:
        if hasattr(part, "text") and part.text:
            text = part.text
        elif hasattr(part, "function_call") and part.function_call.name:
            fc = part.function_call
            tool_calls.append(ToolCall(
                id=fc.name,           # Gemini has no ID; use name as ID
                name=fc.name,
                input=dict(fc.args),
            ))

    stop_reason = "tool_use" if tool_calls else "end_turn"
    return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason)
