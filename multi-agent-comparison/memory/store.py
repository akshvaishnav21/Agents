import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

MAX_COMPARISONS = 20
CACHE_TTL_HOURS = 24
_STORE_PATH = os.path.join(os.path.dirname(__file__), "memory.json")

_EMPTY = {
    "comparisons": [],
    "preferences": {},
    "search_cache": {},
}


class MemoryStore:
    def __init__(self, path: str = _STORE_PATH):
        self._path = path
        self._tmp = path + ".tmp"
        self._data = self._load()

    # ── public API ────────────────────────────────────────────────

    def save_comparison(self, product_a: str, product_b: str, category: str,
                        verdict: str, key_findings: list[str], report: str):
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": _now(),
            "product_a": product_a,
            "product_b": product_b,
            "category": category,
            "verdict": verdict,
            "key_findings": key_findings[:6],
            "report_snippet": report[:500],
        }
        self._data["comparisons"].insert(0, entry)
        self._data["comparisons"] = self._data["comparisons"][:MAX_COMPARISONS]
        self._data["preferences"]["last_category"] = category
        self._write()
        return entry["id"]

    def search(self, query: str, limit: int = 3) -> str:
        """Return formatted string of past comparisons relevant to query."""
        q = query.lower()
        matches = []
        for c in self._data["comparisons"]:
            text = f"{c['product_a']} {c['product_b']} {' '.join(c['key_findings'])}".lower()
            if any(word in text for word in q.split() if len(word) > 2):
                matches.append(c)
            if len(matches) >= limit:
                break

        if not matches:
            return ""

        lines = ["Past comparisons found in memory:"]
        for m in matches:
            lines.append(f"  • {m['product_a']} vs {m['product_b']} ({m['timestamp'][:10]})")
            lines.append(f"    Verdict: {m['verdict']}")
            for f in m["key_findings"][:3]:
                lines.append(f"    - {f}")
        return "\n".join(lines)

    def get_cached_search(self, query: str) -> Optional[str]:
        cache = self._data["search_cache"]
        if query in cache:
            entry = cache[query]
            age = datetime.now(timezone.utc) - datetime.fromisoformat(entry["timestamp"])
            if age < timedelta(hours=CACHE_TTL_HOURS):
                return entry["result"]
            del cache[query]
            self._write()
        return None

    def cache_search(self, query: str, result: str):
        self._data["search_cache"][query] = {
            "result": result,
            "timestamp": _now(),
        }
        self._write()

    def count(self) -> int:
        return len(self._data["comparisons"])

    # ── internal ──────────────────────────────────────────────────

    def _load(self) -> dict:
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {k: v.copy() if isinstance(v, dict) else list(v)
                for k, v in _EMPTY.items()}

    def _write(self):
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._tmp, "w") as f:
            json.dump(self._data, f, indent=2)
        os.replace(self._tmp, self._path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
