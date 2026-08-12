"""
Data Schemas for Griffin Report Tokenizer (GRT)
==============================================
Typed Pydantic and dataclass models representing document layout, metadata,
classified sections, evidence blocks, and final Evidence Tokens.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SectionType(str, Enum):
    """Academic document section categories for structural classification."""
    COVER_PAGE = "COVER_PAGE"
    DECLARATION = "DECLARATION"
    CERTIFICATE = "CERTIFICATE"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    ABSTRACT = "ABSTRACT"
    TABLE_OF_CONTENTS = "TABLE_OF_CONTENTS"
    LIST_OF_TABLES = "LIST_OF_TABLES"
    LIST_OF_FIGURES = "LIST_OF_FIGURES"
    ABBREVIATIONS = "ABBREVIATIONS"
    INTRODUCTION = "INTRODUCTION"
    LITERATURE_REVIEW = "LITERATURE_REVIEW"
    PROBLEM_STATEMENT = "PROBLEM_STATEMENT"
    OBJECTIVES = "OBJECTIVES"
    METHODOLOGY = "METHODOLOGY"
    ARCHITECTURE = "ARCHITECTURE"
    IMPLEMENTATION = "IMPLEMENTATION"
    DATASET = "DATASET"
    RESULTS = "RESULTS"
    DISCUSSION = "DISCUSSION"
    CONCLUSION = "CONCLUSION"
    REFERENCES = "REFERENCES"
    APPENDIX = "APPENDIX"
    BODY_CONTENT = "BODY_CONTENT"
    UNKNOWN = "UNKNOWN"


class LayoutBoundingBox(BaseModel):
    """Spatial bounding box coordinates on a PDF page."""
    x0: float
    y0: float
    x1: float
    y1: float
    page_width: float
    page_height: float


class TextBlock(BaseModel):
    """Low-level structural text element extracted from PDF page layout."""
    text: str
    bbox: LayoutBoundingBox
    font_name: str
    font_size: float
    is_bold: bool
    is_italic: bool
    page_number: int
    line_spacing: float = 0.0


class RawPage(BaseModel):
    """Raw extracted layout and textual elements of a single page."""
    page_number: int
    width: float
    height: float
    blocks: List[TextBlock] = Field(default_factory=list)


class ReportMetadata(BaseModel):
    """Extracted document metadata stored separately from evidence tokens."""
    title: Optional[str] = None
    author: Optional[str] = None
    enrollment: Optional[str] = None
    mentor: Optional[str] = None
    industry_mentor: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    degree: Optional[str] = None
    submission_date: Optional[str] = None
    report_type: Optional[str] = None
    total_pages: int = 0
    raw_attributes: Dict[str, Any] = Field(default_factory=dict)


class ParsedSection(BaseModel):
    """Hierarchical node representing document structural organization."""
    chapter: str
    section: str
    subsection: str
    section_type: SectionType
    heading: str
    page_number: int
    blocks: List[TextBlock] = Field(default_factory=list)
    is_noise: bool = False


class EvidenceToken(BaseModel):
    """
    High-definition semantic evidence token emitted by GRT for Griffin consumption.
    Consumed by ReportEncoder, EvidenceRetriever, EvidenceValidator, and EvidenceGraphBuilder.
    """
    token_id: str
    chapter: str
    section: str
    subsection: str
    page: int
    heading: str
    text: str
    concepts: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    formula_refs: List[str] = Field(default_factory=list)
    figure_refs: List[str] = Field(default_factory=list)
    table_refs: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    technical_density: float = Field(ge=0.0, le=1.0)
    semantic_density: float = Field(ge=0.0, le=1.0)
    information_gain: float = Field(ge=0.0, le=1.0)


class StructuredReportDocument(BaseModel):
    """Complete output artifact produced by Griffin Report Tokenizer."""
    metadata: ReportMetadata
    tokens: List[EvidenceToken] = Field(default_factory=list)
    excluded_pages: List[int] = Field(default_factory=list)
    total_raw_blocks: int = 0
    retained_evidence_blocks: int = 0