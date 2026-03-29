"""
Coordinator — the orchestration spine.

Parses the user query, loads memory, dispatches to sub-agents in sequence,
saves the result to memory, and returns the final report.
"""
import json
import anthropic
from memory import MemoryStore
from agents import run_researcher, run_analyst, run_writer
from display import print_transition, print_memory

_PARSE_SYSTEM = """\
Extract the two products being compared from the user's query.
Output ONLY a JSON object — no markdown, no extra text:

{
  "product_a": "Exact product name",
  "product_b": "Exact product name",
  "category": "smartphones|laptops|tablets|gaming|audio|other",
  "focus_areas": ["specs", "camera", "battery", "price", "performance"]
}
"""

_DEFAULT_FOCUS = ["specs", "pricing", "camera", "battery", "performance", "reviews"]


def run_coordinator(user_query: str) -> str:
    memory = MemoryStore()

    # ── Step 1: Parse query ──────────────────────────────────────
    client = anthropic.Anthropic()
    parse_response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        system=_PARSE_SYSTEM,
        messages=[{"role": "user", "content": user_query}],
    )

    product_a, product_b, category, focus_areas = _parse_query(
        parse_response, user_query
    )

    # ── Step 2: Load memory ──────────────────────────────────────
    memory_context = memory.search(f"{product_a} {product_b}")
    count = memory.count()
    if count > 0:
        print_memory(f"loaded {count} past comparison(s)")
        if memory_context:
            print_memory("found relevant past data")

    # ── Step 3: Researcher A ─────────────────────────────────────
    print_transition("Coordinator", "Researcher A", product_a)
    research_a = run_researcher(
        product_name=product_a,
        focus_areas=focus_areas,
        memory_store=memory,
        agent_label="Researcher A",
    )

    # ── Step 4: Researcher B ─────────────────────────────────────
    print_transition("Coordinator", "Researcher B", product_b)
    research_b = run_researcher(
        product_name=product_b,
        focus_areas=focus_areas,
        memory_store=memory,
        agent_label="Researcher B",
    )

    # ── Step 5: Analyst ──────────────────────────────────────────
    print_transition("Coordinator", "Analyst")
    analysis = run_analyst(research_a, research_b, memory_context)

    # ── Step 6: Writer ───────────────────────────────────────────
    print_transition("Coordinator", "Writer")
    report = run_writer(analysis)

    # ── Step 7: Save to memory ───────────────────────────────────
    entry_id = memory.save_comparison(
        product_a=product_a,
        product_b=product_b,
        category=category,
        verdict=analysis.verdict,
        key_findings=research_a.key_findings + research_b.key_findings,
        report=report,
    )
    print_memory(f"saved comparison (id: {entry_id})")

    return report


def _parse_query(response, fallback_query: str):
    """Extract structured fields from the parse response."""
    for block in response.content:
        if block.type == "text":
            try:
                data = json.loads(block.text.strip())
                return (
                    data.get("product_a", "Product A"),
                    data.get("product_b", "Product B"),
                    data.get("category", "other"),
                    data.get("focus_areas", _DEFAULT_FOCUS),
                )
            except json.JSONDecodeError:
                pass

    # Fallback: use the raw query split on "vs"
    parts = fallback_query.lower().replace("compare", "").split(" vs ")
    if len(parts) == 2:
        return parts[0].strip().title(), parts[1].strip().title(), "other", _DEFAULT_FOCUS
    return "Product A", "Product B", "other", _DEFAULT_FOCUS
