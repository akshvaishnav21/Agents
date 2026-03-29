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


# Tool schema for Claude API
WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": (
        "Search the web for up-to-date product information: specs, prices, "
        "reviews, and benchmarks. Call this multiple times with specific queries "
        "to gather comprehensive data before writing your comparison."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Specific search query. Examples: "
                    "'iPhone 17 full specs price 2025', "
                    "'Galaxy S26 Ultra camera review benchmark'"
                ),
            }
        },
        "required": ["query"],
    },
}
