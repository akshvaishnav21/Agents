#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from coordinator import run_coordinator
from display import print_banner, print_separator
from providers import get_provider, PROVIDERS, ENV_VARS


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-agent product comparison powered by your choice of LLM."
    )
    parser.add_argument(
        "query", nargs="*",
        help="Comparison query, e.g. 'Compare iPhone 17 vs Galaxy S26 Ultra'"
    )
    parser.add_argument(
        "--provider", "-p",
        choices=list(PROVIDERS),
        default="anthropic",
        help="LLM provider to use (default: anthropic)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Override the default model for the chosen provider",
    )
    parser.add_argument(
        "--save", "-s",
        metavar="FILE",
        help="Save the markdown report to a file",
    )
    return parser.parse_args()


def check_api_key(provider_name: str):
    env_var = ENV_VARS[provider_name]
    if not os.getenv(env_var):
        print(f"Error: {env_var} is not set.")
        print(f"Add it to your .env file: {env_var}=your_key_here")
        sys.exit(1)


def main():
    load_dotenv()
    args = parse_args()

    check_api_key(args.provider)
    provider = get_provider(args.provider, args.model)

    print_banner()
    print(f"Provider: {provider}\n")

    if args.query:
        query = " ".join(args.query)
        print(f"Query: {query}\n")
    else:
        query = input("What would you like to compare? > ").strip()
        if not query:
            print("No input provided. Exiting.")
            sys.exit(0)
        print()

    print("Starting multi-agent pipeline...\n")

    report = run_coordinator(query, provider)

    print_separator()
    print(report)
    print_separator()

    if args.save:
        with open(args.save, "w") as f:
            f.write(report)
        print(f"\nReport saved to {args.save}")


if __name__ == "__main__":
    main()
