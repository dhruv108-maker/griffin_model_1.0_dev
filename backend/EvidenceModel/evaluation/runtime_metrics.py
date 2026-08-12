from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(slots=True)
class RuntimeMetricsResult:
    """Stores runtime and resource usage statistics."""

    total_runtime_seconds: float = 0.0
    stage_runtimes: Dict[str, float] = field(default_factory=dict)
    peak_memory_mb: float = 0.0
    gpu_memory_mb: Optional[float] = None


class RuntimeTracker:
    """
    Tracks execution time, stage-wise runtime, memory usage,
    and optional GPU memory consumption.

    Example:
        tracker = RuntimeTracker()

        tracker.start()

        tracker.start_stage("Encoding")
        ...
        tracker.stop_stage("Encoding")

        tracker.start_stage("Retrieval")
        ...
        tracker.stop_stage("Retrieval")

        metrics = tracker.stop()
    """

    def __init__(self) -> None:
        self.stage_runtimes: Dict[str, float] = {}
        self.start_time: float = 0.0
        self._stage_start: Optional[float] = None
        self._running: bool = False

    def start(self) -> None:
        """Start runtime and memory tracking."""

        self.stage_runtimes.clear()

        tracemalloc.start()

        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.reset_peak_memory_stats()
        except Exception:
            pass

        self.start_time = time.perf_counter()
        self._running = True

    def start_stage(self, stage_name: str) -> None:
        """Start timing a pipeline stage."""

        if not self._running:
            raise RuntimeError("RuntimeTracker.start() must be called first.")

        self._stage_start = time.perf_counter()

    def stop_stage(self, stage_name: str) -> None:
        """Stop timing the current stage."""

        if self._stage_start is None:
            raise RuntimeError(f"Stage '{stage_name}' was never started.")

        duration = time.perf_counter() - self._stage_start

        self.stage_runtimes[stage_name] = (
            self.stage_runtimes.get(stage_name, 0.0) + duration
        )

        self._stage_start = None

    def stop(self) -> RuntimeMetricsResult:
        """Finish profiling and return collected metrics."""

        if not self._running:
            raise RuntimeError("RuntimeTracker.start() must be called first.")

        total_runtime = time.perf_counter() - self.start_time

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        gpu_memory = None

        try:
            import torch

            if torch.cuda.is_available():
                gpu_memory = (
                    torch.cuda.max_memory_allocated() / (1024 * 1024)
                )
        except Exception:
            gpu_memory = None

        self._running = False

        return RuntimeMetricsResult(
            total_runtime_seconds=total_runtime,
            stage_runtimes=dict(self.stage_runtimes),
            peak_memory_mb=peak / (1024 * 1024),
            gpu_memory_mb=gpu_memory,
        )