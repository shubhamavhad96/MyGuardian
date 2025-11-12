from dataclasses import dataclass
from typing import Literal, Tuple
import yaml
from pathlib import Path

Route = Literal["allow", "repair", "block"]
RetrieverMode = Literal["hybrid", "bm25", "tfidf"]


@dataclass
class Thresholds:
    faithfulness_min: float
    coverage_min: float
    toxicity_max: float


@dataclass
class RepairCfg:
    retriever_mode: RetrieverMode
    top_k: int
    max_sentences: int
    add_missing_parts: bool
    add_citations: bool


@dataclass
class Policy:
    thresholds: Thresholds
    on_toxicity: Route
    on_low_faithfulness: Route
    on_low_coverage: Route
    repair: RepairCfg


def load_policy(path: str | Path = None) -> Policy:
    if path is None:
        import os
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(backend_dir, "policy.yaml")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    thr = data["thresholds"]
    routes = data["routes"]
    r = data["repair"]
    return Policy(
        thresholds=Thresholds(
            faithfulness_min=float(thr["faithfulness_min"]),
            coverage_min=float(thr["coverage_min"]),
            toxicity_max=float(thr["toxicity_max"]),
        ),
        on_toxicity=routes.get("on_toxicity", "block"),
        on_low_faithfulness=routes.get("on_low_faithfulness", "repair"),
        on_low_coverage=routes.get("on_low_coverage", "repair"),
        repair=RepairCfg(
            retriever_mode=r.get("retriever_mode", "hybrid"),
            top_k=int(r.get("top_k", 3)),
            max_sentences=int(r.get("max_sentences", 4)),
            add_missing_parts=bool(r.get("add_missing_parts", True)),
            add_citations=bool(r.get("add_citations", True)),
        ),
    )


def route_decision(scores: dict, policy: Policy, missing_parts: list[str]) -> Tuple[str, list[str]]:
    reasons: list[str] = []
    thr = policy.thresholds

    if scores["toxicity"] >= thr.toxicity_max:
        if policy.on_toxicity == "block":
            return "block", ["Toxic/PII content detected"]
        reasons.append("Toxic/PII content detected")

    low_faith = scores["faithfulness"] < thr.faithfulness_min
    low_cov = scores["coverage"] < thr.coverage_min

    if low_faith and policy.on_low_faithfulness == "repair":
        reasons.append(
            f"Faithfulness {scores['faithfulness']} < {thr.faithfulness_min}")
    if low_cov and policy.on_low_coverage == "repair":
        msg = f"Coverage {scores['coverage']} < {thr.coverage_min}"
        if missing_parts:
            msg += f" (missing: {', '.join(missing_parts[:3])}{'…' if len(missing_parts) > 3 else ''})"
        reasons.append(msg)

    if not reasons:
        return "allow", []
    return "repair", reasons
