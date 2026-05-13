#!/usr/bin/env python3
"""scorer.py — 加权综合评分逻辑。从审计原始结果计算 agent 级别的综合分数。"""

import json
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

# Weights for composite scoring (sum = 1.0)
WEIGHTS = {
    "hallucination": 0.40,
    "claim_verification": 0.35,
    "output_validation": 0.25,
}


def score_hallucination(h_data: dict) -> dict:
    """Extract hallucination score and flag breakdown."""
    score = h_data.get("hallucination_score", 100)

    checks = h_data.get("checks", {})
    stat_count = len(checks.get("unverified_statistics", []))
    url_count = len(checks.get("suspicious_urls", []))
    claim_count = len(checks.get("unsubstantiated_claims", []))
    entity_count = len(checks.get("entities_to_verify", []))
    hedging_count = len(checks.get("missing_hedging", []))

    all_flags = (
        checks.get("unverified_statistics", [])
        + checks.get("suspicious_urls", [])
        + checks.get("unsubstantiated_claims", [])
        + checks.get("entities_to_verify", [])
        + checks.get("missing_hedging", [])
    )
    high_count = sum(1 for f in all_flags if f.get("severity") == "high")
    critical_count = h_data.get("critical_flags", 0)

    return {
        "score": score,
        "interpretation": h_data.get("interpretation", ""),
        "total_flags": len(all_flags),
        "by_type": {
            "unverified_statistics": stat_count,
            "suspicious_urls": url_count,
            "unsubstantiated_claims": claim_count,
            "entities_to_verify": entity_count,
            "missing_hedging": hedging_count,
        },
        "by_severity": {
            "critical": critical_count,
            "high": high_count,
        },
    }


def score_claims(c_data: dict) -> dict:
    """Extract claim verification score and summary."""
    score = c_data.get("verification_score", 100)
    summary = c_data.get("summary", {})

    return {
        "score": score,
        "interpretation": c_data.get("interpretation", ""),
        "total": summary.get("total", 0),
        "verified": summary.get("verified", 0),
        "partially_verified": summary.get("partially_verified", 0),
        "unverified": summary.get("unverified", 0),
        "contradicted": summary.get("contradicted", 0),
    }


def score_validation(v_data: dict) -> dict:
    """Extract output validation score and issues."""
    return {
        "score": v_data.get("validation_score", 100),
        "interpretation": v_data.get("interpretation", ""),
        "schema": v_data.get("schema", ""),
        "passed": v_data.get("passed", False),
        "issues": v_data.get("issues", []),
    }


def compute_composite(h_score: float, c_score: float, v_score: float) -> float:
    """Compute weighted composite score."""
    return round(
        h_score * WEIGHTS["hallucination"]
        + c_score * WEIGHTS["claim_verification"]
        + v_score * WEIGHTS["output_validation"],
        1,
    )


def score_agent(agent_name: str, audit_results: list[dict]) -> dict:
    """Aggregate audit results for one agent across all their output files."""
    agent_results = [r for r in audit_results if r.get("agent") == agent_name]

    if not agent_results:
        return {"agent": agent_name, "error": "no results found"}

    h_scores, c_scores, v_scores = [], [], []
    all_h_flags = []
    all_claims = {"verified": 0, "partially_verified": 0, "unverified": 0, "contradicted": 0, "total": 0}
    all_issues = []

    for r in agent_results:
        h = score_hallucination(r.get("hallucination", {}))
        c = score_claims(r.get("claim_verification", {}))
        v = score_validation(r.get("output_validation", {}))

        h_scores.append(h["score"])
        c_scores.append(c["score"])
        v_scores.append(v["score"])
        all_h_flags.append(h)
        for k in ["verified", "partially_verified", "unverified", "contradicted", "total"]:
            all_claims[k] += c[k]
        all_issues.extend(v["issues"])

    avg_h = round(sum(h_scores) / len(h_scores), 1)
    avg_c = round(sum(c_scores) / len(c_scores), 1)
    avg_v = round(sum(v_scores) / len(v_scores), 1)
    composite = compute_composite(avg_h, avg_c, avg_v)

    return {
        "agent": agent_name,
        "files_evaluated": len(agent_results),
        "composite_score": composite,
        "scores": {
            "hallucination": avg_h,
            "claim_verification": avg_c,
            "output_validation": avg_v,
        },
        "hallucination_flags": all_h_flags,
        "claim_summary": all_claims,
        "all_issues": all_issues,
    }


def generate_overall(agent_scores: list[dict]) -> dict:
    """Generate overall evaluation summary across all agents."""
    composites = [a["composite_score"] for a in agent_scores if "composite_score" in a]

    if not composites:
        return {"error": "no valid scores"}

    best = max(agent_scores, key=lambda a: a.get("composite_score", 0))
    worst = min(agent_scores, key=lambda a: a.get("composite_score", 0))

    total_flags = sum(
        sum(h.get("total_flags", 0) for h in a.get("hallucination_flags", []))
        for a in agent_scores
    )
    total_claims = sum(
        a.get("claim_summary", {}).get("total", 0) for a in agent_scores
    )

    return {
        "avg_composite_score": round(sum(composites) / len(composites), 1),
        "avg_hallucination_rate": round(
            total_flags / max(1, len(agent_scores)), 1
        ),
        "overall_claim_accuracy": round(
            sum(a.get("claim_summary", {}).get("verified", 0) for a in agent_scores)
            / max(1, total_claims)
            * 100,
            1,
        ) if total_claims > 0 else 0,
        "best_agent": {"name": best["agent"], "score": best["composite_score"]},
        "worst_agent": {"name": worst["agent"], "score": worst["composite_score"]},
    }


if __name__ == "__main__":
    # Smoke test with sample data
    sample = [
        {
            "agent": "test_agent",
            "file": "output/agent_outputs/test/file.md",
            "hallucination": {"hallucination_score": 72, "checks": {}, "critical_flags": 0, "interpretation": "Moderate risk"},
            "claim_verification": {"verification_score": 68, "summary": {"total": 5, "verified": 3, "partially_verified": 1, "unverified": 1, "contradicted": 0}},
            "output_validation": {"validation_score": 85, "schema": "blog_post", "passed": True, "issues": []},
        }
    ]
    agent_result = score_agent("test_agent", sample)
    print(json.dumps(agent_result, indent=2))
    overall = generate_overall([agent_result])
    print(json.dumps(overall, indent=2))
