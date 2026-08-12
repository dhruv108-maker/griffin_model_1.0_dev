import json
import re
from typing import Dict, List, Any, Optional, Tuple
import pypdf
from backend.EvidenceModel.Transformers import EvidenceTransformer
from backend.EvidenceModel.EvidenceExtractor import CurriculumEvidenceExtractor

# Execution Entrypoint
if __name__ == "__main__":
    extractor = CurriculumEvidenceExtractor()
    structured_output = extractor.parse_pdf(r"backend\Tests\Database\Samples\curr_test.pdf")

    # Output directly to final JSON format
    output_filepath = r"backend\Tests\Database\Results\curriculum_evidence_final.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=4, ensure_ascii=False)

    print(f"Extraction successful! Clean evidence tree dumped to {output_filepath}")