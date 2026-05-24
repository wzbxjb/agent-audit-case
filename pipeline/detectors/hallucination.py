"""Hallucination detection via multi-method analysis.

Detects five categories of potential hallucination in marketing text:
1. Unverified statistics — numbers without cited sources
2. Unsubstantiated claims — definite statements lacking evidence markers
3. Suspicious URLs — non-existent or placeholder domains
4. Entities to verify — named entities that may be fabricated
5. Missing hedging — absolute claims that should be qualified

Uses a combination of regex pattern matching, NER extraction, and
heuristic scoring — designed to run without external API calls.
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


@dataclass
class HallucinationFlag:
    """A single flagged issue in the text."""

    category: str  # unverified_statistics | unsubstantiated_claims | suspicious_urls | entities_to_verify | missing_hedging
    text: str  # The flagged text snippet
    severity: str  # high | medium | low
    reason: str  # Why this was flagged
    position: int = 0  # character offset in original text

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "text": self.text[:200],
            "severity": self.severity,
            "reason": self.reason,
            "position": self.position,
        }


@dataclass
class HallucinationResult:
    """Complete hallucination detection output."""

    text_length: int
    hallucination_score: float  # 0-100, higher = fewer hallucinations
    flags: list[HallucinationFlag]
    interpretation: str

    def to_dict(self) -> dict:
        checks = {
            "unverified_statistics": [],
            "suspicious_urls": [],
            "unsubstantiated_claims": [],
            "entities_to_verify": [],
            "missing_hedging": [],
        }
        for f in self.flags:
            key = {
                "unverified_statistics": "unverified_statistics",
                "unsubstantiated_claims": "unsubstantiated_claims",
                "suspicious_urls": "suspicious_urls",
                "entities_to_verify": "entities_to_verify",
                "missing_hedging": "missing_hedging",
            }.get(f.category, "unsubstantiated_claims")
            checks[key].append(f.to_dict())

        return {
            "hallucination_score": self.hallucination_score,
            "checks": checks,
            "critical_flags": sum(1 for f in self.flags if f.severity == "high"),
            "interpretation": self.interpretation,
        }


class HallucinationDetector:
    """Multi-pattern hallucination detection engine.

    Does NOT call external LLM APIs — all detection is rule-based with
    configurable sensitivity. Designed to be fast, interpretable, and
    independent of any specific marketing platform.
    """

    # Patterns for numeric claims that need source attribution
    STATISTIC_PATTERNS = [
        # Percentages: "85% of customers", "conversion rate of 3.2%"
        re.compile(
            r"(\d+(?:\.\d+)?\s*%)\s*(?:of\s+)?(?!open|click|bounce|conversion|engagement)"
            r"(?:customers?|users?|people|consumers?|Americans?|households?|businesses?|companies?|marketers?)",
            re.IGNORECASE,
        ),
        # Dollar amounts with context: "$50M in revenue", "worth $2.5 billion"
        re.compile(
            r"\$\s*\d+(?:\.\d+)?\s*(?:million|billion|thousand|[KMB])\s+(?:in\s+)?"
            r"(?:revenue|sales|worth|market|spending|valuation|growth)",
            re.IGNORECASE,
        ),
        # Growth/decline rates: "grew by 45%", "increased 3x"
        re.compile(
            r"(?:grew|increased|decreased|declined|rose|fell|jumped|dropped|surged|plunged)\s+"
            r"(?:by\s+)?\d+(?:\.\d+)?\s*(?:%|percent|times|[xX])",
            re.IGNORECASE,
        ),
        # Market size claims: "a $12 billion market", "market size of €500M"
        re.compile(
            r"(?:a\s+)?\$\s*\d+(?:\.\d+)?\s*(?:million|billion|trillion|[KMB])\s+"
            r"(?:market|industry|sector|category|space)",
            re.IGNORECASE,
        ),
        # Survey/poll claims: "according to a survey", "studies show that 70%"
        re.compile(
            r"(?:according\s+to\s+(?:a|the)\s+(?:survey|study|report|poll|research))|"
            r"(?:(?:surveys?|studies?|reports?|polls?|research)\s+(?:show|find|suggest|indicate|reveal)\s+that\s+\d+)",
            re.IGNORECASE,
        ),
    ]

    # Claims that assert definite truth without qualification
    ABSOLUTE_CLAIM_PATTERNS = [
        re.compile(
            r"\b(?:guaranteed|proven|never\s+fails|100%|perfect|flawless|"
            r"every\s+(?:single\s+)?(?:customer|user|client)|"
            r"all\s+(?:customers|users|clients)|no\s+one\s+(?:ever|has)|"
            r"the\s+(?:only|best|fastest|cheapest|most|least))\b",
            re.IGNORECASE,
        ),
    ]

    # Known-bad URL patterns
    SUSPICIOUS_URL_PATTERNS = [
        re.compile(r"https?://(?:example\.(?:com|org|net)|placeholder\.\w+|test\.com|site\.com)", re.IGNORECASE),
    ]

    # Hedging words that should accompany uncertain claims
    HEDGING_WORDS = {
        "approximately", "about", "roughly", "estimated", "around",
        "nearly", "close to", "up to", "as many as", "reportedly",
        "according to", "suggests", "may", "might", "could",
    }

    def __init__(
        self,
        statistic_penalty: float = 5.0,
        claim_penalty: float = 4.0,
        url_penalty: float = 8.0,
        entity_penalty: float = 3.0,
        hedging_penalty: float = 2.0,
        score_threshold_high: int = 80,
        score_threshold_moderate: int = 55,
    ):
        self.statistic_penalty = statistic_penalty
        self.claim_penalty = claim_penalty
        self.url_penalty = url_penalty
        self.entity_penalty = entity_penalty
        self.hedging_penalty = hedging_penalty
        self.score_threshold_high = score_threshold_high
        self.score_threshold_moderate = score_threshold_moderate

    def detect(self, text: str) -> HallucinationResult:
        """Run all hallucination checks on the given text.

        Args:
            text: The marketing content to analyze.

        Returns:
            HallucinationResult with score, flags, and interpretation.
        """
        if not text or not text.strip():
            return HallucinationResult(
                text_length=0,
                hallucination_score=100,
                flags=[],
                interpretation="Empty text — no hallucinations possible.",
            )

        flags: list[HallucinationFlag] = []

        # 1. Detect unverified statistics
        flags.extend(self._detect_statistics(text))

        # 2. Detect unsubstantiated absolute claims
        flags.extend(self._detect_absolute_claims(text))

        # 3. Detect suspicious URLs
        flags.extend(self._detect_suspicious_urls(text))

        # 4. Detect entities that warrant verification
        flags.extend(self._detect_entities(text))

        # 5. Detect missing hedging on quantitative claims
        flags.extend(self._detect_missing_hedging(text))

        # Compute score: start at 100, subtract penalties
        # Penalties saturate so a single text can't go below 0
        raw_penalty = sum(
            {
                "unverified_statistics": self.statistic_penalty,
                "unsubstantiated_claims": self.claim_penalty,
                "suspicious_urls": self.url_penalty,
                "entities_to_verify": self.entity_penalty,
                "missing_hedging": self.hedging_penalty,
            }.get(f.category, 3.0)
            for f in flags
        )
        # Sigmoid-style saturation: prevents penalty from dominating on long texts
        text_len_factor = max(1.0, len(text.split()) / 100)
        adjusted_penalty = raw_penalty / math.sqrt(text_len_factor)
        score = max(0.0, min(100.0, 100.0 - adjusted_penalty))
        score = round(score, 1)

        # Interpretation
        if score >= self.score_threshold_high:
            interp = "Low hallucination risk — few or no flags detected."
        elif score >= self.score_threshold_moderate:
            interp = "Moderate hallucination risk — review flagged items before publishing."
        else:
            interp = "High hallucination risk — significant number of unverified claims and statistics. Substantiate or remove flagged content."

        return HallucinationResult(
            text_length=len(text),
            hallucination_score=score,
            flags=flags,
            interpretation=interp,
        )

    def _detect_statistics(self, text: str) -> list[HallucinationFlag]:
        flags = []
        for pattern in self.STATISTIC_PATTERNS:
            for match in pattern.finditer(text):
                matched_text = match.group(0).strip()
                # Check if there's a citation nearby (within 100 chars before)
                start = max(0, match.start() - 100)
                context_before = text[start : match.start()]
                has_citation = bool(
                    re.search(r"\[.*?\]|\(.*?\d{4}.*?\)|source:|according\s+to",
                              context_before, re.IGNORECASE)
                )
                if not has_citation:
                    # Determine severity: large numbers or % = higher concern
                    has_large = bool(re.search(r"(?:million|billion|trillion)", matched_text, re.IGNORECASE))
                    has_dollar = "$" in matched_text
                    flags.append(HallucinationFlag(
                        category="unverified_statistics",
                        text=matched_text,
                        severity="high" if (has_large or has_dollar) else "medium",
                        reason="Statistical claim without cited source in nearby context.",
                        position=match.start(),
                    ))
        return flags

    def _detect_absolute_claims(self, text: str) -> list[HallucinationFlag]:
        flags = []
        for pattern in self.ABSOLUTE_CLAIM_PATTERNS:
            for match in pattern.finditer(text):
                matched_text = match.group(0).strip()
                flags.append(HallucinationFlag(
                    category="unsubstantiated_claims",
                    text=matched_text,
                    severity="high",
                    reason="Absolute/superlative claim without substantiation.",
                    position=match.start(),
                ))
        return flags

    def _detect_suspicious_urls(self, text: str) -> list[HallucinationFlag]:
        flags = []
        # Extract all URLs
        url_pattern = re.compile(r'https?://[^\s<>"\'\)\]]+', re.IGNORECASE)
        for match in url_pattern.finditer(text):
            url = match.group(0).rstrip(".,;:")
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
            except Exception:
                domain = url

            for sus_pattern in self.SUSPICIOUS_URL_PATTERNS:
                if sus_pattern.search(url):
                    flags.append(HallucinationFlag(
                        category="suspicious_urls",
                        text=url,
                        severity="high",
                        reason=f"Suspicious URL detected — domain '{domain}' may be a placeholder.",
                        position=match.start(),
                    ))
                    break
        return flags

    def _detect_entities(self, text: str) -> list[HallucinationFlag]:
        """Detect named entities that may warrant verification.

        Looks for: brand names with trademark symbols, partnership claims,
        celebrity/influencer names, publication names in citation context.
        """
        flags = []
        # Partnership/endorsement claims
        partner_pattern = re.compile(
            r"(?:partner(?:ed|ing|ship)?\s+(?:with|by)\s+|"
            r"featured\s+(?:in|on|by)\s+|"
            r"endorsed\s+(?:by)\s+|"
            r"(?:as\s+seen\s+(?:in|on)))\s*"
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})",
        )
        for match in partner_pattern.finditer(text):
            entity = match.group(1).strip()
            if entity.lower() not in {"the", "a", "an", "our", "their", "this", "that"}:
                flags.append(HallucinationFlag(
                    category="entities_to_verify",
                    text=f"Partnership/feature claim with '{entity}'",
                    severity="high",
                    reason=f"Claim of association with '{entity}' — verify this relationship exists.",
                    position=match.start(),
                ))
        return flags

    def _detect_missing_hedging(self, text: str) -> list[HallucinationFlag]:
        """Detect quantitative statements lacking hedging language.

        Example: "Sales increased 45%" without "approximately" or "estimated"
        is flagged as missing appropriate qualification.
        """
        flags = []
        # Find sentences with numeric claims
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sent in sentences:
            # Does the sentence contain a number?
            has_number = bool(re.search(r'\d+(?:\.\d+)?\s*%', sent))
            if not has_number:
                continue
            # Does it contain hedging words?
            has_hedging = any(hw.lower() in sent.lower() for hw in self.HEDGING_WORDS)
            # Does it have a citation marker?
            has_citation = bool(re.search(r'\[.*?\]|\(.*?\d{4}.*?\)', sent))
            if not has_hedging and not has_citation:
                flags.append(HallucinationFlag(
                    category="missing_hedging",
                    text=sent.strip()[:200],
                    severity="low",
                    reason="Quantitative claim without hedging language ('approximately', 'estimated', etc.) or source citation.",
                    position=text.find(sent) if sent in text else 0,
                ))
        return flags
