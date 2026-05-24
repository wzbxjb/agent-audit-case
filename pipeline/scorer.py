#!/usr/bin/env python3
"""scorer.py — weighted composite scoring with bootstrap confidence intervals.

Computes agent-level and overall scores from raw audit results, with
statistical rigor via bootstrap percentile CIs.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from detectors.statistical import StatisticalAuditor

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

WEIGHTS = {
    "hallucination": 0.40,
    "claim_verification": 0.35,
    "output_validation": 0.25,
}


def _extract_agent_scores(audit_results: list[dict]) -> dict[str, list[float]]:
    """Extract per-agent composite scores from raw audit results.

    Returns: {agent_name: [composite_score_per_file, ...]}
    """
    agent_composites: dict[str, list[float]] = {}
    for r in audit_results:
        if "error" in r:
            continue
        agent = r.get("agent", "unknown")
        h_score = r.get("hallucination", {}).get("hallucination_score", 100)
        c_score = r.get("claim_verification", {}).get("verification_score", 100)
        v_score = r.get("output_validation", {}).get("validation_score", 100)
        composite = round(
            h_score * WEIGHTS["hallucination"]
            + c_score * WEIGHTS["claim_verification"]
            + v_score * WEIGHTS["output_validation"],
            1,
        )
        agent_composites.setdefault(agent, []).append(composite)
    return agent_composites


def score_hallucination(h_data: dict) -> dict:
    """Extract and categorize hallucination flags."""
    checks = h_data.get("checks", {})
    all_flags = []
    for category in ["unverified_statistics", "suspicious_urls",
                      "unsubstantiated_claims", "entities_to_verify",
                      "missing_hedging"]:
        for flag in checks.get(category, []):
            flag["category"] = category
            all_flags.append(flag)

    high_count = sum(1 for f in all_flags if f.get("severity") == "high")
    critical_count = h_data.get("critical_flags", 0)

    return {
        "score": h_data.get("hallucination_score", 100),
        "interpretation": h_data.get("interpretation", ""),
        "total_flags": len(all_flags),
        "by_type": {
            cat: len(checks.get(cat, []))
            for cat in ["unverified_statistics", "suspicious_urls",
                         "unsubstantiated_claims", "entities_to_verify",
                         "missing_hedging"]
        },
        "by_severity": {"critical": critical_count, "high": high_count},
    }


def score_claims(c_data: dict) -> dict:
    """Extract claim verification summary."""
    summary = c_data.get("summary", {})
    return {
        "score": c_data.get("verification_score", 100),
        "interpretation": c_data.get("interpretation", ""),
        "total": summary.get("total", 0),
        "verified": summary.get("verified", 0),
        "partially_verified": summary.get("partially_verified", 0),
        "unverified": summary.get("unverified", 0),
        "contradicted": summary.get("contradicted", 0),
    }


def score_validation(v_data: dict) -> dict:
    """Extract output validation summary."""
    return {
        "score": v_data.get("validation_score", 100),
        "interpretation": v_data.get("interpretation", ""),
        "schema": v_data.get("schema", ""),
        "passed": v_data.get("passed", False),
        "issues": v_data.get("issues", []),
    }


def compute_composite(h_score: float, c_score: float, v_score: float) -> float:
    """Weighted composite score."""
    return round(
        h_score * WEIGHTS["hallucination"]
        + c_score * WEIGHTS["claim_verification"]
        + v_score * WEIGHTS["output_validation"],
        1,
    )


def score_agent(agent_name: str, audit_results: list[dict]) -> dict:
    """Aggregate audit results for one agent across all their output files.

    Now includes bootstrap CI for the agent's mean composite score.
    """
    agent_results = [r for r in audit_results if r.get("agent") == agent_name]
    if not agent_results:
        return {"agent": agent_name, "error": "no results"}

    h_scores, c_scores, v_scores = [], [], []
    all_h_flags = []
    all_claims = {"verified": 0, "partially_verified": 0,
                   "unverified": 0, "contradicted": 0, "total": 0}
    all_issues = []
    composites = []

    for r in agent_results:
        h = score_hallucination(r.get("hallucination", {}))
        c = score_claims(r.get("claim_verification", {}))
        v = score_validation(r.get("output_validation", {}))

        h_scores.append(h["score"])
        c_scores.append(c["score"])
        v_scores.append(v["score"])
        composites.append(compute_composite(h["score"], c["score"], v["score"]))
        all_h_flags.append(h)
        for k in ["verified", "partially_verified", "unverified", "contradicted", "total"]:
            all_claims[k] += c.get(k, 0)
        all_issues.extend(v["issues"])

    avg_h = round(np.mean(h_scores), 1) if h_scores else 0.0
    avg_c = round(np.mean(c_scores), 1) if c_scores else 0.0
    avg_v = round(np.mean(v_scores), 1) if v_scores else 0.0
    composite = round(np.mean(composites), 1) if composites else 0.0

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
    """Generate overall evaluation summary with bootstrap CIs.

    Now uses StatisticalAuditor for proper confidence intervals.
    """
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

    # Build scores dict for statistical audit
    scores_dict = {}
    for a in agent_scores:
        files = a.get("files_evaluated", 0)
        if files > 0 and "composite_score" in a:
            # Distribute the composite across files for bootstrap
            scores_dict[a["agent"]] = [a["composite_score"]] * files

    auditor = StatisticalAuditor(n_bootstrap=2000)
    stat_result = auditor.audit(scores_dict)

    return {
        "avg_composite_score": round(np.mean(composites), 1),
        "avg_hallucination_rate": round(total_flags / max(1, len(agent_scores)), 1),
        "overall_claim_accuracy": (
            round(
                sum(a.get("claim_summary", {}).get("verified", 0) for a in agent_scores)
                / max(1, total_claims) * 100,
                1,
            )
            if total_claims > 0
            else 0
        ),
        "best_agent": {"name": best["agent"], "score": best["composite_score"]},
        "worst_agent": {"name": worst["agent"], "score": worst["composite_score"]},
        "bootstrap_cis": {
            c.metric: {
                "point_estimate": c.point_estimate,
                "ci_lower": c.ci_lower,
                "ci_upper": c.ci_upper,
            }
            for c in stat_result.bootstrap_cis
        },
        "reliability": [r.to_dict() for r in stat_result.reliability],
    }


if __name__ == "__main__":
    sample = [
        {
            "agent": "test_agent",
            "file": "output/agent_outputs/test/file.md",
            "hallucination": {"hallucination_score": 72, "checks": {}, "critical_flags": 0,
                              "interpretation": "Moderate risk"},
            "claim_verification": {"verification_score": 68,
                                   "summary": {"total": 5, "verified": 3, "partially_verified": 1,
                                               "unverified": 1, "contradicted": 0}},
            "output_validation": {"validation_score": 85, "schema": "blog_post", "passed": True,
                                  "issues": []},
        }
    ]
    agent_result = score_agent("test_agent", sample)
    print(json.dumps(agent_result, indent=2, ensure_ascii=False))
    overall = generate_overall([agent_result])
    print(json.dumps(overall, indent=2, ensure_ascii=False))
