#!/usr/bin/env python3
"""evaluate.py — one-click full audit pipeline (standalone, no DM Pro).

Usage:
    python evaluate.py          # Run full audit on all agent outputs
    python evaluate.py --stats  # Run audit + statistical analysis
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from auditor import audit_file
from scorer import score_agent, generate_overall

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")
OUTPUT_DIR = PROJECT_ROOT / "output" / "agent_outputs"


def discover_files() -> list[tuple[str, Path]]:
    """Discover all agent output markdown files."""
    files = []
    if not OUTPUT_DIR.exists():
        print(f"ERROR: Output directory not found: {OUTPUT_DIR}")
        return files

    for agent_dir in sorted(OUTPUT_DIR.iterdir()):
        if agent_dir.is_dir():
            agent_name = agent_dir.name
            for md_file in sorted(agent_dir.glob("*.md")):
                files.append((agent_name, md_file))
    return files


def main():
    files = discover_files()
    if not files:
        print(f"ERROR: No agent output files found in {OUTPUT_DIR}")
        print("Generate agent outputs first, then re-run.")
        sys.exit(1)

    print(f"Found {len(files)} files from {len(set(a for a, _ in files))} agents.\n")

    # Stage 1: Audit each file
    audit_results = []
    for agent_name, file_path in files:
        rel = file_path.relative_to(PROJECT_ROOT)
        print(f"Auditing: {rel} ...")
        try:
            result = audit_file(file_path, agent_name)
            audit_results.append(result)
            h_score = result.get("hallucination", {}).get("hallucination_score", "?")
            c_score = result.get("claim_verification", {}).get("verification_score", "?")
            v_score = result.get("output_validation", {}).get("validation_score", "?")
            print(f"  Hallucination: {h_score} | Claims: {c_score} | Structure: {v_score}")
        except Exception as e:
            print(f"  ERROR: {e}")
            audit_results.append({
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "agent": agent_name,
                "error": str(e),
            })

    # Stage 2: Agent-level aggregation with bootstrap CIs
    agent_names = sorted(set(r.get("agent") for r in audit_results))
    agent_scores = []
    for an in agent_names:
        agent_scores.append(score_agent(an, audit_results))

    overall = generate_overall(agent_scores)

    # Stage 3: Build final output
    output = {
        "meta": {
            "project": "Agent Quality Audit — Standalone (No DM Pro dependency)",
            "brand": "TechGlow",
            "evaluation_date": "2026-05-15",
            "total_files": len(files),
            "total_agents": len(agent_names),
            "detectors": {
                "hallucination": "Multi-pattern + NER + hedging analysis (original)",
                "claim_verification": "Embedding similarity + evidence cross-reference (original)",
                "output_validation": "Semantic section classification (original)",
                "statistical_audit": "Bootstrap CI + Cohen's Kappa + threshold stability (original)",
            },
        },
        "overall": overall,
        "agents": {a["agent"]: a for a in agent_scores},
        "files": audit_results,
    }

    # Write results
    results_path = PROJECT_ROOT / "output" / "audit_results.json"
    results_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"Audit complete. Results: {results_path.relative_to(PROJECT_ROOT)}")
    print(f"Overall composite: {overall.get('avg_composite_score', 'N/A')}")

    # Print bootstrap CIs if available
    bootstrap_cis = overall.get("bootstrap_cis", {})
    if bootstrap_cis:
        print(f"\nBootstrap 95% Confidence Intervals:")
        for metric, ci in bootstrap_cis.items():
            print(f"  {metric}: {ci['point_estimate']:.1f} "
                  f"[{ci['ci_lower']:.1f}, {ci['ci_upper']:.1f}]")

    # Print best/worst
    best = overall.get("best_agent", {})
    worst = overall.get("worst_agent", {})
    print(f"\nBest: {best.get('name', '?')} ({best.get('score', '?')})")
    print(f"Worst: {worst.get('name', '?')} ({worst.get('score', '?')})")


if __name__ == "__main__":
    main()
