"""
presentation/exporter.py
Exports the presentation model into griffin_result.json.
"""

import json
from .builder import GriffinResultBuilder


def export_griffin_result(
    evidence_graph: dict,
    metadata: dict,
    output_path: str = r"backend\Results\Evaluation\griffin_result.json"
) -> str:
    """
    Consumes EvidenceGraph, transforms it into GriffinResult, and writes to griffin_result.json.
    """
    builder = GriffinResultBuilder(confidence_threshold=0.50)
    result_model = builder.build(evidence_graph, metadata)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_model.model_dump_json(indent=2))

    return output_path