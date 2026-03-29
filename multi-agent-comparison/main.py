#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from coordinator import run_coordinator
from display import print_banner, print_separator


def main():
    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your key.")
        sys.exit(1)

    print_banner()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}\n")
    else:
        query = input("What would you like to compare? > ").strip()
        if not query:
            print("No input provided. Exiting.")
            sys.exit(0)
        print()

    print("Starting multi-agent pipeline...\n")

    report = run_coordinator(query)

    print_separator()
    print(report)
    print_separator()

    # Optional: save report to file
    if "--save" in sys.argv:
        idx = sys.argv.index("--save")
        if idx + 1 < len(sys.argv):
            path = sys.argv[idx + 1]
            with open(path, "w") as f:
                f.write(report)
            print(f"\nReport saved to {path}")


if __name__ == "__main__":
    main()
