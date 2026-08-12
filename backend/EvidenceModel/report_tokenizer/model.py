"""
Griffin Report Tokenizer Pipeline (v1.0)
========================================

Canonical processing pipeline for Griffin's document tokenizer.

Purpose
-------
Transforms academic reports into structured, semantically enriched
Griffin Evidence Tokens for downstream retrieval, reasoning,
curriculum mapping, and assessment.

Pipeline
--------
PDF / DOCX
      │
      ▼
Document Parsing
      │
      ▼
Structure Extraction
      │
      ▼
Metadata Extraction
      │
      ▼
Labeled Input Token Generation
      │
      ▼
Semantic Enrichment
      │
      ▼
Griffin Evidence Token Generation
      │
      ▼
GriffinDocument
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PipelineStage:
    """Represents one stage of the Griffin tokenizer pipeline."""

    name: str
    description: str


class GriffinTokenizerPipeline:
    """
    Griffin Tokenizer v1.0 Pipeline

    This class documents the canonical tokenizer workflow.
    It contains no business logic.
    """

    VERSION = "1.0"

    STAGES: List[PipelineStage] = [

        PipelineStage(
            "Document Parsing",
            "Load PDF/DOCX and extract raw document blocks."
        ),

        PipelineStage(
            "Structure Extraction",
            "Identify pages, headings, chapters, sections, tables, figures and equations."
        ),

        PipelineStage(
            "Metadata Extraction",
            "Extract document-level metadata such as title, author and page count."
        ),

        PipelineStage(
            "Labeled Input Token Generation",
            "Convert structured blocks into labeled input tokens."
        ),

        PipelineStage(
            "Semantic Enrichment",
            "Extract concepts, entities, references and compute density metrics."
        ),

        PipelineStage(
            "Griffin Evidence Token Generation",
            "Generate optimized Griffin Evidence Tokens."
        ),

        PipelineStage(
            "GriffinDocument",
            "Package metadata, statistics, input tokens and evidence tokens."
        ),
    ]

    @classmethod
    def print_pipeline(cls):

        print("\nGriffin Tokenizer Pipeline v1.0\n")

        for stage in cls.STAGES:
            print(stage.name)

            if stage != cls.STAGES[-1]:
                print("   ↓")