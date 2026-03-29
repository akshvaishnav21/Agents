#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from agent import run_comparison_agent

BANNER = """
╔══════════════════════════════════════════════════════════╗
║             Product Comparison Agent                     ║
║         Powered by Claude + Web Search                   ║
╚══════════════════════════════════════════════════════════╝

Examples:
  • Compare iPhone 17 vs Galaxy S26 Ultra
  • MacBook Pro M4 vs Dell XPS 15
  • PlayStation 5 vs Xbox Series X
  • AirPods Pro 2 vs Sony WH-1000XM6
"""


def main():
    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your key, then re-run.")
        sys.exit(1)

    print(BANNER)

    # Accept query from CLI arg or interactive prompt
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Comparing: {query}\n")
    else:
        query = input("What would you like to compare? > ").strip()
        if not query:
            print("No input provided. Exiting.")
            sys.exit(0)

    print("\nResearching... (this may take 30–60 seconds)\n")

    report = run_comparison_agent(query)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
