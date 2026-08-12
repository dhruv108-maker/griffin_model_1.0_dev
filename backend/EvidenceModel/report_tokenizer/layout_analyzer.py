"""
PDF Layout Analyzer
===================
Analyzes page spatial properties, typography, font metrics, and bounding boxes.
Separates body blocks from top/bottom margin header/footer regions.
"""

from __future__ import annotations
from typing import List, Tuple
from backend.EvidenceModel.report_tokenizer.schemas import RawPage, TextBlock


class LayoutAnalyzer:
    """Analyzes spatial and typographic characteristics of report pages."""

    def __init__(self, header_margin_ratio: float = 0.08, footer_margin_ratio: float = 0.08):
        self.header_margin_ratio = header_margin_ratio
        self.footer_margin_ratio = footer_margin_ratio

    def analyze_page_layout(self, page: RawPage) -> Tuple[List[TextBlock], List[TextBlock]]:
        """
        Splits page text blocks into body content blocks and margin noise blocks (headers/footers).
        """
        body_blocks: List[TextBlock] = []
        margin_blocks: List[TextBlock] = []

        header_boundary = page.height * self.header_margin_ratio
        footer_boundary = page.height * (1.0 - self.footer_margin_ratio)

        for block in page.blocks:
            # Check bounding box position against page margins
            if block.bbox.y1 <= header_boundary or block.bbox.y0 >= footer_boundary:
                margin_blocks.append(block)
            else:
                body_blocks.append(block)

        return body_blocks, margin_blocks

    def detect_heading_level(self, block: TextBlock, mean_font_size: float) -> int:
        """
        Determines structural heading hierarchy (0=Body, 1=Chapter/H1, 2=Section/H2, 3=Subsection/H3).
        """
        if not block.is_bold and block.font_size <= mean_font_size:
            return 0

        size_ratio = block.font_size / mean_font_size if mean_font_size > 0 else 1.0

        if size_ratio >= 1.4 or (block.is_bold and size_ratio >= 1.25):
            return 1  # Chapter / Main Title
        elif size_ratio >= 1.15 or (block.is_bold and size_ratio >= 1.05):
            return 2  # Section
        elif block.is_bold:
            return 3  # Subsection

        return 0