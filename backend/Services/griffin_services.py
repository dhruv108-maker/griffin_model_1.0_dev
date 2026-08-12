import time
from typing import Dict, Any
from backend.EvidenceModel.pipeline import GriffinCore 
from backend.EvidenceModel.presentation.builder import GriffinResultBuilder

class GriffinService:
    """Interface to the unaltered Griffin Core Pipeline."""

    @staticmethod
    def process_report(report_file_path: str, curriculum_file_path: str, metadata: Dict[str, Any], on_stage_update = None) -> Dict[str, Any]:
        """
        Calls GriffinCore.process and builds the GriffinResult presentation layer.
        """
        start_time = time.time()
        
        griffin = GriffinCore()
        evidence_graph = griffin.process(
            curriculum_pdf_path=curriculum_file_path,
            report_input=report_file_path,
            on_stage_update=on_stage_update
        )
        
        processing_time = round(time.time() - start_time, 2)
        metadata["processing_time"] = processing_time
        
        result = GriffinResultBuilder().build(
            evidence_graph=evidence_graph.model_dump() if hasattr(evidence_graph, "model_dump") else evidence_graph.dict(), 
            metadata=metadata
        )
        
        return result.model_dump() if hasattr(result, "model_dump") else result.dict()

