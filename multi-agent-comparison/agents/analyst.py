"""
Analyst Agent — pure reasoning, no tools.

Receives research from both Researcher agents and produces
a structured AnalysisResult as JSON.
"""
import json
import anthropic
from schemas import ResearchResult, AnalysisResult
from display import print_agent_done

SYSTEM_PROMPT = """\
You are a product analyst. You receive raw research data for two products
and produce a structured, objective comparison analysis.

Output ONLY a JSON object in this exact format (no markdown, no extra text):

{
  "product_a": "...",
  "product_b": "...",
  "feature_rows": [
    {"feature": "Display", "a_value": "...", "b_value": "..."},
    {"feature": "Camera", "a_value": "...", "b_value": "..."},
    {"feature": "Battery", "a_value": "...", "b_value": "..."},
    {"feature": "Processor", "a_value": "...", "b_value": "..."},
    {"feature": "RAM / Storage", "a_value": "...", "b_value": "..."},
    {"feature": "OS", "a_value": "...", "b_value": "..."},
    {"feature": "Price", "a_value": "...", "b_value": "..."}
  ],
  "product_a_pros": ["Pro 1", "Pro 2", "Pro 3"],
  "product_a_cons": ["Con 1", "Con 2"],
  "product_b_pros": ["Pro 1", "Pro 2", "Pro 3"],
  "product_b_cons": ["Con 1", "Con 2"],
  "verdict": "One sentence overall verdict",
  "buy_a_if": "Describe the ideal buyer for product A",
  "buy_b_if": "Describe the ideal buyer for product B"
}
"""


def run_analyst(
    research_a: ResearchResult,
    research_b: ResearchResult,
    memory_context: str = "",
) -> AnalysisResult:
    client = anthropic.Anthropic()

    user_content = f"{research_a.to_prompt_text()}\n\n{research_b.to_prompt_text()}"
    if memory_context:
        user_content += f"\n\n---\nRelevant past comparisons from memory:\n{memory_context}"

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    for block in response.content:
        if block.type == "text":
            try:
                data = json.loads(block.text.strip())
                result = AnalysisResult(
                    product_a=data.get("product_a", research_a.product_name),
                    product_b=data.get("product_b", research_b.product_name),
                    feature_rows=data.get("feature_rows", []),
                    product_a_pros=data.get("product_a_pros", []),
                    product_a_cons=data.get("product_a_cons", []),
                    product_b_pros=data.get("product_b_pros", []),
                    product_b_cons=data.get("product_b_cons", []),
                    verdict=data.get("verdict", ""),
                    buy_a_if=data.get("buy_a_if", ""),
                    buy_b_if=data.get("buy_b_if", ""),
                )
                print_agent_done("Analyst",
                                 f"{len(result.feature_rows)} features compared")
                return result
            except json.JSONDecodeError:
                pass

    print_agent_done("Analyst", "parse fallback")
    return AnalysisResult(
        product_a=research_a.product_name,
        product_b=research_b.product_name,
    )
