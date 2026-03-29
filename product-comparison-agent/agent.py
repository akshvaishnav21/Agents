import anthropic
from tools import web_search, WEB_SEARCH_TOOL

SYSTEM_PROMPT = """You are a consumer product comparison expert. When asked to compare two products:

1. Search for specs, pricing, and reviews for EACH product individually
2. Search for head-to-head comparisons if available
3. Synthesize everything into a clear, structured report

Your final output MUST follow this exact format:

## [Product A] vs [Product B] — Full Comparison

| Feature       | [Product A]  | [Product B]  |
|---------------|--------------|--------------|
| Display       | ...          | ...          |
| Camera        | ...          | ...          |
| Battery       | ...          | ...          |
| Processor     | ...          | ...          |
| RAM / Storage | ...          | ...          |
| OS            | ...          | ...          |
| Price         | ...          | ...          |

### [Product A] — Pros & Cons
**Pros:** bullet points
**Cons:** bullet points

### [Product B] — Pros & Cons
**Pros:** bullet points
**Cons:** bullet points

### Verdict
Who should buy [Product A] and who should buy [Product B]. Keep it practical and opinionated.
"""


def run_comparison_agent(user_query: str) -> str:
    """Run the agentic comparison loop and return the final markdown report."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[WEB_SEARCH_TOOL],
            messages=messages,
        )

        # Append assistant turn to conversation history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "Could not generate comparison."

        if response.stop_reason != "tool_use":
            break

        # Execute all tool calls Claude requested
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                query = block.input.get("query", "")
                print(f"  Searching: \"{query}\"")
                result = web_search(query)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})

    return "Comparison could not be completed."
