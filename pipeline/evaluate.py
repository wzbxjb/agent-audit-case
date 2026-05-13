#!/usr/bin/env python3
"""evaluate.py — 一键执行全流程审计。

读取 output/agent_outputs/ 中的所有 Agent 产出，
依次调用 hallucination-detector / claim-verifier / output-validator，
汇总评分，输出 output/audit_results.json。
"""

import json
import sys
from pathlib import Path

from auditor import audit_file
from scorer import score_agent, generate_overall

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")
OUTPUT_DIR = PROJECT_ROOT / "output" / "agent_outputs"


def discover_files() -> list[tuple[str, Path]]:
    """Discover all agent output files. Returns list of (agent_name, file_path)."""
    files = []
    for agent_dir in sorted(OUTPUT_DIR.iterdir()):
        if agent_dir.is_dir():
            agent_name = agent_dir.name
            for md_file in sorted(agent_dir.glob("*.md")):
                files.append((agent_name, md_file))
    return files


def main():
    files = discover_files()
    if not files:
        print("ERROR: No agent output files found in", str(OUTPUT_DIR))
        print("Run Stage 1 first: generate agent outputs and save them to output/agent_outputs/")
        sys.exit(1)

    print(f"Found {len(files)} files from {len(set(a for a, _ in files))} agents.\n")

    audit_results = []
    for agent_name, file_path in files:
        print(f"Auditing: {file_path.relative_to(PROJECT_ROOT)} ...")
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

    # Agent-level aggregation
    agent_names = sorted(set(r["agent"] for r in audit_results))
    agent_scores = []
    for an in agent_names:
        agent_scores.append(score_agent(an, audit_results))

    overall = generate_overall(agent_scores)

    # Build final output
    output = {
        "meta": {
            "project": "Agent Quality Audit — digital-marketing-pro Case Study",
            "brand": "TechGlow",
            "evaluation_date": "2026-05-15",
            "total_files": len(files),
            "total_agents": len(agent_names),
        },
        "overall": overall,
        "agents": {a["agent"]: a for a in agent_scores},
        "files": audit_results,
    }

    # Write results
    results_path = PROJECT_ROOT / "output" / "audit_results.json"
    results_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Audit complete. Results saved to {results_path.relative_to(PROJECT_ROOT)}")
    print(f"Overall composite score: {overall['avg_composite_score']}")
    print(f"Best agent: {overall['best_agent']['name']} ({overall['best_agent']['score']})")
    print(f"Worst agent: {overall['worst_agent']['name']} ({overall['worst_agent']['score']})")


if __name__ == "__main__":
    main()
