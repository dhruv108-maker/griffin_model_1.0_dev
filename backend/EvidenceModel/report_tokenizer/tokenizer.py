"""
Griffin Report Tokenizer (GRT)
==============================

Canonical tokenizer for Griffin Core v1.0.

Pipeline
--------
PDF
    ↓
Structural Parsing
    ↓
Metadata Extraction
    ↓
Noise & Duplicate Removal
    ↓
Evidence Construction
    ↓
Evidence Ranking
    ↓
GriffinDocument
"""

from __future__ import annotations

from typing import List, Union

import fitz

from backend.Schemas.schemas import (
    EvidenceToken,
    GriffinDocument,
    GriffinStatistics,
    InputToken,
)

from backend.EvidenceModel.report_tokenizer.schemas import (
    LayoutBoundingBox,
    RawPage,
    TextBlock,
)

from backend.EvidenceModel.report_tokenizer.parser import StructuralParser
from backend.EvidenceModel.report_tokenizer.metadata_extractor import MetadataExtractor
from backend.EvidenceModel.report_tokenizer.duplicate_detector import DuplicateDetector
from backend.EvidenceModel.report_tokenizer.evidence_builder import EvidenceBuilder
from backend.EvidenceModel.report_tokenizer.evidence_ranker import EvidenceRanker


class GriffinReportTokenizer:
    """
    Griffin Report Tokenizer.
    """

    def __init__(self):

        self.parser = StructuralParser()
        self.metadata_extractor = MetadataExtractor()
        self.duplicate_detector = DuplicateDetector()
        self.evidence_builder = EvidenceBuilder()
        self.evidence_ranker = EvidenceRanker()

    def tokenize(
        self,
        pdf_input: Union[str, bytes],
    ) -> GriffinDocument:

        # --------------------------------------------------------------
        # Stage 1 : Structural Parsing
        # --------------------------------------------------------------

        parsed_sections = self.parser.parse_pdf(pdf_input)

        # --------------------------------------------------------------
        # Stage 2 : Raw Pages
        # --------------------------------------------------------------

        document = (
            fitz.open(stream=pdf_input, filetype="pdf")
            if isinstance(pdf_input, bytes)
            else fitz.open(pdf_input)
        )

        raw_pages: List[RawPage] = []

        for page_index, page in enumerate(document):

            blocks: List[TextBlock] = []

            for block in page.get_text("dict")["blocks"]:

                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):

                    for span in line.get("spans", []):

                        blocks.append(
                            TextBlock(
                                text=span.get("text", ""),
                                bbox=LayoutBoundingBox(
                                    x0=span["bbox"][0],
                                    y0=span["bbox"][1],
                                    x1=span["bbox"][2],
                                    y1=span["bbox"][3],
                                    page_width=page.rect.width,
                                    page_height=page.rect.height,
                                ),
                                font_name=span.get("font", ""),
                                font_size=span.get("size", 10.0),
                                is_bold="bold"
                                in span.get("font", "").lower(),
                                is_italic="italic"
                                in span.get("font", "").lower(),
                                page_number=page_index + 1,
                            )
                        )

            raw_pages.append(
                RawPage(
                    page_number=page_index + 1,
                    width=page.rect.width,
                    height=page.rect.height,
                    blocks=blocks,
                )
            )

        document.close()

        # --------------------------------------------------------------
        # Stage 3 : Metadata
        # --------------------------------------------------------------

        metadata = self.metadata_extractor.extract_metadata(raw_pages)

        # --------------------------------------------------------------
        # Stage 4 : Noise Removal
        # --------------------------------------------------------------

        filtered_sections = []
        excluded_pages = set()

        for section in parsed_sections:

            if section.is_noise:
                excluded_pages.add(section.page_number)
                continue

            section_text = " ".join(
                block.text
                for block in section.blocks
            )

            if self.duplicate_detector.is_duplicate(section_text):
                continue

            filtered_sections.append(section)

        # --------------------------------------------------------------
        # Stage 5 : Evidence Construction
        # --------------------------------------------------------------

        evidence_tokens: List[EvidenceToken] = (
            self.evidence_builder.build_evidence_tokens(
                filtered_sections
            )
        )

        # --------------------------------------------------------------
        # Stage 6 : Ranking
        # --------------------------------------------------------------

        evidence_tokens = self.evidence_ranker.rank_and_score_tokens(
            evidence_tokens
        )

        # --------------------------------------------------------------
        # Stage 7 : Statistics
        # --------------------------------------------------------------

        total_blocks = sum(
            len(section.blocks)
            for section in parsed_sections
        )

        statistics = GriffinStatistics(
            total_pages=len(raw_pages),
            total_input_tokens=0,
            total_evidence_tokens=len(evidence_tokens),
            total_figures=sum(
                len(token.figure_refs)
                for token in evidence_tokens
            ),
            total_tables=sum(
                len(token.table_refs)
                for token in evidence_tokens
            ),
            total_equations=sum(
                len(token.equation_refs)
                for token in evidence_tokens
            ),
            total_citations=sum(
                len(token.citations)
                for token in evidence_tokens
            ),
        )

        # --------------------------------------------------------------
        # NOTE
        # --------------------------------------------------------------
        #
        # EvidenceBuilder MUST now return:
        #
        # List[backend.Schemas.schemas.EvidenceToken]
        #
        # NOT
        #
        # backend.EvidenceModel.report_tokenizer.schemas.EvidenceToken
        #
        # Otherwise ReportEncoder will fail when assigning embeddings.
        #
        # --------------------------------------------------------------

        return GriffinDocument(
            version="1.0",
            metadata=metadata,
            statistics=statistics,
            input_tokens=[],  # Populate when InputToken generation is migrated
            tokens=evidence_tokens,
        )