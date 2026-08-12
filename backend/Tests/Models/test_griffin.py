"""
Griffin Core Pipeline Test

Pipeline
--------
Curriculum PDF
        │
        ▼
Curriculum Parser
        │
        ▼
HEEM Tree
        │
        ▼
Topic Encoder

                     Report PDF
                         │
                         ▼
                Griffin Report Tokenizer
                         │
                         ▼
               Griffin Evidence Tokens

              Curriculum + Evidence
                     │
                     ▼
             Evidence Retrieval
                     │
                     ▼
             Evidence Validation
                     │
                     ▼
              Evidence Graph
                     │
                     ▼
                Griffin Output

Purpose
-------
Validate the complete Griffin Core pipeline using real curriculum
and report PDFs.
"""

import json
from pathlib import Path

from backend.EvidenceModel.pipeline import GriffinCore


# ==========================================================
# Configuration
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CURRICULUM_PDF = (
    PROJECT_ROOT
    / "backend"
    / "Tests"
    / "Database"
    / "Samples"
    / "curr_test.pdf"
)

REPORT_PDF = (
    PROJECT_ROOT
    / "backend"
    / "Tests"
    / "Database"
    / "Samples"
    / "MajorProjectReport@2026.pdf"
)

RESULT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "Tests"
    / "Results"
)

RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Utilities
# ==========================================================

def serialize(obj):

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "dict"):
        return obj.dict()

    return obj


# ==========================================================
# Main
# ==========================================================

def test_griffin_core():

    print("=" * 60)
    print("Griffin Core Pipeline")
    print("=" * 60)

    print(f"\nCurriculum : {CURRICULUM_PDF.name}")
    print(f"Report     : {REPORT_PDF.name}")

    core = GriffinCore()

    result = core.process(
        curriculum_pdf_path=str(CURRICULUM_PDF),
        report_input=str(REPORT_PDF),
    )

    output_file = RESULT_DIR / "griffin_core_result.json"

    with open(output_file, "w", encoding="utf-8") as fp:
        json.dump(
            serialize(result),
            fp,
            indent=2,
            ensure_ascii=False,
        )

    print("\nPipeline")
    print("--------")
    print("Curriculum PDF")
    print("      ↓")
    print("Curriculum Parser")
    print("      ↓")
    print("HEEM Tree")
    print("      ↓")
    print("Topic Encoder")
    print("      │")
    print("      ├──────────────┐")
    print("      │              │")
    print("      │         Report PDF")
    print("      │              ↓")
    print("      │     Griffin Report Tokenizer")
    print("      │              ↓")
    print("      │     Griffin Evidence Tokens")
    print("      └──────────────┘")
    print("             ↓")
    print("     Evidence Retrieval")
    print("             ↓")
    print("     Evidence Validation")
    print("             ↓")
    print("      Evidence Graph")
    print("             ↓")
    print("      Griffin Output")

    print("\nOutput")
    print(f"------")
    print(output_file)

    print("\n✓ Griffin Core pipeline completed successfully.")

    assert result is not None

if __name__ == "__main__":
    test_griffin_core()