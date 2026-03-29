# Product Comparison Agent

An AI agent that compares any two consumer products using real-time web search and Claude.

Type a query like **"Compare iPhone 17 vs Galaxy S26 Ultra"** and get a structured, opinionated comparison report in seconds.

## How It Works

1. You enter a comparison query in natural language
2. Claude autonomously decides what to search for (specs, prices, reviews)
3. The agent calls the web search tool multiple times to gather data
4. Claude synthesizes all results into a structured markdown report

```
User: "Compare MacBook Pro M4 vs Dell XPS 15"
         │
         ▼
  ┌─────────────────┐
  │  Claude decides │
  │  what to search │
  └────────┬────────┘
           │ tool_use
     ┌─────┴──────┐
     │ web_search │  ← DuckDuckGo (no API key needed)
     └─────┬──────┘
           │ results
     ┌─────┴──────────┐
     │ Claude writes  │
     │ the report     │
     └────────────────┘
         │
         ▼
  Structured Markdown
  comparison report
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Anthropic API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...

# 3. Run
python main.py

# Or pass query as argument
python main.py Compare iPhone 17 vs Galaxy S26 Ultra
```

## Output Format

The agent always produces:
- **Comparison table** — display, camera, battery, processor, storage, OS, price
- **Pros & Cons** for each product
- **Verdict** — practical recommendation by use case

See [`examples/output_iphone_vs_samsung.md`](examples/output_iphone_vs_samsung.md) for a sample output.

## Stack

| Component     | Tool                              |
|---------------|-----------------------------------|
| AI Model      | Claude Opus 4.6 (Anthropic)       |
| Web Search    | DuckDuckGo (no API key required)  |
| Agentic Loop  | Claude tool use (manual loop)     |
| Language      | Python 3.11+                      |

## Project Structure

```
product-comparison-agent/
├── main.py        # CLI entry point
├── agent.py       # Agentic loop logic
├── tools.py       # Web search tool definition
├── requirements.txt
├── .env.example
└── examples/
    └── output_iphone_vs_samsung.md
```
