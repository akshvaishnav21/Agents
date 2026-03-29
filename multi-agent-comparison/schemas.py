from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ResearchResult:
    product_name: str
    specs: dict = field(default_factory=dict)       # feature → value
    pricing: str = ""
    reviews_summary: str = ""
    key_findings: list[str] = field(default_factory=list)
    searches_performed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_prompt_text(self) -> str:
        lines = [f"## Research: {self.product_name}"]
        if self.specs:
            lines.append("**Specs:**")
            for k, v in self.specs.items():
                lines.append(f"  - {k}: {v}")
        if self.pricing:
            lines.append(f"**Pricing:** {self.pricing}")
        if self.reviews_summary:
            lines.append(f"**Reviews:** {self.reviews_summary}")
        if self.key_findings:
            lines.append("**Key findings:**")
            for f_ in self.key_findings:
                lines.append(f"  - {f_}")
        return "\n".join(lines)


@dataclass
class AnalysisResult:
    product_a: str
    product_b: str
    feature_rows: list[dict] = field(default_factory=list)  # [{feature, a_value, b_value}]
    product_a_pros: list[str] = field(default_factory=list)
    product_a_cons: list[str] = field(default_factory=list)
    product_b_pros: list[str] = field(default_factory=list)
    product_b_cons: list[str] = field(default_factory=list)
    verdict: str = ""
    buy_a_if: str = ""
    buy_b_if: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
