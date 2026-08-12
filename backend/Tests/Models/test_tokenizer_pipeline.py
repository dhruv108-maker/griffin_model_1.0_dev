"""
Griffin Report Tokenizer Pipeline Test

Pipeline
--------
PDF / DOCX
      │
      ▼
Document Parser
      │
      ▼
Layout & Structure Analysis
      │
      ▼
Metadata Extraction
      │
      ▼
Labeled Input Tokens
      │
      ▼
Griffin Evidence Tokens

Purpose
-------
Validate Griffin's document intelligence pipeline by transforming
academic reports into structured input tokens and optimized evidence
tokens for downstream curriculum assessment.
"""

import json
import sys
from collections import Counter
from pathlib import Path

# =============================================================================
# Project Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.EvidenceModel.report_tokenizer import GriffinReportTokenizer


# =============================================================================
# Test Configuration
# =============================================================================

PDF_PATH = (
    PROJECT_ROOT
    / "backend"
    / "Tests"
    / "Database"
    / "Samples"
    / "MajorProjectReport@2026.pdf"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "Tests"
    / "Database"
    / "Results"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Utilities
# =============================================================================

def serialize(obj):
    """Convert Pydantic models or dataclasses into dictionaries."""

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "dict"):
        return obj.dict()

    return obj


def save_json(path: Path, data: dict):
    """Save tokenizer output."""

    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)


# =============================================================================
# Summary
# =============================================================================

def summarize_metadata(metadata):

    if metadata is None:
        return

    print("\nDocument")

    print(f"  Title  : {metadata.title or '-'}")
    print(f"  Author : {metadata.author or '-'}")
    print(f"  Pages  : {metadata.total_pages}")


def summarize_input_tokens(tokens):

    print("\nLabeled Input Tokens")
    print("--------------------")
    print(f"Total : {len(tokens)}")

    labels = Counter(
        getattr(token, "label", "UNKNOWN")
        for token in tokens
    )

    for label in sorted(labels):
        print(f"{label:<18}{labels[label]}")


def summarize_evidence_tokens(tokens):

    print("\nGriffin Evidence Tokens")
    print("-----------------------")
    print(f"Total : {len(tokens)}")

    if not tokens:
        return

    avg_semantic = sum(
        getattr(t, "semantic_density", 0)
        for t in tokens
    ) / len(tokens)

    avg_information = sum(
        getattr(t, "information_gain", 0)
        for t in tokens
    ) / len(tokens)

    avg_technical = sum(
        getattr(t, "technical_density", 0)
        for t in tokens
    ) / len(tokens)

    print(f"Semantic Density : {avg_semantic:.3f}")
    print(f"Technical Density: {avg_technical:.3f}")
    print(f"Information Gain : {avg_information:.3f}")


def print_summary(result):

    print("\n=================================================")
    print("         GRIFFIN TOKENIZATION SUMMARY")
    print("=================================================")

    summarize_metadata(getattr(result, "metadata", None))
    summarize_input_tokens(getattr(result, "input_tokens", []))
    summarize_evidence_tokens(getattr(result, "tokens", []))

    print("\nPipeline")

    print("  PDF")
    print("    ↓")
    print("  Layout & Structure")
    print("    ↓")
    print("  Metadata")
    print("    ↓")
    print("  Input Tokens")
    print("    ↓")
    print("  Griffin Evidence Tokens")


# =============================================================================
# Main
# =============================================================================

def main():

    if not PDF_PATH.exists():
        print(f"PDF not found:\n{PDF_PATH}")
        return

    print("=" * 60)
    print("Griffin Report Tokenizer")
    print("=" * 60)

    print(f"\nInput : {PDF_PATH.name}")

    tokenizer = GriffinReportTokenizer()

    result = tokenizer.tokenize(PDF_PATH)

    output_file = OUTPUT_DIR / f"{PDF_PATH.stem}_griffin_tokens.json"

    save_json(output_file, serialize(result))

    print_summary(result)

    print(f"\nOutput : {output_file}")

    print("\n✓ Pipeline completed successfully.")


if __name__ == "__main__":
    main()