"""
Evidence Block Construction Engine
==================================
Aggregates structural text sections into canonical Griffin EvidenceTokens.
"""

from __future__ import annotations

import re
import uuid
from typing import List

from backend.EvidenceModel.report_tokenizer.schemas import (
    ParsedSection,
)

from backend.Schemas.schemas import EvidenceToken

from backend.EvidenceModel.report_tokenizer.utils import (
    extract_formulas,
    extract_figure_and_table_refs,
    extract_academic_citations,
    TECHNICAL_INDICATORS,
)


class EvidenceBuilder:
    """Construct canonical EvidenceTokens from parsed report sections."""

    def build_evidence_tokens(
        self,
        sections: List[ParsedSection],
    ) -> List[EvidenceToken]:

        evidence_tokens: List[EvidenceToken] = []

        for sec in sections:

            if sec.is_noise or not sec.blocks:
                continue

            full_text = "\n".join(
                block.text.strip()
                for block in sec.blocks
                if block.text.strip()
            )

            if len(full_text) < 30:
                continue

            concepts = self._extract_concepts(full_text)
            entities = self._extract_entities(full_text)
            keywords = self._extract_keywords(full_text)

            equations = extract_formulas(full_text)
            figures, tables = extract_figure_and_table_refs(full_text)
            citations = extract_academic_citations(full_text)

            token = EvidenceToken(
                token_id=f"grt_{uuid.uuid4().hex[:12]}",
                page_number=sec.page_number,
                chapter=sec.chapter,
                section=sec.section,
                subsection=sec.subsection,
                heading=sec.heading,
                text=full_text,
                token_type="SECTION",
                category=self._infer_category(sec),

                parent_token=None,

                concepts=concepts,
                entities=entities,
                keywords=keywords,

                citations=citations,
                figure_refs=figures,
                table_refs=tables,
                equation_refs=equations,

                semantic_density=0.0,
                technical_density=0.0,
                information_gain=0.0,
                priority=0.0,
                confidence=1.0,

                embedding=None,
                embedding_model=None,
                embedding_dimension=None,

                source_page=sec.page_number,
                source_bbox=None,
                source_id=None,

                metadata={},
            )

            evidence_tokens.append(token)

        return evidence_tokens

    def _extract_concepts(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        return sorted({
            word
            for word in words
            if word in TECHNICAL_INDICATORS
        })

    def _extract_entities(self, text: str) -> List[str]:

        acronyms = set(
            re.findall(r"\b[A-Z]{2,6}\b", text)
        )

        camel_case = set(
            re.findall(
                r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b",
                text,
            )
        )

        return sorted(acronyms | camel_case)

    def _extract_keywords(self, text: str) -> List[str]:

        words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            text.lower(),
        )

        stopwords = {
            "this", "that", "with", "from", "into",
            "have", "been", "were", "their", "there",
            "which", "using", "used", "than", "also",
            "such", "these", "those", "where", "when",
            "will", "shall", "could", "would", "about",
            "between", "because", "while"
        }

        keywords = {
            word
            for word in words
            if word not in stopwords
        }

        return sorted(keywords)

    def _infer_category(self, section: ParsedSection) -> str:

        heading = (section.heading or "").lower()

        if "abstract" in heading:
            return "ABSTRACT"

        if "introduction" in heading:
            return "INTRODUCTION"

        if "method" in heading:
            return "METHODOLOGY"

        if "result" in heading:
            return "RESULTS"

        if "discussion" in heading:
            return "DISCUSSION"

        if "conclusion" in heading:
            return "CONCLUSION"

        if "reference" in heading:
            return "REFERENCES"

        return "CONTENT"