"""
Writer Agent — formats the final markdown report.

Receives the structured AnalysisResult and returns a polished
markdown comparison report as a plain string.
"""
import json
from schemas import AnalysisResult
from display import print_agent_done
from providers import LLMProvider

SYSTEM_PROMPT = """\
You are a consumer tech writer. Format the provided analysis data into a
polished markdown report. Be opinionated and practical in the verdict.

Use this exact structure:

## [Product A] vs [Product B] — Full Comparison

| Feature       | [Product A]  | [Product B]  |
|---------------|--------------|--------------|
(one row per feature from the analysis)

### [Product A] — Pros & Cons
**Pros:**
- ...

**Cons:**
- ...

### [Product B] — Pros & Cons
**Pros:**
- ...

**Cons:**
- ...

### Verdict
[verdict sentence]

**Buy [Product A] if:** [buy_a_if text]

**Buy [Product B] if:** [buy_b_if text]
"""


def run_writer(analysis: AnalysisResult, provider: LLMProvider) -> str:
    user_content = (
        f"Format this analysis into the markdown report:\n\n"
        f"{json.dumps(analysis.to_dict(), indent=2)}"
    )

    response = provider.complete(
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        tools=[],
        max_tokens=4096,
    )

    if response.text:
        print_agent_done("Writer")
        return response.text

    print_agent_done("Writer", "empty response")
    return "Report generation failed."
