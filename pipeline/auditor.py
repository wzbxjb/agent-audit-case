#!/usr/bin/env python3
"""auditor.py — runs 3 original detection engines on agent output files.

ALL detection is now done by our own detectors. NO subprocess calls to DM Pro.
"""

from __future__ import annotations

import json
from pathlib import Path

from detectors.hallucination import HallucinationDetector
from detectors.claim_checker import ClaimChecker
from detectors.structure import StructureValidator

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

# Schema mapping: agent name → content schema
AGENT_SCHEMA_MAP = {
    "seo_specialist": "content_brief",
    "content_creator": "blog_post",
    "email_specialist": "email",
    "social_media_manager": "social_post",
}


def audit_file(file_path: Path, agent_name: str) -> dict:
    """Run full audit (3 checks) on a single agent output file.

    Uses our own detection engines — no subprocess, no DM Pro dependency.
    """
    text = file_path.read_text(encoding="utf-8")

    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "agent": agent_name,
        "word_count": len(text.split()),
    }

    # 1. Hallucination detection — our own multi-pattern engine
    h_detector = HallucinationDetector()
    h_result = h_detector.detect(text)
    result["hallucination"] = h_result.to_dict()

    # 2. Claim verification — our own semantic embedding checker
    c_checker = ClaimChecker()
    c_result = c_checker.verify(text)
    result["claim_verification"] = c_result.to_dict()

    # 3. Output validation — our own semantic section classifier
    schema = AGENT_SCHEMA_MAP.get(agent_name, "blog_post")
    v_validator = StructureValidator()
    v_result = v_validator.validate(text, schema)
    result["output_validation"] = v_result.to_dict()

    return result


if __name__ == "__main__":
    test_text = "TechGlow has 500,000 customers worldwide and was featured in Forbes magazine."
    print("=== Hallucination Test ===")
    h = HallucinationDetector()
    print(json.dumps(h.detect(test_text).to_dict(), indent=2, ensure_ascii=False))

    print("\n=== Claim Verification Test ===")
    c = ClaimChecker()
    print(json.dumps(c.verify(test_text).to_dict(), indent=2, ensure_ascii=False))

    print("\n=== Structure Validation Test ===")
    v = StructureValidator()
    print(json.dumps(v.validate(test_text, "blog_post").to_dict(), indent=2, ensure_ascii=False))
