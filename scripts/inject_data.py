#!/usr/bin/env python3
"""inject_data.py — 将 audit_results.json 注入到 dashboard/index.html 的 auditData 对象中。"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")


def main():
    results_path = PROJECT_ROOT / "output" / "audit_results.json"
    dashboard_path = PROJECT_ROOT / "dashboard" / "index.html"

    if not results_path.exists():
        print(f"ERROR: {results_path} not found. Run evaluate.py first.")
        sys.exit(1)

    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    # Build the agents dict (what the dashboard needs)
    dashboard_data = {
        "meta": data["meta"],
        "overall": data["overall"],
        "agents": data["agents"],
    }

    dashboard_html = dashboard_path.read_text(encoding="utf-8")

    # Replace the placeholder auditData object
    new_data_block = f"const auditData = {json.dumps(dashboard_data, indent=2, ensure_ascii=False)};"
    updated = re.sub(
        r"const auditData = \{[\s\S]*?\};",
        new_data_block,
        dashboard_html,
        count=1,
    )

    if updated == dashboard_html:
        print("WARNING: Could not find auditData block. Data may not have been injected.")
    else:
        dashboard_path.write_text(updated, encoding="utf-8")
        print(f"Injected audit data into {dashboard_path.relative_to(PROJECT_ROOT)}")
        print(f"Overall score: {data['overall']['avg_composite_score']}")
        print(f"Best agent: {data['overall']['best_agent']['name']}")
        print(f"Worst agent: {data['overall']['worst_agent']['name']}")


if __name__ == "__main__":
    main()
