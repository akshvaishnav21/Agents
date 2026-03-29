# AI Agents Portfolio

A collection of AI agent projects built with the Claude API (Anthropic).

## Projects

### [Product Comparison Agent](./product-comparison-agent/)

Compare any two consumer products using real-time web search and Claude.

```
> Compare iPhone 17 vs Galaxy S26 Ultra
```

The agent autonomously searches the web, gathers specs and reviews, and outputs a structured markdown comparison with a clear verdict.

**Stack:** Python · Claude Opus 4.6 · DuckDuckGo Search · Tool Use (Agentic Loop)

---

## Getting Started

Each project has its own `README.md` and `requirements.txt`. You'll need an [Anthropic API key](https://console.anthropic.com/).

---

### [Multi-Agent Comparison](./multi-agent-comparison/)

An advanced version with **agent-to-agent communication** and **persistent memory**.

```
[Coordinator] → [Researcher A] → [Researcher B] → [Analyst] → [Writer]
```

Four specialized Claude agents collaborate. Memory persists past comparisons and caches web searches across sessions.

**Stack:** Python · Claude Opus 4.6 · Multi-Agent Pipeline · DuckDuckGo · JSON Memory Store

---

## Patterns Demonstrated

| Pattern | Project |
|---|---|
| Tool Use + Agentic Loop | product-comparison-agent |
| Agent-to-Agent Communication | multi-agent-comparison |
| Persistent Memory | multi-agent-comparison |
| Search Caching | multi-agent-comparison |

## About

These projects demonstrate practical AI agent patterns using Claude's tool use capabilities — from a single agentic loop to a full multi-agent pipeline with memory.
