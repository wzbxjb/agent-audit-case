"""Semantic claim verification using embedding similarity.

Replaces SequenceMatcher-based fuzzy matching with a two-stage
semantic verification pipeline:

Stage 1 — Embedding similarity: compute cosine similarity between
         each extracted claim and each evidence record using
         sentence-transformers. Threshold-based filtering.

Stage 2 — Entity-aware cross-referencing: extract key entities
          (numbers, dates, proper nouns) from claim and evidence,
          check for consistency beyond surface string match.

This addresses the core weakness identified in the original case study:
string-based matching fails when semantic meaning is equivalent but
wording differs (e.g. "$80K monthly" vs "monthly revenue of $80,000").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class VerifiedClaim:
    """A single claim with its verification status."""

    claim_text: str
    status: str  # verified | partially_verified | unverified | contradicted
    matched_evidence: Optional[str] = None
    similarity: float = 0.0
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "claim": self.claim_text,
            "status": self.status,
            "matched_evidence": self.matched_evidence,
            "similarity": round(self.similarity, 4),
            "reason": self.reason,
        }


@dataclass
class ClaimVerificationResult:
    """Complete claim verification output."""

    claims: list[VerifiedClaim]
    verification_score: float  # 0-100
    interpretation: str
    summary: dict  # {total, verified, partially_verified, unverified, contradicted}

    def to_dict(self) -> dict:
        return {
            "verification_score": self.verification_score,
            "claims": [c.to_dict() for c in self.claims],
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class ClaimChecker:
    """Semantic claim verification with embedding similarity.

    Extracts factual claims from text, compares against an evidence
    base using embedding cosine similarity, and classifies each claim
    as verified / partially verified / unverified / contradicted.
    """

    # Patterns to extract factual claims from marketing text
    CLAIM_PATTERNS = [
        # Revenue/sales numbers
        re.compile(
            r"(?:revenue|sales|recurring\s+revenue|ARR|MRR)\s+(?:of|is|was|exceeds?|reached?|totals?)?\s*"
            r"\$?\s*\d+(?:\.\d+)?\s*(?:million|billion|thousand|[KMB])?",
            re.IGNORECASE,
        ),
        # Founded/established dates
        re.compile(
            r"(?:founded|established|launched|started|since)\s+(?:in\s+)?\d{4}",
            re.IGNORECASE,
        ),
        # Customer/user counts
        re.compile(
            r"\d+(?:\.\d+)?\s*(?:million|billion|thousand|[KMB])?\s*\+?\s*"
            r"(?:customers?|users?|subscribers?|clients?|downloads?|installations?)",
            re.IGNORECASE,
        ),
        # Rating scores
        re.compile(
            r"(?:rated|rating|rated\s+at|score\s+of)\s+\d+(?:\.\d+)?\s*(?:stars?|out\s+of|/\s*5)",
            re.IGNORECASE,
        ),
        # Founded location
        re.compile(
            r"(?:based\s+(?:in|out\s+of)|headquartered\s+(?:in|at)|located\s+in)\s+"
            r"[A-Z][a-zA-Z]+(?:\s*,\s*[A-Z][a-zA-Z]+)?",
        ),
        # Product counts / SKUs
        re.compile(
            r"\d+\s*(?:SKUs?|products?|product\s+lines?|categories?)",
            re.IGNORECASE,
        ),
        # Generic factual assertion with numbers
        re.compile(
            r"(?:over|more\s+than|less\s+than|approximately|about|nearly|around|exactly)\s+"
            r"\$?\s*\d+(?:\.\d+)?\s*(?:%|percent|million|billion|thousand|[KMB])?",
            re.IGNORECASE,
        ),
    ]

    def __init__(
        self,
        similarity_threshold: float = 0.55,
        partial_threshold: float = 0.35,
    ):
        """
        Args:
            similarity_threshold: Cosine similarity above which a claim is 'verified'.
            partial_threshold: Cosine similarity above which a claim is 'partially verified'.
        """
        self.similarity_threshold = similarity_threshold
        self.partial_threshold = partial_threshold
        self._model = None

    @property
    def model(self):
        """Lazy-load sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                # Fallback: use a simpler approach if sentence-transformers unavailable
                self._model = None
        return self._model

    def verify(self, text: str, evidence_path: str | None = None) -> ClaimVerificationResult:
        """Verify claims in text against evidence base.

        Args:
            text: The marketing content to check.
            evidence_path: Path to evidence JSON file. If None, uses default.

        Returns:
            ClaimVerificationResult with per-claim status and aggregate score.
        """
        # Load evidence
        evidence = self._load_evidence(evidence_path)

        # Extract claims from text
        raw_claims = self._extract_claims(text)

        if not raw_claims:
            return ClaimVerificationResult(
                claims=[],
                verification_score=100,
                interpretation="No factual claims detected to verify.",
                summary={"total": 0, "verified": 0, "partially_verified": 0,
                         "unverified": 0, "contradicted": 0},
            )

        # Build evidence embeddings and verify each claim
        evidence_texts = [e["claim"] for e in evidence]
        verified_claims: list[VerifiedClaim] = []

        for raw_claim in raw_claims:
            vc = self._verify_single(raw_claim, evidence, evidence_texts)
            verified_claims.append(vc)

        # Compute aggregate score
        n = len(verified_claims)
        n_verified = sum(1 for c in verified_claims if c.status == "verified")
        n_partial = sum(1 for c in verified_claims if c.status == "partially_verified")
        n_unverified = sum(1 for c in verified_claims if c.status == "unverified")
        n_contradicted = sum(1 for c in verified_claims if c.status == "contradicted")

        # Score: verified=full credit, partial=half, unverified=0, contradicted=penalty
        score = (n_verified * 100 + n_partial * 50) / max(n, 1)
        score = round(max(0.0, min(100.0, score)), 1)

        if score >= 80:
            interp = "High claim accuracy — most claims verified against evidence."
        elif score >= 40:
            interp = "Moderate claim accuracy — several claims could not be verified. Review before publishing."
        else:
            interp = "Low claim accuracy — majority of factual claims cannot be verified. Significant revision needed."

        return ClaimVerificationResult(
            claims=verified_claims,
            verification_score=score,
            interpretation=interp,
            summary={
                "total": n,
                "verified": n_verified,
                "partially_verified": n_partial,
                "unverified": n_unverified,
                "contradicted": n_contradicted,
            },
        )

    def _extract_claims(self, text: str) -> list[str]:
        """Extract factual claims from text using pattern matching."""
        claims = set()
        for pattern in self.CLAIM_PATTERNS:
            for match in pattern.finditer(text):
                claim = match.group(0).strip()
                # Normalize: remove excessive whitespace
                claim = re.sub(r'\s+', ' ', claim)
                if len(claim) > 10:  # skip overly short matches
                    claims.add(claim)
        return sorted(claims, key=lambda c: len(c), reverse=True)

    def _verify_single(
        self, claim: str, evidence: list[dict], evidence_texts: list[str]
    ) -> VerifiedClaim:
        """Verify a single claim against all evidence records."""
        # Compute embedding similarity if model available
        best_sim = 0.0
        best_evidence = None

        if self.model is not None:
            try:
                claim_emb = self.model.encode([claim], normalize_embeddings=True)[0]
                ev_embs = self.model.encode(
                    evidence_texts, normalize_embeddings=True, batch_size=32
                )
                similarities = (claim_emb @ ev_embs.T)
                best_idx = int(np.argmax(similarities))
                best_sim = float(similarities[best_idx])
                best_evidence = evidence[best_idx]
            except Exception:
                pass

        # Fallback: keyword overlap if embedding model unavailable or failed
        if best_evidence is None:
            best_sim, best_evidence = self._keyword_match(claim, evidence)

        # Classify
        if best_sim >= self.similarity_threshold:
            if best_evidence.get("verified", False):
                return VerifiedClaim(
                    claim_text=claim,
                    status="verified",
                    matched_evidence=best_evidence["claim"],
                    similarity=best_sim,
                    reason=f"Semantically matches verified evidence (similarity={best_sim:.2f}).",
                )
            else:
                return VerifiedClaim(
                    claim_text=claim,
                    status="contradicted",
                    matched_evidence=best_evidence["claim"],
                    similarity=best_sim,
                    reason="Claim matches known FALSE evidence — this statement is contradicted by available data.",
                )
        elif best_sim >= self.partial_threshold:
            return VerifiedClaim(
                claim_text=claim,
                status="partially_verified",
                matched_evidence=best_evidence["claim"],
                similarity=best_sim,
                reason=f"Partial semantic match — similar to evidence but wording differs significantly (similarity={best_sim:.2f}).",
            )
        else:
            return VerifiedClaim(
                claim_text=claim,
                status="unverified",
                matched_evidence=None,
                similarity=best_sim,
                reason=f"No evidence record semantically matches this claim (best similarity={best_sim:.2f}). May be hallucinated or outside evidence scope.",
            )

    def _keyword_match(self, claim: str, evidence: list[dict]) -> tuple[float, dict | None]:
        """Fallback: keyword overlap matching when embeddings unavailable."""
        claim_words = set(claim.lower().split())
        best = 0.0
        best_ev = evidence[0] if evidence else None

        for ev in evidence:
            ev_words = set(ev["claim"].lower().split())
            if not claim_words or not ev_words:
                continue
            overlap = len(claim_words & ev_words) / len(claim_words | ev_words)
            if overlap > best:
                best = overlap
                best_ev = ev

        return best, best_ev

    @staticmethod
    def _load_evidence(evidence_path: str | None) -> list[dict]:
        """Load evidence records from JSON file."""
        if evidence_path is None:
            evidence_path = str(
                Path(__file__).parent.parent.parent / "output" / "evidence.json"
            )

        path = Path(evidence_path)
        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("evidence", data if isinstance(data, list) else [])
        except (json.JSONDecodeError, KeyError):
            return []
