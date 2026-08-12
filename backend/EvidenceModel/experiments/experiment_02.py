"""
Experiment 02: Griffin Core + RL Guided Search Agent
====================================================
Evaluates Griffin Core coupled with Reinforcement Learning search navigation space.
"""

from unittest.mock import MagicMock, patch
from backend.EvidenceModel.pipeline import GriffinCore
from backend.rl.environment import GriffinSearchEnv
from backend.rl.agent import ActorCritic
from backend.EvidenceModel.evaluation.benchmark_runner import BenchmarkRunner
from backend.EvidenceModel.evaluation.report_generator import EvaluationReportGenerator


def run_experiment_02():
    benchmark_file = "backend/EvidenceModel/benchmarks/benchmark.json"
    runner = BenchmarkRunner(benchmark_file)

    mock_heem = {
        "roots": [
            {
                "id": 1, "type": "UNIT", "text": "Unit 1: Relational Model",
                "children": [
                    {"id": 2, "type": "TOPIC", "text": "Normalization", "children": []}
                ]
            }
        ]
    }

    with patch(
        "backend.EvidenceModel.pipeline.CurriculumEvidenceExtractor"
    ) as mock_extractor_cls:

        mock_instance = MagicMock()
        mock_instance.parse_pdf.return_value = mock_heem
        mock_extractor_cls.return_value = mock_instance

        pipeline = GriffinCore()

        result = runner.run_benchmark(
            experiment_name="Exp_01_Standard_Griffin",
            griffin_pipeline=pipeline,
        )

    generator = EvaluationReportGenerator(result.report_data)
    print(generator.render_console_report())
    runner.save_results(result, "backend/EvidenceModel/experiments/results/exp_02_results.json")


if __name__ == "__main__":
    run_experiment_02()