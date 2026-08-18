import time
from typing import Any, Dict

from backend.EvidenceModel.pipeline import GriffinCore
from backend.EvidenceModel.presentation.builder import GriffinResultBuilder


class GriffinService:
    """Thin product wrapper around the frozen Griffin Core pipeline."""

    @staticmethod
    def process_report(
        report_file_path: str,
        curriculum_file_path: str,
        metadata: Dict[str, Any],
        on_stage_update=None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        def progress_callback(stage: str, percent: float):
            if on_stage_update:
                on_stage_update(stage, percent)

        griffin = GriffinCore()
        evidence_graph = griffin.process(
            curriculum_pdf_path=curriculum_file_path,
            report_input=report_file_path,
            on_stage_update=progress_callback,
        )

        processing_time = round(time.time() - start_time, 2)
        result_metadata = dict(metadata)
        result_metadata["processing_time"] = processing_time

        result = GriffinResultBuilder().build(
            evidence_graph=evidence_graph.model_dump() if hasattr(evidence_graph, "model_dump") else evidence_graph.dict(),
            metadata=result_metadata,
        )

        return result.model_dump() if hasattr(result, "model_dump") else result.dict()
