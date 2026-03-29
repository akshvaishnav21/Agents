import os

# ANSI colours — disabled when NO_COLOR is set or output is not a tty
_USE_COLOR = os.getenv("NO_COLOR") is None and os.isatty(1)

CYAN   = "\033[96m" if _USE_COLOR else ""
YELLOW = "\033[93m" if _USE_COLOR else ""
GREEN  = "\033[92m" if _USE_COLOR else ""
BLUE   = "\033[94m" if _USE_COLOR else ""
RESET  = "\033[0m"  if _USE_COLOR else ""
DIM    = "\033[2m"  if _USE_COLOR else ""

AGENT_COLORS = {
    "Coordinator": CYAN,
    "Researcher A": YELLOW,
    "Researcher B": YELLOW,
    "Analyst": GREEN,
    "Writer": BLUE,
}

BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║       Multi-Agent Product Comparison                     ║
║   Coordinator · Researcher · Analyst · Writer            ║
╚══════════════════════════════════════════════════════════╝

Examples:
  • Compare iPhone 17 vs Galaxy S26 Ultra
  • MacBook Pro M4 vs Dell XPS 15
  • PlayStation 5 vs Xbox Series X
"""


def _agent(name: str) -> str:
    color = AGENT_COLORS.get(name, "")
    return f"{color}[{name}]{RESET}"


def print_banner():
    print(BANNER)


def print_transition(from_agent: str, to_agent: str, detail: str = ""):
    suffix = f"  {DIM}({detail}){RESET}" if detail else ""
    print(f"\n{_agent(from_agent)} → {_agent(to_agent)}{suffix}")


def print_search(query: str):
    print(f"  {DIM}Searching:{RESET} \"{query}\"")


def print_agent_done(agent: str, detail: str = ""):
    suffix = f" — {detail}" if detail else ""
    print(f"  {_agent(agent)} complete{suffix}")


def print_memory(msg: str):
    print(f"  {DIM}Memory:{RESET} {msg}")


def print_separator():
    print("\n" + "=" * 60)
