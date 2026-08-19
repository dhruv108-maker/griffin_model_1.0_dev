import threading
import time
from typing import Any, Dict

from backend.EvidenceModel.pipeline import GriffinCore
from backend.EvidenceModel.presentation.builder import GriffinResultBuilder


class GriffinService:
    """Thin product wrapper around the frozen Griffin Core pipeline."""

    _core: GriffinCore | None = None
    _core_lock = threading.Lock()
    _process_lock = threading.Lock()

    @classmethod
    def _get_core(cls) -> GriffinCore:
        """Create Griffin Core once per worker and reuse its loaded models."""
        if cls._core is None:
            with cls._core_lock:
                if cls._core is None:
                    cls._core = GriffinCore()
        return cls._core

    @classmethod
    def warm_up(cls) -> None:
        """Load Griffin's model stack before the first user evaluation."""
        cls._get_core()

    @classmethod
    def process_report(
        cls,
        report_file_path: str,
        curriculum_file_path: str,
        metadata: Dict[str, Any],
        on_stage_update=None,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        def progress_callback(stage: str, percent: float):
            if on_stage_update:
                on_stage_update(stage, percent)

        # GriffinCore owns model/evaluation state. Keep one warm instance per
        # worker and serialize access to avoid concurrent inference contention.
        with cls._process_lock:
            griffin = cls._get_core()
            evidence_graph = griffin.process(
                curriculum_pdf_path=curriculum_file_path,
                report_input=report_file_path,
                on_stage_update=progress_callback,
            )

        processing_time = round(time.perf_counter() - start_time, 2)
        result_metadata = dict(metadata)
        result_metadata["processing_time"] = processing_time

        result = GriffinResultBuilder().build(
            evidence_graph=(
                evidence_graph.model_dump()
                if hasattr(evidence_graph, "model_dump")
                else evidence_graph.dict()
            ),
            metadata=result_metadata,
        )

        return result.model_dump() if hasattr(result, "model_dump") else result.dict()
