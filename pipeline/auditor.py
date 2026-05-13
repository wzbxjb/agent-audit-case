#!/usr/bin/env python3
"""auditor.py — 调用 DM Pro 检测脚本的适配层，返回标准化审计结果。"""

import json
import subprocess
import sys
from pathlib import Path

DM_PRO_SCRIPTS = Path("/Users/wangzhe/Desktop/digital-marketing-pro/scripts")
PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")


def run_hallucination_detect(text: str, brand_domain: str = "techglowlighting.com") -> dict:
    """Run DM Pro hallucination-detector on the given text."""
    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "hallucination-detector.py"),
            "--action", "detect",
            "--text", text,
            "--brand-domain", brand_domain,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"hallucination-detector failed: {result.stderr}"}
    return json.loads(result.stdout)


def run_claim_verification(text: str, evidence_path: str = None) -> dict:
    """Run DM Pro claim-verifier on the given text against evidence file."""
    if evidence_path is None:
        evidence_path = str(PROJECT_ROOT / "output" / "evidence.json")

    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "claim-verifier.py"),
            "--action", "verify",
            "--text", text,
            "--evidence", evidence_path,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"claim-verifier failed: {result.stderr}"}
    return json.loads(result.stdout)


def run_output_validation(text: str, schema: str) -> dict:
    """Run DM Pro output-validator on the given text against a content schema.

    Schema must be one of: blog_post, email, social_post, landing_page,
    press_release, content_brief, campaign_plan.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "output-validator.py"),
            "--action", "validate",
            "--text", text,
            "--schema", schema,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"output-validator failed: {result.stderr}"}
    return json.loads(result.stdout)


# Schema mapping: agent name -> content schema for output-validator
AGENT_SCHEMA_MAP = {
    "seo_specialist": "content_brief",
    "content_creator": "blog_post",
    "email_specialist": "email",
    "social_media_manager": "social_post",
}


def audit_file(file_path: Path, agent_name: str) -> dict:
    """Run full audit (3 checks) on a single agent output file."""
    text = file_path.read_text(encoding="utf-8")

    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "agent": agent_name,
        "word_count": len(text.split()),
    }

    # 1. Hallucination detection
    h_result = run_hallucination_detect(text)
    result["hallucination"] = h_result

    # 2. Claim verification
    c_result = run_claim_verification(text)
    result["claim_verification"] = c_result

    # 3. Output validation
    schema = AGENT_SCHEMA_MAP.get(agent_name, "blog_post")
    v_result = run_output_validation(text, schema)
    result["output_validation"] = v_result

    return result


if __name__ == "__main__":
    # Quick smoke test
    test_text = "TechGlow has 500,000 customers and was featured in Forbes."
    print("=== Hallucination Test ===")
    print(json.dumps(run_hallucination_detect(test_text), indent=2))
    print("\n=== Claim Verification Test ===")
    print(json.dumps(run_claim_verification(test_text), indent=2))
    print("\n=== Output Validation Test (blog) ===")
    print(json.dumps(run_output_validation(test_text, "blog_post"), indent=2))
