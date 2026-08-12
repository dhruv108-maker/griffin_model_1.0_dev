from __future__ import annotations
import json
import os
from typing import Dict, List, Set, Any
from backend.EvidenceModel.pipeline import GriffinCore
from backend.EvidenceModel.evaluation.evaluator import Evaluator, EvaluationResult
from backend.EvidenceModel.evaluation.report_generator import EvaluationReportGenerator
from backend.EvidenceModel.evaluation.runtime_metrics import RuntimeTracker


class BenchmarkRunner:
    """
    Executes evaluation benchmarks over datasets without introducing model logic.
    """

    def __init__(self, benchmark_config_path: str):
        self.config_path = benchmark_config_path
        with open(benchmark_config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.evaluator = Evaluator()

    def run_benchmark(self, experiment_name: str, griffin_pipeline: GriffinCore) -> EvaluationResult:
        tracker = RuntimeTracker()
        tracker.start()

        curriculum_pdf = self.config["curriculum_pdf"]
        report_pages = self.config["report_pages"]

        # Track pipeline execution
        tracker.start_stage("GriffinCore.process")
        graph = griffin_pipeline.process(
            curriculum_pdf_path=curriculum_pdf,
            report_input=report_pages
        )
        tracker.stop_stage("GriffinCore.process")

        runtime_res = tracker.stop()

        # Convert benchmark gold labels
        retrieval_gt: Dict[int, Set[str]] = {
            int(k): set(v) for k, v in self.config["gold_retrieval"].items()
        }
        all_topic_ids: List[int] = self.config["all_topic_ids"]

        # Extract candidates directly from retrieval stage
        retrieved_candidates: Dict[int, List[str]] = {}
        for edge in graph.edges:
            if edge.relation == "HAS_EVIDENCE":
                try:
                    t_id = int(edge.source.replace("topic_", ""))
                except ValueError:
                    continue
                retrieved_candidates.setdefault(t_id, []).append(edge.target)

        # Validator evaluation ground truth
        val_gt = (
            self.config["gold_validator"]["y_true"],
            self.config["gold_validator"]["y_pred"],
            self.config["gold_validator"]["y_prob"]
        )

        eval_result = self.evaluator.evaluate(
            experiment_name=experiment_name,
            graph=graph,
            all_topic_ids=all_topic_ids,
            retrieval_candidates=retrieved_candidates,
            retrieval_ground_truth=retrieval_gt,
            validator_ground_truth=val_gt,
            runtime_result=runtime_res
        )

        return eval_result

    def save_results(self, eval_result: EvaluationResult, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        generator = EvaluationReportGenerator(eval_result.report_data)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generator.to_json())