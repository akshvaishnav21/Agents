# Multi-Agent Product Comparison

An advanced product comparison system using **four specialized AI agents** and **persistent memory**.

Demonstrates two key agent engineering patterns:
1. **Agent-to-Agent Communication** — a Coordinator delegates tasks to specialized sub-agents
2. **Memory** — past comparisons and search results persist across sessions

## Architecture

```
User Input
    │
    ▼
[Coordinator]          orchestrates the pipeline + manages memory
    │
    ├──→ [Researcher A]    searches the web for Product A specs/reviews
    ├──→ [Researcher B]    searches the web for Product B specs/reviews
    ├──→ [Analyst]         compares the two research outputs (no tools)
    └──→ [Writer]          formats the final markdown report (no tools)
         │
         ▼
  memory.json            persists comparisons + search cache
```

Each agent is a **separate Claude API call** with its own system prompt and tool set.
Coordination is explicit Python — no guessing, no non-determinism in the pipeline.

## What Memory Does

- **Saves** every comparison with verdict and key findings
- **Loads** relevant past comparisons at the start of each run (injected into the Analyst's context)
- **Caches** web searches for 24 hours — run the same query twice and the second is instant
- Stored in `memory/memory.json` (auto-created, gitignored)

## Console Output

```
[Coordinator] → [Researcher A]  (iPhone 17)
  Searching: "iPhone 17 full specs 2025"
  Searching: "iPhone 17 battery camera review"
  [Researcher A] complete — 2 searches, 4 findings

[Coordinator] → [Researcher B]  (Galaxy S26 Ultra)
  Searching: "Samsung Galaxy S26 Ultra specs price"  [cached]
  Searching: "Galaxy S26 Ultra vs competition 2026"
  [Researcher B] complete — 1 search, 5 findings

[Coordinator] → [Analyst]
  [Analyst] complete — 7 features compared

[Coordinator] → [Writer]
  [Writer] complete
  Memory: saved comparison (id: a3f2...)
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env    # add keys for whichever provider(s) you want to use

# Default: Claude (Anthropic)
python main.py "Compare iPhone 17 vs Galaxy S26 Ultra"

# Use OpenAI
python main.py "Compare MacBook Pro vs Dell XPS 15" --provider openai

# Use Gemini
python main.py "Compare PS5 vs Xbox Series X" --provider gemini

# Override the model
python main.py "Compare AirPods Pro vs Sony WH-1000XM6" --provider openai --model gpt-4o-mini

# Save report to file
python main.py "Compare iPhone 17 vs Galaxy S26 Ultra" --save report.md
```

## Provider & Model Options

| Flag | Options | Default model |
|---|---|---|
| `--provider anthropic` | Claude | `claude-opus-4-6` |
| `--provider openai` | GPT | `gpt-4o` |
| `--provider gemini` | Gemini | `gemini-1.5-pro` |

Set the matching API key in `.env`:
- `ANTHROPIC_API_KEY` for Anthropic
- `OPENAI_API_KEY` for OpenAI
- `GOOGLE_API_KEY` for Gemini

## How It Differs From `product-comparison-agent`

| Feature | product-comparison-agent | multi-agent-comparison |
|---|---|---|
| Agents | 1 (monolithic) | 4 (specialized) |
| Memory | None | Persistent JSON |
| Search cache | None | 24h TTL cache |
| Agent communication | N/A | Coordinator pattern |
| Intermediate data | Hidden | Typed schemas |

## Stack

| Component | Tool |
|---|---|
| AI Model | Claude Opus 4.6 (Anthropic) |
| Web Search | DuckDuckGo (`ddgs`) |
| Memory | JSON file (no external DB) |
| Language | Python 3.11+ |

## Project Structure

```
multi-agent-comparison/
├── main.py           # CLI entry point
├── coordinator.py    # Orchestration spine
├── schemas.py        # ResearchResult, AnalysisResult dataclasses
├── display.py        # Colored console output
├── agents/
│   ├── researcher.py # Agentic loop + web search (per product)
│   ├── analyst.py    # Single Claude call, structured analysis
│   └── writer.py     # Single Claude call, markdown formatting
├── memory/
│   └── store.py      # MemoryStore: CRUD, search, cache, atomic writes
└── tools/
    └── web_search.py # DuckDuckGo wrapper + tool schema
```
