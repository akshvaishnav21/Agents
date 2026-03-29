from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return formatted results."""
    try:
        results = list(DDGS().text(query, max_results=max_results))
        if not results:
            return f"No results found for: {query}"

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', 'N/A')}")
            lines.append(f"    {r.get('href', '')}")
            lines.append(f"    {r.get('body', '')}")
            lines.append("")
        return "\n".join(lines)

    except Exception as e:
        return f"Search failed: {e}"


WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": (
        "Search the web for product specifications, pricing, reviews, and benchmarks. "
        "Call multiple times with focused queries to gather thorough data."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Specific search query, e.g. 'iPhone 17 full specs price 2025'",
            }
        },
        "required": ["query"],
    },
}
