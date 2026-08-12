"""
Griffin Report Tokenizer (GRT)
==============================
Core tokenizer model for Griffin Model 1.0.
Transforms academic report PDFs into structured, semantic, curriculum-aware evidence tokens.
"""

from backend.EvidenceModel.report_tokenizer.tokenizer import GriffinReportTokenizer
from backend.EvidenceModel.report_tokenizer.schemas import (
    EvidenceToken,
    ReportMetadata,
    StructuredReportDocument,
    SectionType,
)

__all__ = [
    "GriffinReportTokenizer",
    "EvidenceToken",
    "ReportMetadata",
    "StructuredReportDocument",
    "SectionType",
]