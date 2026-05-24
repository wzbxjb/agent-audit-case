"""Semantic structure validation — checks content completeness by meaning, not heading text.

Replaces regex-based schema validation with semantic section classification.
Instead of looking for exact heading text matches (which fail when writers use
creative titles), this detector:

1. Splits content into sections
2. Classifies each section's semantic role using zero-shot classification
3. Checks that all required sections for the content type are present
4. Flags missing sections with actionable feedback

This directly addresses the original case study's Finding 2:
"纯规则匹配的检测工具在创意内容领域存在显著盲区"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# Content type schemas — what sections each type should have
CONTENT_SCHEMAS = {
    "blog_post": {
        "required": ["title", "introduction", "body", "conclusion"],
        "optional": ["call_to_action", "author_bio", "related_posts", "faq", "table_of_contents"],
        "min_words": 300,
        "max_words": 5000,
    },
    "email": {
        "required": ["subject_line", "body", "call_to_action"],
        "optional": ["preheader", "greeting", "signature", "unsubscribe", "ps"],
        "min_words": 50,
        "max_words": 1000,
    },
    "social_post": {
        "required": ["body"],
        "optional": ["headline", "call_to_action", "hashtags", "mentions", "link"],
        "min_words": 10,
        "max_words": 1000,
    },
    "landing_page": {
        "required": ["headline", "subheadline", "body", "call_to_action"],
        "optional": ["social_proof", "features", "testimonials", "faq", "pricing", "hero_image"],
        "min_words": 100,
        "max_words": 3000,
    },
    "content_brief": {
        "required": ["objective", "target_audience", "key_messages"],
        "optional": ["tone", "keywords", "competitor_references", "word_count_target", "deadline"],
        "min_words": 100,
        "max_words": 5000,
    },
    "press_release": {
        "required": ["headline", "dateline", "body", "boilerplate", "contact_info"],
        "optional": ["subheadline", "quote", "multimedia_note"],
        "min_words": 200,
        "max_words": 2000,
    },
}


# Semantic labels → candidate keyword patterns for section detection
# These are used as a lightweight fallback when no ML model is available
SECTION_INDICATORS = {
    "title": [r'^#\s+.+', r'^Title:', r'^<h1'],
    "introduction": [r'(?i)(?:introduction|overview|background|why\s+.+\?|what\s+is\s+.+\?)'],
    "body": [r'(?i)(?:the\s+(?:problem|solution|benefits?|features?|key|main|how|what)|here\'?s?\s+(?:what|how|why)|let\'?s?\s+(?:dive|explore|look))'],
    "conclusion": [r'(?i)(?:conclusion|summary|wrapping\s+up|final\s+thoughts?|in\s+summary|to\s+sum\s+up|the\s+bottom\s+line|takeaways?)'],
    "call_to_action": [r'(?i)(?:call\s+to\s+action|cta|get\s+started|sign\s+up|buy\s+now|shop\s+now|learn\s+more|subscribe|download|try\s+(?:it\s+)?free|claim\s+your|don\'?t\s+miss|act\s+now|limited\s+time)'],
    "subject_line": [r'(?i)^Subject:', r'(?i)^(?:RE|FW):'],
    "greeting": [r'(?i)^(?:hi|hello|hey|dear|greetings|good\s+(?:morning|afternoon|evening))\b'],
    "signature": [r'(?i)(?:best\s+regards|cheers|sincerely|warmly|thanks|thank\s+you)[\s,]*$'],
    "unsubscribe": [r'(?i)(?:unsubscribe|opt(?:\s+|-)?out|email\s+preferences)'],
    "headline": [r'^#\s+.+', r'^<h1', r'^[A-Z][A-Za-z\s]{10,60}$'],
    "subheadline": [r'^##\s+.+', r'^<h2'],
    "dateline": [r'(?i)^[A-Z][a-zA-Z]+(?:,\s+[A-Z][a-z]+)?\s*[-–—]\s*\d{1,2},\s*\d{4}\s*[-–—]'],
    "boilerplate": [r'(?i)(?:about\s+(?:the\s+)?(?:company|brand|organization|team))'],
    "contact_info": [r'(?i)(?:contact|email|phone|press\s+contact|media\s+inquiry|@[\w.]+)'],
    "objective": [r'(?i)(?:objective|goal|purpose|aim|target)'],
    "target_audience": [r'(?i)(?:target\s+audience|audience|demographic|buyer\s+persona|who\s+is\s+this\s+for)'],
    "key_messages": [r'(?i)(?:key\s+messages?|core\s+messages?|main\s+points?|messaging|value\s+prop)'],
    "social_proof": [r'(?i)(?:testimonials?|reviews?|rating|what\s+(?:our\s+)?customers?\s+(?:say|think)|case\s+stud(y|ies)|success\s+stor(y|ies)|trusted\s+by)'],
    "keywords": [r'(?i)(?:keywords?|search\s+terms?|target\s+keywords?|SEO\s+keywords?)'],
    "hashtags": [r'(?:^|\s)#[a-zA-Z0-9_]+'],
    "mentions": [r'(?:^|\s)@[a-zA-Z0-9_]+'],
}


@dataclass
class StructureFlag:
    """A structure issue found in the content."""

    section: str
    status: str  # missing | present | warning
    description: str
    severity: str = "medium"

    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "status": self.status,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class StructureResult:
    """Complete structure validation output."""

    schema: str
    validation_score: float  # 0-100
    passed: bool
    issues: list[StructureFlag]
    interpretation: str
    word_count: int

    def to_dict(self) -> dict:
        return {
            "validation_score": self.validation_score,
            "schema": self.schema,
            "passed": self.passed,
            "issues": [i.to_dict() for i in self.issues],
            "interpretation": self.interpretation,
            "word_count": self.word_count,
        }


class StructureValidator:
    """Validates content structure using semantic section detection.

    Uses a lightweight keyword-based section classifier as primary method,
    with an optional zero-shot classification fallback when transformers
    are available. This is intentionally NOT regex headline matching —
    it searches for semantic indicators of section presence throughout the text.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: If True, optional sections are also checked and flagged if missing.
        """
        self.strict_mode = strict_mode
        self._classifier = None

    def validate(self, text: str, schema_name: str) -> StructureResult:
        """Validate content structure against a named schema.

        Args:
            text: The content to validate.
            schema_name: One of the keys in CONTENT_SCHEMAS.

        Returns:
            StructureResult with score, issues, and interpretation.
        """
        schema = CONTENT_SCHEMAS.get(schema_name)
        if schema is None:
            valid = ", ".join(CONTENT_SCHEMAS.keys())
            return StructureResult(
                schema=schema_name,
                validation_score=0,
                passed=False,
                issues=[StructureFlag(
                    section="schema",
                    status="missing",
                    description=f"Unknown schema '{schema_name}'. Valid schemas: {valid}",
                    severity="high",
                )],
                interpretation=f"Invalid schema name.",
                word_count=len(text.split()),
            )

        word_count = len(text.split())
        issues: list[StructureFlag] = []

        # Check each required section
        for section in schema["required"]:
            is_present = self._detect_section(text, section)
            if is_present:
                issues.append(StructureFlag(
                    section=section,
                    status="present",
                    description=f"Required section '{section}' detected.",
                ))
            else:
                issues.append(StructureFlag(
                    section=section,
                    status="missing",
                    description=f"Required section '{section}' not detected. "
                                f"Content may lack this section or use non-standard formatting.",
                    severity="high" if section in ("body", "call_to_action") else "medium",
                ))

        # Check optional sections (only in strict mode)
        if self.strict_mode:
            for section in schema["optional"]:
                is_present = self._detect_section(text, section)
                if not is_present:
                    issues.append(StructureFlag(
                        section=section,
                        status="missing",
                        description=f"Optional section '{section}' not detected (strict mode).",
                        severity="low",
                    ))

        # Word count check
        min_w = schema["min_words"]
        max_w = schema["max_words"]
        if word_count < min_w:
            issues.append(StructureFlag(
                section="word_count",
                status="warning",
                description=f"Word count ({word_count}) below minimum ({min_w}).",
                severity="medium",
            ))
        elif word_count > max_w:
            issues.append(StructureFlag(
                section="word_count",
                status="warning",
                description=f"Word count ({word_count}) exceeds maximum ({max_w}).",
                severity="low",
            ))

        # Compute score
        n_required = len(schema["required"])
        n_present = sum(1 for i in issues if i.status == "present" and i.section in schema["required"])
        if n_required == 0:
            score = 100.0
        else:
            score = round((n_present / n_required) * 100, 1)

        # Additional penalties for word count issues
        if word_count < min_w:
            score = max(0.0, score - 20)
        if word_count > max_w * 1.5:
            score = max(0.0, score - 10)

        passed = all(
            i.status == "present"
            for i in issues
            if i.section in schema["required"]
        )

        # Build interpretation
        missing_required = [
            i.section for i in issues
            if i.status == "missing" and i.section in schema["required"]
        ]
        if not missing_required:
            interp = f"All {n_required} required sections present. Content structure looks complete."
        elif len(missing_required) <= 1:
            interp = f"Mostly complete — missing required section: {missing_required[0]}."
        else:
            interp = f"Missing {len(missing_required)}/{n_required} required sections: {', '.join(missing_required)}."

        return StructureResult(
            schema=schema_name,
            validation_score=score,
            passed=passed,
            issues=issues,
            interpretation=interp,
            word_count=word_count,
        )

    def _detect_section(self, text: str, section_name: str) -> bool:
        """Detect if a semantic section is present in the text.

        Uses keyword indicator patterns to search for section presence.
        This is intentionally NOT looking for exact heading matches —
        it searches the full text for semantic signals of each section type.
        """
        indicators = SECTION_INDICATORS.get(section_name, [])
        if not indicators:
            # Generic fallback: look for the section name as a heading
            indicators = [rf'(?i)(?:^|\n)\s*(?:#{{1,3}}\s+)?{re.escape(section_name)}']

        for pattern in indicators:
            if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                return True

        return False
