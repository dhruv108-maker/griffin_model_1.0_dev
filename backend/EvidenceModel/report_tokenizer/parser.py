"""
Document Structural Parsing Engine
==================================
Extracts spatial layout elements from PDF reports and builds a hierarchical tree structure
(Chapter -> Section -> Subsection -> TextBlocks).
"""

from __future__ import annotations
import fitz  # PyMuPDF
from typing import List, Tuple
from backend.EvidenceModel.report_tokenizer.schemas import (
    RawPage,
    TextBlock,
    LayoutBoundingBox,
    ParsedSection,
    SectionType
)
from backend.EvidenceModel.report_tokenizer.layout_analyzer import LayoutAnalyzer
from backend.EvidenceModel.report_tokenizer.section_classifier import SectionClassifier


class StructuralParser:
    """Parses raw PDF bytes or file paths into layout-aware document structures."""

    def __init__(self):
        self.layout_analyzer = LayoutAnalyzer()
        self.section_classifier = SectionClassifier()

    def parse_pdf(self, pdf_input: str | bytes) -> List[ParsedSection]:
        """Extracts text blocks and builds a tree of structural document sections."""
        doc = fitz.open(stream=pdf_input, filetype="pdf") if isinstance(pdf_input, bytes) else fitz.open(pdf_input)
        raw_pages: List[RawPage] = []

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            page_width = page.rect.width
            page_height = page.rect.height
            text_blocks: List[TextBlock] = []

            # Extract spatial text blocks from PyMuPDF layout engine
            text_instances = page.get_text("dict")["blocks"]
            for b in text_instances:
                if b.get("type") != 0:  # Text block
                    continue

                for line in b.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue

                        bbox = LayoutBoundingBox(
                            x0=span["bbox"][0],
                            y0=span["bbox"][1],
                            x1=span["bbox"][2],
                            y1=span["bbox"][3],
                            page_width=page_width,
                            page_height=page_height
                        )

                        flags = span.get("flags", 0)
                        is_bold = bool(flags & 2) or ("bold" in span.get("font", "").lower())
                        is_italic = bool(flags & 1) or ("italic" in span.get("font", "").lower())

                        block = TextBlock(
                            text=text,
                            bbox=bbox,
                            font_name=span.get("font", "unknown"),
                            font_size=span.get("size", 10.0),
                            is_bold=is_bold,
                            is_italic=is_italic,
                            page_number=page_num
                        )
                        text_blocks.append(block)

            raw_pages.append(RawPage(page_number=page_num, width=page_width, height=page_height, blocks=text_blocks))

        doc.close()
        return self._build_structural_sections(raw_pages)

    def _build_structural_sections(self, pages: List[RawPage]) -> List[ParsedSection]:
        """Groups layout blocks into logical hierarchical document sections."""
        parsed_sections: List[ParsedSection] = []

        current_chapter = "General"
        current_section = "Main"
        current_subsection = "Content"
        current_heading = "Overview"

        for page in pages:
            body_blocks, _ = self.layout_analyzer.analyze_page_layout(page)
            if not body_blocks:
                continue

            all_sizes = [b.font_size for b in body_blocks]
            mean_size = sum(all_sizes) / len(all_sizes) if all_sizes else 10.0

            current_section_blocks: List[TextBlock] = []

            for block in body_blocks:
                heading_level = self.layout_analyzer.detect_heading_level(block, mean_size)

                if heading_level > 0:
                    # Flush current accumulated block section
                    if current_section_blocks:
                        stype = self.section_classifier.classify_heading(current_heading)
                        parsed_sections.append(
                            ParsedSection(
                                chapter=current_chapter,
                                section=current_section,
                                subsection=current_subsection,
                                section_type=stype,
                                heading=current_heading,
                                page_number=page.page_number,
                                blocks=current_section_blocks,
                                is_noise=self.section_classifier.is_administrative_noise(stype)
                            )
                        )
                        current_section_blocks = []

                    current_heading = block.text
                    if heading_level == 1:
                        current_chapter = block.text
                        current_section = "Main"
                        current_subsection = "Overview"
                    elif heading_level == 2:
                        current_section = block.text
                        current_subsection = "Overview"
                    elif heading_level == 3:
                        current_subsection = block.text
                else:
                    current_section_blocks.append(block)

            # Flush remaining blocks on page
            if current_section_blocks:
                stype = self.section_classifier.classify_heading(current_heading)
                parsed_sections.append(
                    ParsedSection(
                        chapter=current_chapter,
                        section=current_section,
                        subsection=current_subsection,
                        section_type=stype,
                        heading=current_heading,
                        page_number=page.page_number,
                        blocks=current_section_blocks,
                        is_noise=self.section_classifier.is_administrative_noise(stype)
                    )
                )

        return parsed_sections