import os
import queue
import threading
import time
from typing import Any, Dict

from backend.EvidenceModel.pipeline import GriffinCore
from backend.EvidenceModel.presentation.builder import GriffinResultBuilder


class GriffinService:
    """Product wrapper around the Griffin Core pipeline with reusable model instances."""

    _pool: queue.Queue[GriffinCore] | None = None
    _pool_lock = threading.Lock()
    _pool_size: int | None = None

    @classmethod
    def _configured_pool_size(cls) -> int:
        configured = os.getenv("GRIFFIN_MAX_CONCURRENT_REPORTS", "2")
        try:
            return max(1, int(configured))
        except ValueError:
            return 2

    @classmethod
    def _ensure_pool(cls, size: int | None = None) -> queue.Queue[GriffinCore]:
        target_size = size or cls._configured_pool_size()
        if cls._pool is not None and cls._pool_size == target_size:
            return cls._pool

        with cls._pool_lock:
            if cls._pool is not None and cls._pool_size == target_size:
                return cls._pool

            pool: queue.Queue[GriffinCore] = queue.Queue(maxsize=target_size)
            for _ in range(target_size):
                pool.put(GriffinCore())
            cls._pool = pool
            cls._pool_size = target_size
            return pool

    @classmethod
    def warm_up(cls) -> None:
        cls._ensure_pool()

    @classmethod
    def process_report(
        cls,
        report_file_path: str,
        curriculum_file_path: str,
        curriculum_schema: Dict[str, Any] | None,
        metadata: Dict[str, Any],
        on_stage_update=None,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        pool = cls._ensure_pool()
        griffin = pool.get()

        try:
            def progress_callback(stage: str, percent: float):
                if on_stage_update:
                    on_stage_update(stage, percent)

            evidence_graph = griffin.process(
                curriculum_pdf_path=curriculum_file_path,
                report_input=report_file_path,
                on_stage_update=progress_callback,
                curriculum_schema=curriculum_schema,
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
        finally:
            pool.put(griffin)
