"""
Evidence Density and Technical Relevance Ranker
===============================================
Computes technical_density, semantic_density,
and information_gain for canonical Griffin EvidenceTokens.
"""

from __future__ import annotations

import re
from typing import List

from backend.Schemas.schemas import EvidenceToken

from backend.EvidenceModel.report_tokenizer.utils import (
    calculate_shannon_entropy,
    TECHNICAL_INDICATORS,
    TECHNICAL_STOPWORDS,
)


CATEGORY_PRIORS = {
    "METHODOLOGY": 1.00,
    "ARCHITECTURE": 0.98,
    "IMPLEMENTATION": 0.95,
    "RESULTS": 0.92,
    "PROBLEM_STATEMENT": 0.90,
    "OBJECTIVES": 0.88,
    "LITERATURE_REVIEW": 0.75,
    "INTRODUCTION": 0.70,
    "DISCUSSION": 0.85,
    "CONCLUSION": 0.80,
    "ABSTRACT": 0.60,
    "REFERENCES": 0.40,
    "CONTENT": 0.75,
}


class EvidenceRanker:
    """
    Computes semantic density, technical density and information gain
    for canonical EvidenceTokens.
    """

    def rank_and_score_tokens(
        self,
        tokens: List[EvidenceToken],
    ) -> List[EvidenceToken]:

        for token in tokens:

            tech_density = self._calculate_technical_density(token)
            sem_density = self._calculate_semantic_density(token)
            info_gain = self._calculate_information_gain(
                token,
                tech_density,
                sem_density,
            )

            token.technical_density = round(tech_density, 4)
            token.semantic_density = round(sem_density, 4)
            token.information_gain = round(info_gain, 4)

        return tokens

    def _calculate_technical_density(
        self,
        token: EvidenceToken,
    ) -> float:

        words = re.findall(r"\b\w+\b", token.text.lower())

        if not words:
            return 0.0

        tech_count = sum(
            1
            for word in words
            if word in TECHNICAL_INDICATORS
        )

        tech_count += len(token.concepts) * 2
        tech_count += len(token.entities) * 2
        tech_count += len(token.equation_refs) * 3
        tech_count += len(token.figure_refs)
        tech_count += len(token.table_refs)
        tech_count += len(token.citations)

        density = tech_count / len(words)

        return float(min(1.0, max(0.0, density)))

    def _calculate_semantic_density(
        self,
        token: EvidenceToken,
    ) -> float:

        words = re.findall(
            r"\b[a-zA-Z]{2,}\b",
            token.text.lower(),
        )

        if not words:
            return 0.0

        content_words = [
            w
            for w in words
            if w not in TECHNICAL_STOPWORDS
        ]

        if not content_words:
            return 0.0

        unique_ratio = (
            len(set(content_words))
            / len(content_words)
        )

        entropy = calculate_shannon_entropy(
            token.text
        )

        semantic_density = (
            (0.6 * unique_ratio)
            + (0.4 * entropy)
        )

        return float(
            min(1.0, max(0.0, semantic_density))
        )

    def _calculate_information_gain(
        self,
        token: EvidenceToken,
        technical_density: float,
        semantic_density: float,
    ) -> float:

        prior = CATEGORY_PRIORS.get(
            token.category.upper(),
            0.75,
        )

        gain = (
            (0.40 * technical_density)
            + (0.35 * semantic_density)
            + (0.25 * prior)
        )

        return float(
            min(1.0, max(0.0, gain))
        )