"""
Document Section Classifier
===========================
Classifies pages and structural headers into SectionType enumerations using
layout structure, document flow context, and heading hierarchy (No keyword filtering).
"""

from __future__ import annotations
import re
from typing import List
from backend.EvidenceModel.report_tokenizer.schemas import SectionType, TextBlock, ParsedSection


NOISE_SECTION_TYPES = {
    SectionType.COVER_PAGE,
    SectionType.DECLARATION,
    SectionType.CERTIFICATE,
    SectionType.ACKNOWLEDGEMENT,
    SectionType.TABLE_OF_CONTENTS,
    SectionType.LIST_OF_TABLES,
    SectionType.LIST_OF_FIGURES,
    SectionType.ABBREVIATIONS,
    SectionType.REFERENCES,
    SectionType.APPENDIX,
}


class SectionClassifier:
    """Classifies report sections and identifies administrative noise pages."""

    SECTION_PATTERNS = [
        (r"^\s*cover(?:\s+page)?\s*$", SectionType.COVER_PAGE),
        (r"^\s*declaration\s*$", SectionType.DECLARATION),
        (r"^\s*certificate\s*$", SectionType.CERTIFICATE),
        (r"^\s*acknowledg?ment[s]?\s*$", SectionType.ACKNOWLEDGEMENT),
        (r"^\s*abstract\s*$", SectionType.ABSTRACT),
        (r"^\s*(?:table\s+of\s+)?contents\s*$", SectionType.TABLE_OF_CONTENTS),
        (r"^\s*list\s+of\s+tables\s*$", SectionType.LIST_OF_TABLES),
        (r"^\s*list\s+of\s+figures\s*$", SectionType.LIST_OF_FIGURES),
        (r"^\s*abbreviations\s*$", SectionType.ABBREVIATIONS),
        (r"^\s*(?:\d+\.?\s*)?introduction\s*$", SectionType.INTRODUCTION),
        (r"^\s*(?:\d+\.?\s*)?literature\s+review\s*$", SectionType.LITERATURE_REVIEW),
        (r"^\s*(?:\d+\.?\s*)?problem\s+statement\s*$", SectionType.PROBLEM_STATEMENT),
        (r"^\s*(?:\d+\.?\s*)?objectives?\s*$", SectionType.OBJECTIVES),
        (r"^\s*(?:\d+\.?\s*)?methodology\s*$", SectionType.METHODOLOGY),
        (r"^\s*(?:\d+\.?\s*)?architecture(?:\s+ design)?\s*$", SectionType.ARCHITECTURE),
        (r"^\s*(?:\d+\.?\s*)?implementation\s*$", SectionType.IMPLEMENTATION),
        (r"^\s*(?:\d+\.?\s*)?dataset[s]?\s*$", SectionType.DATASET),
        (r"^\s*(?:\d+\.?\s*)?results?(?:\s+and\s+analysis)?\s*$", SectionType.RESULTS),
        (r"^\s*(?:\d+\.?\s*)?discussion\s*$", SectionType.DISCUSSION),
        (r"^\s*(?:\d+\.?\s*)?conclusion[s]?\s*$", SectionType.CONCLUSION),
        (r"^\s*references\s*$", SectionType.REFERENCES),
        (r"^\s*appendix(?:\s+[a-z0-9]+)?\s*$", SectionType.APPENDIX),
    ]

    def classify_heading(self, heading_text: str) -> SectionType:
        """Classifies a structural heading string into a SectionType."""
        normalized = heading_text.strip().lower()
        for pattern, stype in self.SECTION_PATTERNS:
            if re.search(pattern, normalized):
                return stype
        return SectionType.BODY_CONTENT

    def is_administrative_noise(self, section_type: SectionType) -> bool:
        """Determines if a section contains administrative non-evidence noise."""
        return section_type in NOISE_SECTION_TYPES