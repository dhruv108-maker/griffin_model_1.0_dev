"""
Experiment 01: Standard Griffin Core Benchmark
==============================================

Evaluates the complete Griffin Core pipeline without reinforcement learning.

Pipeline
--------
Curriculum PDF
        ↓
CurriculumEvidenceExtractor
        ↓
HEEM Curriculum Tree
        ↓
Topic Encoder

+

Academic Report
        ↓
Document Parser
        ↓
Report Encoder

↓

Evidence Retrieval

↓

Evidence Validation

↓

Evidence Graph

↓

Research Evaluation

Outputs
-------
- Console evaluation report
- JSON experiment results
"""

from __future__ import annotations

from pathlib import Path

from backend.EvidenceModel.pipeline import GriffinCore
from backend.EvidenceModel.evaluation.benchmark_runner import BenchmarkRunner
from backend.EvidenceModel.evaluation.report_generator import (
    EvaluationReportGenerator,
)


EXPERIMENT_NAME = "Exp_01_Standard_Griffin"

PROJECT_ROOT = Path("backend") / "EvidenceModel"

BENCHMARK_FILE = PROJECT_ROOT / "benchmarks" / "benchmark.json"

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RESULT_FILE = RESULTS_DIR / "exp_01_results.json"


def run_experiment() -> None:
    """
    Execute Experiment 01.

    This experiment evaluates the complete Griffin Core pipeline using
    the benchmark dataset defined in benchmark.json.

    No pipeline components are mocked.
    """

    print("=" * 70)
    print("GRIFFIN CORE RESEARCH BENCHMARK")
    print(EXPERIMENT_NAME)
    print("=" * 70)

    # Initialize Griffin
    griffin = GriffinCore()

    # Load benchmark
    benchmark_runner = BenchmarkRunner(str(BENCHMARK_FILE))

    # Execute benchmark
    result = benchmark_runner.run_benchmark(
        experiment_name=EXPERIMENT_NAME,
        griffin_pipeline=griffin,
    )

    # Generate report
    report = EvaluationReportGenerator(result.report_data)

    print()
    print(report.render_console_report())

    # Save JSON results
    benchmark_runner.save_results(
        result,
        str(RESULT_FILE)
    )

    print()
    print(f"Results saved to: {RESULT_FILE}")


def main() -> None:
    """Experiment entry point."""

    run_experiment()


if __name__ == "__main__":
    main()