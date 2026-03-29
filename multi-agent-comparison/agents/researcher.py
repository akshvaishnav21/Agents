"""
Researcher Agent — scoped to a single product.

Runs an agentic loop using the injected LLMProvider, then outputs a
structured ResearchResult as JSON in its final text block.
"""
import json
from schemas import ResearchResult
from memory import MemoryStore
from tools import web_search, WEB_SEARCH_TOOL
from display import print_search, print_agent_done
from providers import LLMProvider

SYSTEM_PROMPT = """\
You are a product research specialist. Your only job is to gather factual information
about ONE specific product: {product_name}.

Research these areas: {focus_areas}

Use web_search to find accurate, up-to-date data. Make 3–5 targeted searches.

When you have enough data, output ONLY a JSON object in this exact format
(no markdown fences, no extra text before or after):

{{
  "product_name": "{product_name}",
  "specs": {{
    "Display": "...",
    "Camera": "...",
    "Battery": "...",
    "Processor": "...",
    "RAM / Storage": "...",
    "OS": "..."
  }},
  "pricing": "Starting price and variants",
  "reviews_summary": "2-3 sentence summary of expert consensus",
  "key_findings": [
    "Finding 1",
    "Finding 2",
    "Finding 3"
  ],
  "searches_performed": ["query 1", "query 2"]
}}
"""


def run_researcher(
    product_name: str,
    focus_areas: list[str],
    memory_store: MemoryStore,
    provider: LLMProvider,
    agent_label: str = "Researcher",
) -> ResearchResult:
    system = SYSTEM_PROMPT.format(
        product_name=product_name,
        focus_areas=", ".join(focus_areas),
    )
    messages = [{"role": "user", "content": f"Research {product_name} now."}]
    searches_done = 0

    while True:
        response = provider.complete(
            system=system,
            messages=messages,
            tools=[WEB_SEARCH_TOOL],
            max_tokens=2048,
        )

        # Append assistant turn in normalized format
        messages.append({
            "role": "assistant",
            "content": response.text,
            "tool_calls": [{"id": tc.id, "name": tc.name, "input": tc.input}
                           for tc in response.tool_calls],
        })

        if response.stop_reason == "end_turn":
            if response.text:
                try:
                    data = json.loads(response.text.strip())
                    result = ResearchResult(
                        product_name=data.get("product_name", product_name),
                        specs=data.get("specs", {}),
                        pricing=data.get("pricing", ""),
                        reviews_summary=data.get("reviews_summary", ""),
                        key_findings=data.get("key_findings", []),
                        searches_performed=data.get("searches_performed", []),
                    )
                    print_agent_done(agent_label,
                                     f"{searches_done} searches, "
                                     f"{len(result.key_findings)} findings")
                    return result
                except json.JSONDecodeError:
                    print_agent_done(agent_label, "parse fallback")
                    return ResearchResult(
                        product_name=product_name,
                        reviews_summary=response.text[:400],
                    )
            return ResearchResult(product_name=product_name)

        if response.stop_reason != "tool_use":
            break

        # Execute tool calls and build normalized tool result messages
        for tc in response.tool_calls:
            query = tc.input.get("query", "")
            cached = memory_store.get_cached_search(query)
            if cached:
                result_text = cached
                print_search(f"{query}  [cached]")
            else:
                print_search(query)
                result_text = web_search(query)
                memory_store.cache_search(query, result_text)
                searches_done += 1

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.name,
                "content": result_text,
            })

    print_agent_done(agent_label, "incomplete")
    return ResearchResult(product_name=product_name)
