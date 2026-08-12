"""
Report Metadata Extractor
=========================
Extracts document-level metadata from the report front matter.
"""

from __future__ import annotations

import re
from typing import List, Optional

from backend.EvidenceModel.report_tokenizer.schemas import (
    RawPage,
    TextBlock,
)

from backend.Schemas.schemas import ReportMetadata


class MetadataExtractor:
    """Extract document metadata from the first few pages."""

    DATE_REGEX = (
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\b"
    )

    YEAR_REGEX = r"\b(19|20)\d{2}\b"

    def extract_metadata(
        self,
        pages: List[RawPage],
    ) -> ReportMetadata:

        metadata = ReportMetadata(
            total_pages=len(pages)
        )

        if not pages:
            return metadata

        front_text = ""
        front_blocks: List[TextBlock] = []

        for page in pages[:5]:
            for block in page.blocks:
                front_text += block.text + "\n"
                front_blocks.append(block)

        metadata.title = self._extract_title(front_blocks)
        metadata.author = self._extract_field(
            front_text,
            [
                "prepared by",
                "submitted by",
                "author",
                "student name",
            ],
        )

        metadata.institution = self._extract_field(
            front_text,
            [
                "institution",
                "college",
                "institute",
            ],
        )

        metadata.department = self._extract_field(
            front_text,
            [
                "department",
                "school",
            ],
        )

        metadata.university = self._extract_field(
            front_text,
            [
                "university",
            ],
        )

        metadata.guide = self._extract_field(
            front_text,
            [
                "guide",
                "internal guide",
                "guided by",
            ],
        )

        metadata.supervisor = self._extract_field(
            front_text,
            [
                "supervisor",
                "mentor",
                "project supervisor",
            ],
        )

        metadata.degree = self._extract_field(
            front_text,
            [
                "b.tech",
                "m.tech",
                "bachelor",
                "master",
                "phd",
            ],
        )

        metadata.date = self._extract_regex(
            front_text,
            self.DATE_REGEX,
        )

        metadata.year = self._extract_regex(
            front_text,
            self.YEAR_REGEX,
        )

        metadata.raw_metadata = {
            "source": "MetadataExtractor"
        }

        return metadata

    def _extract_title(
        self,
        blocks: List[TextBlock],
    ) -> Optional[str]:

        if not blocks:
            return None

        largest = max(
            blocks,
            key=lambda b: b.font_size,
        )

        if largest.font_size >= 14:
            return largest.text.strip().replace("\n", " ")

        return None

    def _extract_regex(
        self,
        text: str,
        pattern: str,
    ) -> Optional[str]:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(0).strip()

        return None

    def _extract_field(
        self,
        text: str,
        labels: List[str],
    ) -> Optional[str]:

        for label in labels:

            pattern = rf"{re.escape(label)}\s*:?\s*([^\n\r]+)"

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(1).strip()

        return None