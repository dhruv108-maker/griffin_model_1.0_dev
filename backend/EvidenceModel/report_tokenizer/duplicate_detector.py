"""
Duplicate and Repetitive Content Detector
=========================================
Removes repeated headers, footers, institutional disclaimers, and duplicate paragraphs
using semantic SimHash signatures and MinHash similarity.
"""

from __future__ import annotations
from typing import Set, List
from backend.EvidenceModel.report_tokenizer.schemas import TextBlock
from backend.EvidenceModel.report_tokenizer.utils import compute_simhash_signature


class DuplicateDetector:
    """Detects and filters duplicate and repetitive blocks across document pages."""

    def __init__(self, hamming_threshold: int = 3):
        self.hamming_threshold = hamming_threshold
        self.seen_signatures: List[str] = []

    def is_duplicate(self, text: str) -> bool:
        """Checks if a text block is semantically identical to a previously indexed block."""
        if len(text.strip()) < 15:
            return False  # Skip short elements

        signature = compute_simhash_signature(text)
        for prev in self.seen_signatures:
            if self._hamming_distance(signature, prev) <= self.hamming_threshold:
                return True

        self.seen_signatures.append(signature)
        return False

    def filter_margin_duplicates(self, margin_blocks: List[TextBlock]) -> List[TextBlock]:
        """Identifies repetitive page headers and footers across pages."""
        text_counts: dict[str, int] = {}
        for block in margin_blocks:
            clean = block.text.strip().lower()
            text_counts[clean] = text_counts.get(clean, 0) + 1

        # Margin blocks appearing on > 2 pages are repetitive running headers/footers
        unique_margins = []
        for block in margin_blocks:
            clean = block.text.strip().lower()
            if text_counts.get(clean, 0) <= 2:
                unique_margins.append(block)

        return unique_margins

    @staticmethod
    def _hamming_distance(hex1: str, hex2: str) -> int:
        val1 = int(hex1, 16)
        val2 = int(hex2, 16)
        x = val1 ^ val2
        dist = 0
        while x > 0:
            dist += x & 1
            x >>= 1
        return dist