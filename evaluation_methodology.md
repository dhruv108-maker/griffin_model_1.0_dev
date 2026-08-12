# Evaluation Methodology

Automatically extracted from source code.

================================================================================

# File: __init__.py

No classes or functions found.


================================================================================

# File: benchmark_runner.py

# BenchmarkRunner

Executes evaluation benchmarks over datasets without introducing model logic.

## BenchmarkRunner.__init__

### Inputs
- benchmark_config_path: str

### Output Type
`Unknown`

### Returns
- None

### Methods Used
- `Evaluator()`
- `open()`
- `json.load()`

### Mathematical Procedure
```python
self.config_path = benchmark_config_path
self.evaluator = Evaluator()
self.config = json.load(f)
```

## BenchmarkRunner.run_benchmark

### Inputs
- experiment_name: str
- griffin_pipeline: GriffinCore

### Output Type
`EvaluationResult`

### Returns
- `eval_result`

### Methods Used
- `RuntimeTracker()`
- `tracker.start()`
- `tracker.start_stage()`
- `griffin_pipeline.process()`
- `tracker.stop_stage()`
- `tracker.stop()`
- `self.evaluator.evaluate()`
- `int()`
- `set()`
- `self.config['gold_retrieval'].items()`
- `retrieved_candidates.setdefault(t_id, []).append()`
- `edge.source.replace()`
- `retrieved_candidates.setdefault()`

### Mathematical Procedure
```python
tracker = RuntimeTracker()
curriculum_pdf = self.config['curriculum_pdf']
report_pages = self.config['report_pages']
graph = griffin_pipeline.process(curriculum_pdf_path=curriculum_pdf, report_input=report_pages)
runtime_res = tracker.stop()
val_gt = (self.config['gold_validator']['y_true'], self.config['gold_validator']['y_pred'], self.config['gold_validator']['y_prob'])
eval_result = self.evaluator.evaluate(experiment_name=experiment_name, graph=graph, all_topic_ids=all_topic_ids, retrieval_candidates=retrieved_candidates, retrieval_ground_truth=retrieval_gt, validator_ground_truth=val_gt, runtime_result=runtime_res)
return eval_result
t_id = int(edge.source.replace('topic_', ''))
```

## BenchmarkRunner.save_results

### Inputs
- eval_result: EvaluationResult
- output_path: str

### Output Type
`Unknown`

### Returns
- None

### Methods Used
- `os.makedirs()`
- `EvaluationReportGenerator()`
- `os.path.dirname()`
- `open()`
- `f.write()`
- `generator.to_json()`

### Mathematical Procedure
```python
generator = EvaluationReportGenerator(eval_result.report_data)
```



================================================================================

# File: evaluator.py

# EvaluationResult

# Evaluator

Central evaluator enforcing separation of concerns.
Consumes EvidenceGraph and ground truth data to produce evaluation results.

## Evaluator.evaluate

### Description
Coordinates all evaluation modules.

:param experiment_name: Name of evaluation run.
:param graph: Output EvidenceGraph from Griffin.
:param all_topic_ids: Full list of topic IDs present in curriculum.
:param retrieval_candidates: Map of topic_id -> list of retrieved paragraph_ids.
:param retrieval_ground_truth: Map of topic_id -> set of true relevant paragraph_ids.
:param validator_ground_truth: Optional Tuple (y_true, y_pred, y_prob) for validator set.
:param runtime_result: Optional recorded runtime metrics.

### Inputs
- experiment_name: str
- graph: EvidenceGraph
- all_topic_ids: List[int]
- retrieval_candidates: Dict[int, List[str]]
- retrieval_ground_truth: Dict[int, Set[str]]
- validator_ground_truth: Optional[Tuple[List[int], List[int], List[float]]]
- runtime_result: Optional[RuntimeMetricsResult]

### Output Type
`EvaluationResult`

### Returns
- `EvaluationResult(retrieval=retrieval_res, validator=validator_res, graph=graph_res, runtime=rt_res, report_data=report_data)`

### Methods Used
- `calculate_retrieval_metrics()`
- `calculate_graph_metrics()`
- `EvaluationReportData()`
- `EvaluationResult()`
- `calculate_validator_metrics()`
- `ValidatorMetricsResult()`
- `RuntimeMetricsResult()`

### Mathematical Procedure
```python
retrieval_res = calculate_retrieval_metrics(retrieved_map=retrieval_candidates, ground_truth_map=retrieval_ground_truth)
graph_res = calculate_graph_metrics(graph=graph, all_topic_ids=all_topic_ids, ground_truth_map=retrieval_ground_truth)
rt_res = runtime_result if runtime_result is not None else RuntimeMetricsResult()
report_data = EvaluationReportData(experiment_name=experiment_name, retrieval=retrieval_res, validator=validator_res, graph=graph_res, runtime=rt_res)
return EvaluationResult(retrieval=retrieval_res, validator=validator_res, graph=graph_res, runtime=rt_res, report_data=report_data)
(y_true, y_pred, y_prob) = validator_ground_truth
validator_res = calculate_validator_metrics(y_true, y_pred, y_prob)
validator_res = ValidatorMetricsResult()
```



================================================================================

# File: graph_metrics.py

# GraphMetricsResult

## calculate_graph_metrics

### Description
Calculates structural and topological validity metrics directly from EvidenceGraph.

### Inputs
- graph: EvidenceGraph
- all_topic_ids: List[int]
- ground_truth_map: Dict[int, Set[str]]

### Output Type
`GraphMetricsResult`

### Returns
- `GraphMetricsResult(curriculum_coverage=curriculum_coverage, evidence_density=evidence_density, duplicate_edge_rate=duplicate_edge_rate, hallucination_rate=hallucination_rate, average_confidence=avg_confidence)`
- `GraphMetricsResult()`

### Methods Used
- `set()`
- `GraphMetricsResult()`
- `evidence_to_para.get()`
- `mapped_topics.add()`
- `confidence_scores.append()`
- `len()`
- `int()`
- `unique_pairs.add()`
- `ground_truth_map.get()`
- `sum()`
- `edge.source.replace()`

### Mathematical Procedure
```python
topic_evidence_edges = [edge for edge in graph.edges if edge.relation == 'HAS_EVIDENCE']
evidence_para_edges = [edge for edge in graph.edges if edge.relation == 'EXTRACTED_FROM']
total_evidence_nodes = 0
total_accepted_edges = 0
hallucinations = 0
curriculum_coverage = len(mapped_topics) / len(all_topic_ids)
evidence_density = total_evidence_nodes / len(mapped_topics) if mapped_topics else 0.0
duplicates = total_accepted_edges - len(unique_pairs)
duplicate_edge_rate = duplicates / total_accepted_edges if total_accepted_edges > 0 else 0.0
hallucination_rate = hallucinations / total_accepted_edges if total_accepted_edges > 0 else 0.0
avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
return GraphMetricsResult(curriculum_coverage=curriculum_coverage, evidence_density=evidence_density, duplicate_edge_rate=duplicate_edge_rate, hallucination_rate=hallucination_rate, average_confidence=avg_confidence)
return GraphMetricsResult()
evidence_node_id = edge.target
para_id = evidence_to_para.get(evidence_node_id)
total_evidence_nodes += 1
total_accepted_edges += 1
topic_id = int(edge.source.replace('topic_', ''))
pair = (topic_id, para_id)
gt_paras = ground_truth_map.get(topic_id, set())
hallucinations += 1
```



================================================================================

# File: report_generator.py

# EvaluationReportData

# EvaluationReportGenerator

Generates structured evaluation reports and formatted CLI outputs.

## EvaluationReportGenerator.__init__

### Inputs
- data: EvaluationReportData

### Output Type
`Unknown`

### Returns
- None

### Methods Used
- None

### Mathematical Procedure
```python
self.data = data
```

## EvaluationReportGenerator.to_dict

### Inputs
- None

### Output Type
`Dict[str, Any]`

### Returns
- `asdict(self.data)`

### Methods Used
- `asdict()`

### Mathematical Procedure
```python
return asdict(self.data)
```

## EvaluationReportGenerator.to_json

### Inputs
- indent: int

### Output Type
`str`

### Returns
- `json.dumps(self.to_dict(), indent=indent)`

### Methods Used
- `json.dumps()`
- `self.to_dict()`

### Mathematical Procedure
```python
return json.dumps(self.to_dict(), indent=indent)
```

## EvaluationReportGenerator.render_console_report

### Inputs
- None

### Output Type
`str`

### Returns
- `report`

### Methods Used
- `', '.join()`
- `'\n'.join()`
- `d.retrieval.precision_at_k.get()`
- `d.retrieval.precision_at_k.items()`
- `d.retrieval.recall_at_k.items()`
- `d.retrieval.ndcg_at_k.items()`
- `d.runtime.stage_runtimes.items()`

### Mathematical Procedure
```python
d = self.data
line = '=' * 70
subline = '-' * 70
ret_p = ', '.join([f'P@{k}: {v:.4f}' for (k, v) in d.retrieval.precision_at_k.items()])
ret_r = ', '.join([f'R@{k}: {v:.4f}' for (k, v) in d.retrieval.recall_at_k.items()])
ret_ndcg = ', '.join([f'nDCG@{k}: {v:.4f}' for (k, v) in d.retrieval.ndcg_at_k.items()])
auc_str = f'{d.validator.roc_auc:.4f}' if d.validator.roc_auc is not None else 'N/A'
gpu_str = f'{d.runtime.gpu_memory_mb:.2f} MB' if d.runtime.gpu_memory_mb is not None else 'N/A'
stages_str = '\n'.join([f'    - {k}: {v:.4f}s' for (k, v) in d.runtime.stage_runtimes.items()])
report = f'\n{line}\nGRIFFIN CORE RESEARCH EVALUATION REPORT\nExperiment: {d.experiment_name}\n{line}\n\n1. RETRIEVAL METRICS\n{subline}\n  * Precision : {ret_p}\n  * Recall    : {ret_r}\n  * nDCG      : {ret_ndcg}\n  * MRR       : {d.retrieval.mrr:.4f}\n\n2. VALIDATOR METRICS (Cross-Encoder Entailment)\n{subline}\n  * Accuracy  : {d.validator.accuracy:.4f}\n  * Precision : {d.validator.precision:.4f}\n  * Recall    : {d.validator.recall:.4f}\n  * F1-Score  : {d.validator.f1_score:.4f}\n  * ROC AUC   : {auc_str}\n\n3. GRAPH & TOPOLOGY METRICS\n{subline}\n  * Curriculum Coverage  : {d.graph.curriculum_coverage * 100:.2f}%\n  * Evidence Density     : {d.graph.evidence_density:.2f} nodes/topic\n  * Duplicate Edge Rate  : {d.graph.duplicate_edge_rate * 100:.2f}%\n  * Hallucination Rate   : {d.graph.hallucination_rate * 100:.2f}%\n  * Average Confidence   : {d.graph.average_confidence:.4f}\n\n4. RUNTIME & SYSTEM PERFORMANCE\n{subline}\n  * Total Runtime  : {d.runtime.total_runtime_seconds:.4f} seconds\n  * Peak CPU RAM   : {d.runtime.peak_memory_mb:.2f} MB\n  * GPU VRAM       : {gpu_str}\n  * Stage Breakdown:\n{stages_str}\n\n{line}\nOVERALL SUMMARY: Coverage={d.graph.curriculum_coverage * 100:.1f}% | Precision@1={d.retrieval.precision_at_k.get(1, 0.0):.4f} | F1={d.validator.f1_score:.4f}\n{line}\n'
return report
```



================================================================================

# File: retrieval_metrics.py

# RetrievalMetricsResult

## precision_at_k

### Description
Calculates Precision@K: Ratio of relevant retrieved items in top-K.

### Inputs
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

### Output Type
`float`

### Returns
- `relevant_retrieved / k`
- `0.0`

### Methods Used
- `sum()`

### Mathematical Procedure
```python
top_k = retrieved[:k]
relevant_retrieved = sum((1 for item in top_k if item in ground_truth))
return relevant_retrieved / k
return 0.0
return 0.0
```

## recall_at_k

### Description
Calculates Recall@K: Ratio of relevant items found in top-K out of all ground truth.

### Inputs
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

### Output Type
`float`

### Returns
- `relevant_retrieved / len(ground_truth)`
- `0.0`

### Methods Used
- `sum()`
- `len()`

### Mathematical Procedure
```python
top_k = retrieved[:k]
relevant_retrieved = sum((1 for item in top_k if item in ground_truth))
return relevant_retrieved / len(ground_truth)
return 0.0
```

## mean_reciprocal_rank

### Description
Calculates Mean Reciprocal Rank (MRR) across all queries.

### Inputs
- all_retrieved: List[List[str]]
- all_ground_truth: List[Set[str]]

### Output Type
`float`

### Returns
- `sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0`
- `0.0`

### Methods Used
- `zip()`
- `enumerate()`
- `reciprocal_ranks.append()`
- `len()`
- `sum()`

### Mathematical Procedure
```python
reciprocal_ranks = []
return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
return 0.0
rank_found = 0.0
rank_found = 1.0 / idx
```

## ndcg_at_k

### Description
Calculates Normalized Discounted Cumulative Gain (nDCG@K) for binary relevance.

### Inputs
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

### Output Type
`float`

### Returns
- `dcg / idcg`
- `0.0`

### Methods Used
- `enumerate()`
- `min()`
- `range()`
- `len()`
- `math.log2()`

### Mathematical Procedure
```python
top_k = retrieved[:k]
dcg = 0.0
idcg = 0.0
ideal_hits = min(k, len(ground_truth))
return dcg / idcg
return 0.0
rel = 1.0 if item in ground_truth else 0.0
dcg += rel / math.log2(idx + 1)
idcg += 1.0 / math.log2(idx + 1)
return 0.0
```

## calculate_retrieval_metrics

### Description
Computes aggregated Precision@K, Recall@K, MRR, and nDCG@K over all topics.

### Inputs
- retrieved_map: Dict[int, List[str]]
- ground_truth_map: Dict[int, Set[str]]
- k_list: List[int]

### Output Type
`RetrievalMetricsResult`

### Returns
- `RetrievalMetricsResult(precision_at_k=mean_p, recall_at_k=mean_r, mrr=mrr_score, ndcg_at_k=mean_ndcg)`

### Methods Used
- `retrieved_map.items()`
- `mean_reciprocal_rank()`
- `RetrievalMetricsResult()`
- `ground_truth_map.get()`
- `all_retrieved.append()`
- `all_gt.append()`
- `set()`
- `p_at_k_accum[k].append()`
- `r_at_k_accum[k].append()`
- `ndcg_at_k_accum[k].append()`
- `float()`
- `p_at_k_accum.items()`
- `r_at_k_accum.items()`
- `ndcg_at_k_accum.items()`
- `precision_at_k()`
- `recall_at_k()`
- `ndcg_at_k()`
- `sum()`
- `len()`

### Mathematical Procedure
```python
all_retrieved = []
all_gt = []
mrr_score = mean_reciprocal_rank(all_retrieved, all_gt)
mean_p = {k: float(sum(vals) / len(vals)) if vals else 0.0 for (k, vals) in p_at_k_accum.items()}
mean_r = {k: float(sum(vals) / len(vals)) if vals else 0.0 for (k, vals) in r_at_k_accum.items()}
mean_ndcg = {k: float(sum(vals) / len(vals)) if vals else 0.0 for (k, vals) in ndcg_at_k_accum.items()}
return RetrievalMetricsResult(precision_at_k=mean_p, recall_at_k=mean_r, mrr=mrr_score, ndcg_at_k=mean_ndcg)
gt_set = ground_truth_map.get(topic_id, set())
```



================================================================================

# File: runtime_metrics.py

# RuntimeMetricsResult

Stores runtime and resource usage statistics.

# RuntimeTracker

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

## RuntimeTracker.__init__

### Inputs
- None

### Output Type
`None`

### Returns
- None

### Methods Used
- None

### Mathematical Procedure
No explicit mathematical statements.

## RuntimeTracker.start

### Description
Start runtime and memory tracking.

### Inputs
- None

### Output Type
`None`

### Returns
- None

### Methods Used
- `self.stage_runtimes.clear()`
- `tracemalloc.start()`
- `time.perf_counter()`
- `torch.cuda.is_available()`
- `torch.cuda.reset_peak_memory_stats()`

### Mathematical Procedure
```python
self.start_time = time.perf_counter()
self._running = True
```

## RuntimeTracker.start_stage

### Description
Start timing a pipeline stage.

### Inputs
- stage_name: str

### Output Type
`None`

### Returns
- None

### Methods Used
- `time.perf_counter()`
- `RuntimeError()`

### Mathematical Procedure
```python
self._stage_start = time.perf_counter()
```

## RuntimeTracker.stop_stage

### Description
Stop timing the current stage.

### Inputs
- stage_name: str

### Output Type
`None`

### Returns
- None

### Methods Used
- `RuntimeError()`
- `time.perf_counter()`
- `self.stage_runtimes.get()`

### Mathematical Procedure
```python
duration = time.perf_counter() - self._stage_start
self.stage_runtimes[stage_name] = self.stage_runtimes.get(stage_name, 0.0) + duration
self._stage_start = None
```

## RuntimeTracker.stop

### Description
Finish profiling and return collected metrics.

### Inputs
- None

### Output Type
`RuntimeMetricsResult`

### Returns
- `RuntimeMetricsResult(total_runtime_seconds=total_runtime, stage_runtimes=dict(self.stage_runtimes), peak_memory_mb=peak / (1024 * 1024), gpu_memory_mb=gpu_memory)`

### Methods Used
- `tracemalloc.get_traced_memory()`
- `tracemalloc.stop()`
- `RuntimeMetricsResult()`
- `RuntimeError()`
- `time.perf_counter()`
- `torch.cuda.is_available()`
- `dict()`
- `torch.cuda.max_memory_allocated()`

### Mathematical Procedure
```python
total_runtime = time.perf_counter() - self.start_time
(current, peak) = tracemalloc.get_traced_memory()
gpu_memory = None
self._running = False
return RuntimeMetricsResult(total_runtime_seconds=total_runtime, stage_runtimes=dict(self.stage_runtimes), peak_memory_mb=peak / (1024 * 1024), gpu_memory_mb=gpu_memory)
gpu_memory = torch.cuda.max_memory_allocated() / (1024 * 1024)
gpu_memory = None
```



================================================================================

# File: validator_metrics.py

# ValidatorMetricsResult

## calculate_validator_metrics

### Description
Computes classification performance metrics for the EvidenceValidator cross-encoder.

### Inputs
- y_true: List[int]
- y_pred: List[int]
- y_prob: Optional[List[float]]

### Output Type
`ValidatorMetricsResult`

### Returns
- `ValidatorMetricsResult(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1, roc_auc=auc)`
- `ValidatorMetricsResult()`

### Methods Used
- `len()`
- `sum()`
- `ValidatorMetricsResult()`
- `_compute_roc_auc()`
- `zip()`
- `set()`

### Mathematical Procedure
```python
total = len(y_true)
tp = sum((1 for (gt, pred) in zip(y_true, y_pred) if gt == 1 and pred == 1))
tn = sum((1 for (gt, pred) in zip(y_true, y_pred) if gt == 0 and pred == 0))
fp = sum((1 for (gt, pred) in zip(y_true, y_pred) if gt == 0 and pred == 1))
fn = sum((1 for (gt, pred) in zip(y_true, y_pred) if gt == 1 and pred == 0))
accuracy = (tp + tn) / total if total > 0 else 0.0
precision = tp / (tp + fp) if tp + fp > 0 else 0.0
recall = tp / (tp + fn) if tp + fn > 0 else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
auc = None
return ValidatorMetricsResult(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1, roc_auc=auc)
return ValidatorMetricsResult()
auc = _compute_roc_auc(y_true, y_prob)
```

## _compute_roc_auc

### Description
Computes Area Under ROC Curve via Mann-Whitney U test formula.

### Inputs
- y_true: List[int]
- y_prob: List[float]

### Output Type
`float`

### Returns
- `float(u_stat / (n_pos * n_neg))`
- `0.0`

### Methods Used
- `len()`
- `sorted()`
- `sum()`
- `float()`
- `enumerate()`
- `range()`

### Mathematical Procedure
```python
pos_indices = [i for (i, label) in enumerate(y_true) if label == 1]
neg_indices = [i for (i, label) in enumerate(y_true) if label == 0]
n_pos = len(pos_indices)
n_neg = len(neg_indices)
combined = sorted(enumerate(y_prob), key=lambda x: x[1])
ranks = [0.0] * len(y_prob)
i = 0
pos_rank_sum = sum((ranks[idx] for idx in pos_indices))
u_stat = pos_rank_sum - n_pos * (n_pos + 1) / 2.0
return float(u_stat / (n_pos * n_neg))
return 0.0
j = i
rank_val = (i + 1 + j) / 2.0
i = j
j += 1
ranks[combined[k][0]] = rank_val
```


