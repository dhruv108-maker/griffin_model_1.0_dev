# Backend API Map

## __init__.py

*No classes or methods.*

## config.py

*No classes or methods.*

## mian.py

*No classes or methods.*

## compute/cpu.py

#### submit

Input
- task: Any

Output Type : `Unknown`

Output
- future.result -> `future.result()`


## compute/device.py

### Schema/Class `Device`

Fields
- CPU
- GPU
- AUTO


## compute/executor.py

### Class `ComputeExecutor`

#### ComputeExecutor.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### ComputeExecutor.execute

Input
- self: Any
- task: ComputeTask

Output Type : `Unknown`

Output
- self.scheduler.run -> `self.scheduler.run(task)`


## compute/gpu.py

#### submit

Input
- task: Any

Output Type : `Unknown`

Output
- task.fn -> `task.fn(*task.args, **task.kwargs)`


## compute/runner.py

*No classes or methods.*

## compute/scheduler.py

### Class `Scheduler`

#### Scheduler.run

Input
- self: Any
- task: Any

Output Type : `Unknown`

Output
- cpu.submit -> `cpu.submit(task)`
- gpu.submit -> `gpu.submit(task)`


## compute/task.py

### Schema/Class `ComputeTask`

Fields
- name: str
- fn: Callable
- args: tuple
- kwargs: dict
- device: str

#### ComputeTask.__post_init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Database/database.py

*No classes or methods.*

## Database/models.py

#### generate_uuid

Input
- None

Output Type : `Unknown`

Output
- str -> `str(uuid.uuid4())`

### Schema/Class `TimestampMixin`

Fields
- created_at
- updated_at

### Schema/Class `JobStatus`

Fields
- PENDING
- PROCESSING
- COMPLETED
- FAILED

### Schema/Class `Workspace`

Fields
- __tablename__
- id
- name
- description
- owner_id
- projects

### Schema/Class `Project`

Fields
- __tablename__
- id
- workspace_id
- name
- description
- workspace
- curriculums
- reports
- evaluations
- chats

### Schema/Class `Curriculum`

Fields
- __tablename__
- id
- project_id
- title
- file_path
- parsed_schema
- project
- evaluations

### Schema/Class `Report`

Fields
- __tablename__
- id
- project_id
- title
- student_name
- file_path
- total_pages
- project
- generated_reports

### Schema/Class `Evaluation`

Fields
- __tablename__
- id
- project_id
- curriculum_id
- name
- status
- project
- curriculum
- batch_jobs
- generated_reports

### Schema/Class `BatchJob`

Fields
- __tablename__
- id
- evaluation_id
- status
- progress_percentage
- error_message
- started_at
- completed_at
- evaluation

### Schema/Class `GeneratedReport`

Fields
- __tablename__
- id
- evaluation_id
- report_id
- griffin_result
- evaluation
- report

### Schema/Class `Chat`

Fields
- __tablename__
- id
- project_id
- evaluation_id
- title
- project
- messages

### Schema/Class `Message`

Fields
- __tablename__
- id
- chat_id
- sender
- content
- chat


## Dependencies/database_dep.py

#### get_db

Input
- None

Output Type : `Generator[Session, None, None]`

Output
- yield -> `db`


## EvidenceModel/EvidenceExtractor.py

### Class `CurriculumEvidenceExtractor`

#### CurriculumEvidenceExtractor.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### CurriculumEvidenceExtractor._next_id

Input
- self: Any

Output Type : `int`

Output
- current_id -> `current_id`

#### CurriculumEvidenceExtractor._create_node

Input
- self: Any
- node_type: str
- text: str
- page: int
- confidence: float
- attributes: Optional[Dict[str, Any]]

Output Type : `Dict[str, Any]`

Output
- node -> `node`

#### CurriculumEvidenceExtractor._clean_layout_artifacts

Input
- self: Any
- text: str

Output Type : `str`

Output
- text -> `text`

#### CurriculumEvidenceExtractor._is_noise

Input
- self: Any
- line: str

Output Type : `bool`

Output
- expression -> `False`
- expression -> `True`

#### CurriculumEvidenceExtractor._parse_attributes_and_cos

Input
- self: Any
- raw_text: str

Output Type : `Tuple[str, Dict[str, Any], List[str]]`

Output
- tuple -> `(cleaned_text, attributes, embedded_cos)`

#### CurriculumEvidenceExtractor._extract_metadata

Input
- self: Any
- line: str
- course_node: Dict[str, Any]

Output Type : `bool`

Output
- expression -> `False`
- expression -> `True`

#### CurriculumEvidenceExtractor.parse_pdf

Input
- self: Any
- pdf_path: str

Output Type : `Dict[str, Any]`

Output
- self.transformer.transform -> `self.transformer.transform(raw_output)`


## EvidenceModel/Transformers.py

### Class `EvidenceTransformer`

#### EvidenceTransformer.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvidenceTransformer.transform

Input
- self: Any
- tree: Dict[str, Any]

Output Type : `Dict[str, Any]`

Output
- dict -> `{'roots': cleaned_roots}`
- tree -> `tree`

#### EvidenceTransformer._canonicalize_roots

Input
- self: Any
- roots: List[Dict[str, Any]]

Output Type : `List[Dict[str, Any]]`

Output
- list -> `[primary_root]`
- list -> `[]`

#### EvidenceTransformer._process_node

Input
- self: Any
- node: Dict[str, Any]

Output Type : `Optional[Dict[str, Any]]`

Output
- node -> `node`
- expression -> `None`

#### EvidenceTransformer._reindex_node

Input
- self: Any
- node: Dict[str, Any]

Output Type : `None`

Output
- None -> `No explicit return`


## EvidenceModel/model.py

*No classes or methods.*

## EvidenceModel/pipeline.py

### Class `GriffinCore`

#### GriffinCore.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### GriffinCore.process

Input
- self: Any
- curriculum_pdf_path: str
- report_input: Union[str, List[Dict[str, Any]]]

Output Type : `EvidenceGraph`

Output
- graph -> `graph`


## EvidenceModel/encoders/report_encoder.py

### Class `ReportEncoder`

#### ReportEncoder.__init__

Input
- self: Any
- model_name: str
- device: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### ReportEncoder.encode

Input
- self: Any
- tokens: List[EvidenceToken]
- batch_size: int

Output Type : `List[EvidenceToken]`

Output
- tokens -> `tokens`

#### ReportEncoder._mean_pooling

Input
- token_embeddings: torch.Tensor
- attention_mask: torch.Tensor

Output Type : `torch.Tensor`

Output
- expression -> `summed / counts`


## EvidenceModel/encoders/topic_encoder.py

### Schema/Class `TopicEncoder`

Fields
- ALLOWED_NODE_TYPES

#### TopicEncoder.__init__

Input
- self: Any
- model_name: str
- device: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### TopicEncoder.extract_filtered_topics

Input
- self: Any
- heem_tree: Dict[str, Any]

Output Type : `List[Dict[str, Any]]`

Output
- extracted -> `extracted`

#### TopicEncoder.encode

Input
- self: Any
- heem_tree: Dict[str, Any]

Output Type : `List[Dict[str, Any]]`

Output
- topics -> `topics`
- list -> `[]`


## EvidenceModel/evaluation/__init__.py

*No classes or methods.*

## EvidenceModel/evaluation/benchmark_runner.py

### Class `BenchmarkRunner`

#### BenchmarkRunner.__init__

Input
- self: Any
- benchmark_config_path: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### BenchmarkRunner.run_benchmark

Input
- self: Any
- experiment_name: str
- griffin_pipeline: GriffinCore

Output Type : `EvaluationResult`

Output
- eval_result -> `eval_result`

#### BenchmarkRunner.save_results

Input
- self: Any
- eval_result: EvaluationResult
- output_path: str

Output Type : `Unknown`

Output
- None -> `No explicit return`


## EvidenceModel/evaluation/evaluator.py

### Schema/Class `EvaluationResult`

Fields
- retrieval: RetrievalMetricsResult
- validator: ValidatorMetricsResult
- graph: GraphMetricsResult
- runtime: RuntimeMetricsResult
- report_data: EvaluationReportData

### Class `Evaluator`

#### Evaluator.evaluate

Input
- self: Any
- experiment_name: str
- graph: EvidenceGraph
- all_topic_ids: List[int]
- retrieval_candidates: Dict[int, List[str]]
- retrieval_ground_truth: Dict[int, Set[str]]
- validator_ground_truth: Optional[Tuple[List[int], List[int], List[float]]]
- runtime_result: Optional[RuntimeMetricsResult]

Output Type : `EvaluationResult`

Output
- EvaluationResult -> `EvaluationResult(retrieval=retrieval_res, validator=validator_res, graph=graph_res, runtime=rt_res, report_data=report_data)`


## EvidenceModel/evaluation/graph_metrics.py

### Schema/Class `GraphMetricsResult`

Fields
- curriculum_coverage: float
- evidence_density: float
- duplicate_edge_rate: float
- hallucination_rate: float
- average_confidence: float

#### calculate_graph_metrics

Input
- graph: EvidenceGraph
- all_topic_ids: List[int]
- ground_truth_map: Dict[int, Set[str]]

Output Type : `GraphMetricsResult`

Output
- GraphMetricsResult -> `GraphMetricsResult(curriculum_coverage=curriculum_coverage, evidence_density=evidence_density, duplicate_edge_rate=duplicate_edge_rate, hallucination_rate=hallucination_rate, average_confidence=avg_confidence)`
- GraphMetricsResult -> `GraphMetricsResult()`


## EvidenceModel/evaluation/report_generator.py

### Schema/Class `EvaluationReportData`

Fields
- experiment_name: str
- retrieval: RetrievalMetricsResult
- validator: ValidatorMetricsResult
- graph: GraphMetricsResult
- runtime: RuntimeMetricsResult

### Class `EvaluationReportGenerator`

#### EvaluationReportGenerator.__init__

Input
- self: Any
- data: EvaluationReportData

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvaluationReportGenerator.to_dict

Input
- self: Any

Output Type : `Dict[str, Any]`

Output
- asdict -> `asdict(self.data)`

#### EvaluationReportGenerator.to_json

Input
- self: Any
- indent: int

Output Type : `str`

Output
- json.dumps -> `json.dumps(self.to_dict(), indent=indent)`

#### EvaluationReportGenerator.render_console_report

Input
- self: Any

Output Type : `str`

Output
- report -> `report`


## EvidenceModel/evaluation/retrieval_metrics.py

### Schema/Class `RetrievalMetricsResult`

Fields
- precision_at_k: Dict[int, float]
- recall_at_k: Dict[int, float]
- mrr: float
- ndcg_at_k: Dict[int, float]

#### precision_at_k

Input
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

Output Type : `float`

Output
- expression -> `relevant_retrieved / k`
- expression -> `0.0`

#### recall_at_k

Input
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

Output Type : `float`

Output
- expression -> `relevant_retrieved / len(ground_truth)`
- expression -> `0.0`

#### mean_reciprocal_rank

Input
- all_retrieved: List[List[str]]
- all_ground_truth: List[Set[str]]

Output Type : `float`

Output
- expression -> `sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0`
- expression -> `0.0`

#### ndcg_at_k

Input
- retrieved: List[str]
- ground_truth: Set[str]
- k: int

Output Type : `float`

Output
- expression -> `dcg / idcg`
- expression -> `0.0`

#### calculate_retrieval_metrics

Input
- retrieved_map: Dict[int, List[str]]
- ground_truth_map: Dict[int, Set[str]]
- k_list: List[int]

Output Type : `RetrievalMetricsResult`

Output
- RetrievalMetricsResult -> `RetrievalMetricsResult(precision_at_k=mean_p, recall_at_k=mean_r, mrr=mrr_score, ndcg_at_k=mean_ndcg)`


## EvidenceModel/evaluation/runtime_metrics.py

### Schema/Class `RuntimeMetricsResult`

Fields
- total_runtime_seconds: float
- stage_runtimes: Dict[str, float]
- peak_memory_mb: float
- gpu_memory_mb: Optional[float]

### Class `RuntimeTracker`

#### RuntimeTracker.__init__

Input
- self: Any

Output Type : `None`

Output
- None -> `No explicit return`

#### RuntimeTracker.start

Input
- self: Any

Output Type : `None`

Output
- None -> `No explicit return`

#### RuntimeTracker.start_stage

Input
- self: Any
- stage_name: str

Output Type : `None`

Output
- None -> `No explicit return`

#### RuntimeTracker.stop_stage

Input
- self: Any
- stage_name: str

Output Type : `None`

Output
- None -> `No explicit return`

#### RuntimeTracker.stop

Input
- self: Any

Output Type : `RuntimeMetricsResult`

Output
- RuntimeMetricsResult -> `RuntimeMetricsResult(total_runtime_seconds=total_runtime, stage_runtimes=dict(self.stage_runtimes), peak_memory_mb=peak / (1024 * 1024), gpu_memory_mb=gpu_memory)`


## EvidenceModel/evaluation/validator_metrics.py

### Schema/Class `ValidatorMetricsResult`

Fields
- accuracy: float
- precision: float
- recall: float
- f1_score: float
- roc_auc: Optional[float]

#### calculate_validator_metrics

Input
- y_true: List[int]
- y_pred: List[int]
- y_prob: Optional[List[float]]

Output Type : `ValidatorMetricsResult`

Output
- ValidatorMetricsResult -> `ValidatorMetricsResult(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1, roc_auc=auc)`
- ValidatorMetricsResult -> `ValidatorMetricsResult()`

#### _compute_roc_auc

Input
- y_true: List[int]
- y_prob: List[float]

Output Type : `float`

Output
- float -> `float(u_stat / (n_pos * n_neg))`
- expression -> `0.0`


## EvidenceModel/experiments/compare_baselines.py

#### run_baseline_comparison

Input
- None

Output Type : `Unknown`

Output
- None -> `No explicit return`


## EvidenceModel/experiments/experiment_01.py

#### run_experiment

Input
- None

Output Type : `None`

Output
- None -> `No explicit return`

#### main

Input
- None

Output Type : `None`

Output
- None -> `No explicit return`


## EvidenceModel/experiments/experiment_02.py

#### run_experiment_02

Input
- None

Output Type : `Unknown`

Output
- None -> `No explicit return`


## EvidenceModel/parsers/document_parser.py

### Schema/Class `DocumentStructureParser`

Fields
- IGNORED_HEADERS

#### DocumentStructureParser.parse

Input
- self: Any
- pdf_pages: List[Dict[str, Any]]
- metadata: ReportMetadata

Output Type : `GriffinDocument`

Output
- GriffinDocument -> `GriffinDocument(version='1.0', metadata=metadata, statistics=statistics, input_tokens=input_tokens, tokens=evidence_tokens)`

#### DocumentStructureParser._is_heading

Input
- text: str

Output Type : `bool`

Output
- bool -> `bool(re.match('^(chapter\\s+\\d+|\\d+(\\.\\d+)*\\s+)', text, re.IGNORECASE))`
- expression -> `False`
- expression -> `True`

#### DocumentStructureParser._heading_level

Input
- text: str

Output Type : `int`

Output
- expression -> `numbering.count('.') + 1`
- expression -> `1`


## EvidenceModel/parsers/metadata_extractor.py

### Class `ReportMetadataExtractor`

#### ReportMetadataExtractor.__init__

Input
- self: Any
- model_name_or_path: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### ReportMetadataExtractor.extract

Input
- self: Any
- cover_page_image: Any
- raw_tokens: list[str]
- bbox: list[list[int]]

Output Type : `ReportMetadata`

Output
- metadata -> `metadata`


## EvidenceModel/presentation/builder.py

### Class `GriffinResultBuilder`

#### GriffinResultBuilder.__init__

Input
- self: Any
- confidence_threshold: float

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### GriffinResultBuilder.build

Input
- self: Any
- evidence_graph: Dict[str, Any]
- metadata: Dict[str, Any]

Output Type : `GriffinResult`

Output
- GriffinResult -> `GriffinResult(report_information=ReportMetadata(report_title=metadata.get('title', 'Curriculum Analysis Report'), student=metadata.get('student', 'Unknown Student'), university=metadata.get('university', 'GSFC University'), total_pages=metadata.get('total_pages', 0), processing_time_seconds=metadata.get('processing_time', 0.0), timestamp=datetime.utcnow().isoformat() + 'Z'), overall_summary=overall_summary, curriculum_mapping=unit_details, topic_mapping=topic_details, evidence_analysis=evidence_analysis, coverage_analysis=CoverageAnalysis(covered_topics=covered_topics, uncovered_topics=uncovered_topics, partially_covered_topics=partially_covered_topics), depth_and_significance=depth_significance, graph_statistics=graph_stats, visualizations=visualizations)`

#### GriffinResultBuilder._build_visualizations

Input
- self: Any
- units: List[UnitMappingDetail]
- topics: List[TopicMappingDetail]
- page_density: Dict[int, int]
- units_map: Dict[str, Any]
- topics_map: Dict[str, Any]

Output Type : `VisualizationPayload`

Output
- VisualizationPayload -> `VisualizationPayload(unit_coverage_bar_chart=unit_bar, topic_coverage_pie_chart=topic_pie, page_evidence_distribution=page_dist, confidence_histogram=conf_hist, curriculum_treemap={'name': 'Curriculum', 'children': treemap_children}, curriculum_sunburst={'name': 'Curriculum', 'children': sunburst_children})`


## EvidenceModel/presentation/exporter.py

#### export_griffin_result

Input
- evidence_graph: dict
- metadata: dict
- output_path: str

Output Type : `str`

Output
- output_path -> `output_path`


## EvidenceModel/presentation/schema.py

### Schema/Class `ReportMetadata`

Fields
- report_title: str
- student: str
- university: str
- total_pages: int
- processing_time_seconds: float
- timestamp: str

### Schema/Class `OverallSummary`

Fields
- overall_coverage_pct: float
- overall_confidence: float
- total_units: int
- covered_units: int
- total_topics: int
- covered_topics: int
- missing_topics_count: int
- total_evidence: int
- validated_evidence: int

### Schema/Class `UnitMappingDetail`

Fields
- unit_id: str
- unit_name: str
- coverage_percentage: float
- topics_covered: List[str]
- topics_missing: List[str]
- evidence_count: int
- average_confidence: float
- significance_score: float

### Schema/Class `TopicMappingDetail`

Fields
- topic_id: str
- topic_name: str
- unit_id: str
- matched: bool
- confidence: float
- evidence_count: int
- supporting_pages: List[int]
- supporting_headings: List[str]
- evidence_ids: List[str]

### Schema/Class `EvidenceDetail`

Fields
- evidence_id: str
- topic_id: str
- page_number: int
- heading: str
- similarity_score: float
- validation_score: float

### Schema/Class `EvidenceAnalysis`

Fields
- strongest_evidence: List[EvidenceDetail]
- weakest_evidence: List[EvidenceDetail]
- evidence_density_per_page: Dict[int, int]
- evidence_distribution_by_unit: Dict[str, int]

### Schema/Class `CoverageAnalysis`

Fields
- covered_topics: List[str]
- uncovered_topics: List[str]
- partially_covered_topics: List[str]

### Schema/Class `DepthAndSignificance`

Fields
- breadth_score: float
- depth_score: float
- evidence_richness_pct: float
- curriculum_completeness_pct: float
- report_comprehensiveness_score: float
- average_evidence_per_topic: float
- average_evidence_per_unit: float

### Schema/Class `GraphStatistics`

Fields
- total_nodes: int
- total_edges: int
- unit_nodes: int
- topic_nodes: int
- evidence_nodes: int
- graph_density: float
- average_degree: float

### Schema/Class `VisualizationPayload`

Fields
- unit_coverage_bar_chart: Dict[str, Any]
- topic_coverage_pie_chart: Dict[str, Any]
- page_evidence_distribution: Dict[str, Any]
- confidence_histogram: Dict[str, Any]
- curriculum_treemap: Dict[str, Any]
- curriculum_sunburst: Dict[str, Any]

### Schema/Class `GriffinResult`

Fields
- report_information: ReportMetadata
- overall_summary: OverallSummary
- curriculum_mapping: List[UnitMappingDetail]
- topic_mapping: List[TopicMappingDetail]
- evidence_analysis: EvidenceAnalysis
- coverage_analysis: CoverageAnalysis
- depth_and_significance: DepthAndSignificance
- graph_statistics: GraphStatistics
- visualizations: VisualizationPayload


## EvidenceModel/report_tokenizer/__init__.py

*No classes or methods.*

## EvidenceModel/report_tokenizer/duplicate_detector.py

### Class `DuplicateDetector`

#### DuplicateDetector.__init__

Input
- self: Any
- hamming_threshold: int

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### DuplicateDetector.is_duplicate

Input
- self: Any
- text: str

Output Type : `bool`

Output
- expression -> `False`
- expression -> `True`

#### DuplicateDetector.filter_margin_duplicates

Input
- self: Any
- margin_blocks: List[TextBlock]

Output Type : `List[TextBlock]`

Output
- unique_margins -> `unique_margins`

#### DuplicateDetector._hamming_distance

Input
- hex1: str
- hex2: str

Output Type : `int`

Output
- dist -> `dist`


## EvidenceModel/report_tokenizer/evidence_builder.py

### Class `EvidenceBuilder`

#### EvidenceBuilder.build_evidence_tokens

Input
- self: Any
- sections: List[ParsedSection]

Output Type : `List[EvidenceToken]`

Output
- evidence_tokens -> `evidence_tokens`

#### EvidenceBuilder._extract_concepts

Input
- self: Any
- text: str

Output Type : `List[str]`

Output
- sorted -> `sorted({word for word in words if word in TECHNICAL_INDICATORS})`

#### EvidenceBuilder._extract_entities

Input
- self: Any
- text: str

Output Type : `List[str]`

Output
- sorted -> `sorted(acronyms | camel_case)`

#### EvidenceBuilder._extract_keywords

Input
- self: Any
- text: str

Output Type : `List[str]`

Output
- sorted -> `sorted(keywords)`

#### EvidenceBuilder._infer_category

Input
- self: Any
- section: ParsedSection

Output Type : `str`

Output
- expression -> `'CONTENT'`
- expression -> `'ABSTRACT'`
- expression -> `'INTRODUCTION'`
- expression -> `'METHODOLOGY'`
- expression -> `'RESULTS'`
- expression -> `'DISCUSSION'`
- expression -> `'CONCLUSION'`
- expression -> `'REFERENCES'`


## EvidenceModel/report_tokenizer/evidence_ranker.py

### Class `EvidenceRanker`

#### EvidenceRanker.rank_and_score_tokens

Input
- self: Any
- tokens: List[EvidenceToken]

Output Type : `List[EvidenceToken]`

Output
- tokens -> `tokens`

#### EvidenceRanker._calculate_technical_density

Input
- self: Any
- token: EvidenceToken

Output Type : `float`

Output
- float -> `float(min(1.0, max(0.0, density)))`
- expression -> `0.0`

#### EvidenceRanker._calculate_semantic_density

Input
- self: Any
- token: EvidenceToken

Output Type : `float`

Output
- float -> `float(min(1.0, max(0.0, semantic_density)))`
- expression -> `0.0`

#### EvidenceRanker._calculate_information_gain

Input
- self: Any
- token: EvidenceToken
- technical_density: float
- semantic_density: float

Output Type : `float`

Output
- float -> `float(min(1.0, max(0.0, gain)))`


## EvidenceModel/report_tokenizer/layout_analyzer.py

### Class `LayoutAnalyzer`

#### LayoutAnalyzer.__init__

Input
- self: Any
- header_margin_ratio: float
- footer_margin_ratio: float

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### LayoutAnalyzer.analyze_page_layout

Input
- self: Any
- page: RawPage

Output Type : `Tuple[List[TextBlock], List[TextBlock]]`

Output
- tuple -> `(body_blocks, margin_blocks)`

#### LayoutAnalyzer.detect_heading_level

Input
- self: Any
- block: TextBlock
- mean_font_size: float

Output Type : `int`

Output
- expression -> `0`
- expression -> `1`
- expression -> `2`
- expression -> `3`


## EvidenceModel/report_tokenizer/metadata_extractor.py

### Schema/Class `MetadataExtractor`

Fields
- DATE_REGEX
- YEAR_REGEX

#### MetadataExtractor.extract_metadata

Input
- self: Any
- pages: List[RawPage]

Output Type : `ReportMetadata`

Output
- metadata -> `metadata`

#### MetadataExtractor._extract_title

Input
- self: Any
- blocks: List[TextBlock]

Output Type : `Optional[str]`

Output
- expression -> `None`
- largest.text.strip().replace -> `largest.text.strip().replace('\n', ' ')`

#### MetadataExtractor._extract_regex

Input
- self: Any
- text: str
- pattern: str

Output Type : `Optional[str]`

Output
- expression -> `None`
- match.group(0).strip -> `match.group(0).strip()`

#### MetadataExtractor._extract_field

Input
- self: Any
- text: str
- labels: List[str]

Output Type : `Optional[str]`

Output
- expression -> `None`
- match.group(1).strip -> `match.group(1).strip()`


## EvidenceModel/report_tokenizer/model.py

### Schema/Class `PipelineStage`

Fields
- name: str
- description: str

### Schema/Class `GriffinTokenizerPipeline`

Fields
- VERSION
- STAGES: List[PipelineStage]

#### GriffinTokenizerPipeline.print_pipeline

Input
- cls: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`


## EvidenceModel/report_tokenizer/parser.py

### Class `StructuralParser`

#### StructuralParser.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### StructuralParser.parse_pdf

Input
- self: Any
- pdf_input: str | bytes

Output Type : `List[ParsedSection]`

Output
- self._build_structural_sections -> `self._build_structural_sections(raw_pages)`

#### StructuralParser._build_structural_sections

Input
- self: Any
- pages: List[RawPage]

Output Type : `List[ParsedSection]`

Output
- parsed_sections -> `parsed_sections`


## EvidenceModel/report_tokenizer/schemas.py

### Schema/Class `SectionType`

Fields
- COVER_PAGE
- DECLARATION
- CERTIFICATE
- ACKNOWLEDGEMENT
- ABSTRACT
- TABLE_OF_CONTENTS
- LIST_OF_TABLES
- LIST_OF_FIGURES
- ABBREVIATIONS
- INTRODUCTION
- LITERATURE_REVIEW
- PROBLEM_STATEMENT
- OBJECTIVES
- METHODOLOGY
- ARCHITECTURE
- IMPLEMENTATION
- DATASET
- RESULTS
- DISCUSSION
- CONCLUSION
- REFERENCES
- APPENDIX
- BODY_CONTENT
- UNKNOWN

### Schema/Class `LayoutBoundingBox`

Fields
- x0: float
- y0: float
- x1: float
- y1: float
- page_width: float
- page_height: float

### Schema/Class `TextBlock`

Fields
- text: str
- bbox: LayoutBoundingBox
- font_name: str
- font_size: float
- is_bold: bool
- is_italic: bool
- page_number: int
- line_spacing: float

### Schema/Class `RawPage`

Fields
- page_number: int
- width: float
- height: float
- blocks: List[TextBlock]

### Schema/Class `ReportMetadata`

Fields
- title: Optional[str]
- author: Optional[str]
- enrollment: Optional[str]
- mentor: Optional[str]
- industry_mentor: Optional[str]
- institution: Optional[str]
- department: Optional[str]
- semester: Optional[str]
- degree: Optional[str]
- submission_date: Optional[str]
- report_type: Optional[str]
- total_pages: int
- raw_attributes: Dict[str, Any]

### Schema/Class `ParsedSection`

Fields
- chapter: str
- section: str
- subsection: str
- section_type: SectionType
- heading: str
- page_number: int
- blocks: List[TextBlock]
- is_noise: bool

### Schema/Class `EvidenceToken`

Fields
- token_id: str
- chapter: str
- section: str
- subsection: str
- page: int
- heading: str
- text: str
- concepts: List[str]
- entities: List[str]
- formula_refs: List[str]
- figure_refs: List[str]
- table_refs: List[str]
- citations: List[str]
- technical_density: float
- semantic_density: float
- information_gain: float

### Schema/Class `StructuredReportDocument`

Fields
- metadata: ReportMetadata
- tokens: List[EvidenceToken]
- excluded_pages: List[int]
- total_raw_blocks: int
- retained_evidence_blocks: int


## EvidenceModel/report_tokenizer/section_classifier.py

### Schema/Class `SectionClassifier`

Fields
- SECTION_PATTERNS

#### SectionClassifier.classify_heading

Input
- self: Any
- heading_text: str

Output Type : `SectionType`

Output
- expression -> `SectionType.BODY_CONTENT`
- stype -> `stype`

#### SectionClassifier.is_administrative_noise

Input
- self: Any
- section_type: SectionType

Output Type : `bool`

Output
- expression -> `section_type in NOISE_SECTION_TYPES`


## EvidenceModel/report_tokenizer/tokenizer.py

### Class `GriffinReportTokenizer`

#### GriffinReportTokenizer.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### GriffinReportTokenizer.tokenize

Input
- self: Any
- pdf_input: Union[str, bytes]

Output Type : `GriffinDocument`

Output
- GriffinDocument -> `GriffinDocument(version='1.0', metadata=metadata, statistics=statistics, input_tokens=[], tokens=evidence_tokens)`


## EvidenceModel/report_tokenizer/utils.py

#### calculate_shannon_entropy

Input
- text: str

Output Type : `float`

Output
- float -> `float(entropy / 8.0)`
- expression -> `0.0`

#### extract_formulas

Input
- text: str

Output Type : `List[str]`

Output
- list -> `list(set(matches))`

#### extract_figure_and_table_refs

Input
- text: str

Output Type : `Tuple[List[str], List[str]]`

Output
- tuple -> `(figures, tables)`

#### extract_academic_citations

Input
- text: str

Output Type : `List[str]`

Output
- list -> `list(set(citations))`

#### compute_simhash_signature

Input
- text: str

Output Type : `str`

Output
- expression -> `f'{fingerprint:016x}'`
- expression -> `'0' * 16`


## EvidenceModel/retrieval/evidence_retriever.py

### Class `EvidenceRetriever`

#### EvidenceRetriever.__init__

Input
- self: Any
- top_k: int

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvidenceRetriever.retrieve

Input
- self: Any
- encoded_topics: List[Dict[str, Any]]
- encoded_tokens: List[EvidenceToken]

Output Type : `List[CandidateEvidence]`

Output
- candidates -> `candidates`
- list -> `[]`


## EvidenceModel/validation/evidence_validator.py

### Class `EvidenceValidator`

#### EvidenceValidator.__init__

Input
- self: Any
- model_name: str
- device: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvidenceValidator.validate

Input
- self: Any
- topic_text: str
- token: EvidenceToken
- similarity_score: float

Output Type : `ValidatedEvidence`

Output
- ValidatedEvidence -> `ValidatedEvidence(topic_id=-1, token_id=token.token_id, page_number=token.page_number, similarity=similarity_score, confidence=confidence, reasoning_score=reasoning_score, explanation=explanation)`


## graph/evidence_graph.py

### Class `EvidenceGraphBuilder`

#### EvidenceGraphBuilder.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvidenceGraphBuilder.build

Input
- self: Any
- units: List[Dict[str, Any]]
- topics: List[Dict[str, Any]]
- validated_evidences: List[ValidatedEvidence]
- evidence_tokens: List[EvidenceToken]

Output Type : `EvidenceGraph`

Output
- expression -> `self.graph`


## KnowledgeBase/knowledge_evidence.py

### Class `EvidenceTransformer`

#### EvidenceTransformer.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvidenceTransformer.transform

Input
- self: Any
- tree: Dict[str, Any]

Output Type : `Dict[str, Any]`

Output
- dict -> `{'roots': cleaned_roots}`
- tree -> `tree`

#### EvidenceTransformer._canonicalize_roots

Input
- self: Any
- roots: List[Dict[str, Any]]

Output Type : `List[Dict[str, Any]]`

Output
- list -> `[primary_root]`
- list -> `[]`

#### EvidenceTransformer._process_node

Input
- self: Any
- node: Dict[str, Any]

Output Type : `Optional[Dict[str, Any]]`

Output
- node -> `node`
- expression -> `None`

#### EvidenceTransformer._reindex_node

Input
- self: Any
- node: Dict[str, Any]

Output Type : `None`

Output
- None -> `No explicit return`

### Class `CurriculumEvidenceExtractor`

#### CurriculumEvidenceExtractor.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### CurriculumEvidenceExtractor._next_id

Input
- self: Any

Output Type : `int`

Output
- current_id -> `current_id`

#### CurriculumEvidenceExtractor._create_node

Input
- self: Any
- node_type: str
- text: str
- page: int
- confidence: float
- attributes: Optional[Dict[str, Any]]

Output Type : `Dict[str, Any]`

Output
- node -> `node`

#### CurriculumEvidenceExtractor._clean_layout_artifacts

Input
- self: Any
- text: str

Output Type : `str`

Output
- text -> `text`

#### CurriculumEvidenceExtractor._is_noise

Input
- self: Any
- line: str

Output Type : `bool`

Output
- expression -> `False`
- expression -> `True`

#### CurriculumEvidenceExtractor._parse_attributes_and_cos

Input
- self: Any
- raw_text: str

Output Type : `Tuple[str, Dict[str, Any], List[str]]`

Output
- tuple -> `(cleaned_text, attributes, embedded_cos)`

#### CurriculumEvidenceExtractor._extract_metadata

Input
- self: Any
- line: str
- course_node: Dict[str, Any]

Output Type : `bool`

Output
- expression -> `False`
- expression -> `True`

#### CurriculumEvidenceExtractor.parse_pdf

Input
- self: Any
- pdf_path: str

Output Type : `Dict[str, Any]`

Output
- self.transformer.transform -> `self.transformer.transform(raw_output)`


## KnowledgeBase/model.py

*No classes or methods.*

## llm/__init__.py

*No classes or methods.*

## llm/config.py

*No classes or methods.*

## llm/prompts.py

*No classes or methods.*

## llm/Client/__init__.py

*No classes or methods.*

## llm/Client/ollama_client.py

### Class `OllamaClient`

#### OllamaClient.__init__

Input
- self: Any
- model: str

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### OllamaClient.chat

Input
- self: Any
- messages: Any
- temperature: Any

Output Type : `Unknown`

Output
- expression -> `response['message']['content']`


## llm/Services/__init__.py

*No classes or methods.*

## llm/Services/chat_service.py

#### chat

Input
- message: str
- history: Any
- system_prompt: Any

Output Type : `Unknown`

Output
- _client.chat -> `_client.chat(messages=messages, temperature=TEMPERATURE)`


## rl/agent.py

### Class `ActorCritic`

#### ActorCritic.__init__

Input
- self: Any
- state_dim: int
- action_dim: int

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### ActorCritic.forward

Input
- self: Any
- state: torch.Tensor

Output Type : `Unknown`

Output
- tuple -> `(probs, value)`


## rl/environment.py

### Class `GriffinSearchEnv`

#### GriffinSearchEnv.__init__

Input
- self: Any
- topics: list
- paragraphs: list

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### GriffinSearchEnv.reset

Input
- self: Any
- seed: Any
- options: Any

Output Type : `Unknown`

Output
- tuple -> `(self._get_obs(), {})`

#### GriffinSearchEnv._get_obs

Input
- self: Any

Output Type : `Unknown`

Output
- np.concatenate -> `np.concatenate([topic_vec, ctx_vec, coverage, step_ratio])`

#### GriffinSearchEnv.step

Input
- self: Any
- action: int

Output Type : `Unknown`

Output
- tuple -> `(self._get_obs(), reward, terminated, False, {})`


## Routes/chat.py

#### send_chat_message

Input
- chat_id: str
- content: str
- db: Session

Output Type : `Unknown`

Output
- dict -> `{'user_message': msg.content, 'response': bot_msg.content}`


## Routes/evaluation.py

#### start_evaluation

Input
- payload: EvaluationCreateSchema
- background_tasks: BackgroundTasks
- db: Session

Output Type : `Unknown`

Output
- eval_obj -> `eval_obj`

#### get_job_status

Input
- evaluation_id: str
- db: Session

Output Type : `Unknown`

Output
- job -> `job`

#### get_evaluation_result

Input
- evaluation_id: str
- db: Session

Output Type : `Unknown`

Output
- dict -> `{'evaluation_id': evaluation_id, 'results': [r.griffin_result for r in reports]}`


## Routes/health.py

#### check_health

Input
- db: Session

Output Type : `Unknown`

Output
- dict -> `{'status': 'healthy', 'database': db_status, 'engine': 'Griffin Core v1.0 Backend'}`


## Routes/history.py

#### get_evaluation_history

Input
- project_id: str
- db: Session

Output Type : `Unknown`

Output
- query.order_by(Evaluation.created_at.desc()).all -> `query.order_by(Evaluation.created_at.desc()).all()`


## Routes/projects.py

#### list_projects

Input
- workspace_id: str
- db: Session

Output Type : `Unknown`

Output
- query.all -> `query.all()`


## Routes/reports.py

#### async upload_report

Input
- project_id: str
- student_name: str
- file: UploadFile
- db: Session

Output Type : `Unknown`

Output
- report -> `report`


## Routes/settings.py

#### get_system_settings

Input
- None

Output Type : `Unknown`

Output
- dict -> `{'confidence_threshold': 0.5, 'max_concurrent_jobs': 4, 'vector_embedding_model': 'all-MiniLM-L6-v2', 'llm_validation_active': True}`


## Routes/workspace.py

#### workspaces

Input
- db: Session

Output Type : `Unknown`

Output
- db.query(Workspace).all -> `db.query(Workspace).all()`

#### create_workspace

Input
- name: str
- description: str
- db: Session

Output Type : `Unknown`

Output
- ws -> `ws`


## Schemas/__init__.py

*No classes or methods.*

## Schemas/chat.py

### Schema/Class `MessageCreateSchema`

Fields
- chat_id: str
- content: str

### Schema/Class `MessageResponseSchema`

Fields
- model_config
- id: str
- chat_id: str
- sender: str
- content: str
- created_at: datetime

### Schema/Class `ChatCreateSchema`

Fields
- project_id: str
- evaluation_id: Optional[str]
- title: str

### Schema/Class `ChatResponseSchema`

Fields
- model_config
- id: str
- project_id: str
- evaluation_id: Optional[str]
- title: str
- created_at: datetime
- updated_at: datetime

### Schema/Class `ChatDetailResponseSchema`

Fields
- messages: List[MessageResponseSchema]


## Schemas/common.py

### Schema/Class `APIResponse`

Fields
- success: bool
- message: Optional[str]
- data: Optional[T]

### Schema/Class `StatusResponse`

Fields
- success: bool
- message: str

### Schema/Class `PaginationParams`

Fields
- page: int
- page_size: int

### Schema/Class `PaginatedResponse`

Fields
- items: List[T]
- total_items: int
- page: int
- page_size: int
- total_pages: int


## Schemas/curriculum.py

### Schema/Class `CurriculumCreateSchema`

Fields
- project_id: str
- title: str

### Schema/Class `CurriculumResponseSchema`

Fields
- model_config
- id: str
- project_id: str
- title: str
- file_path: str
- parsed_schema: Optional[Dict[str, Any]]
- created_at: datetime
- updated_at: datetime


## Schemas/evaluation.py

### Schema/Class `EvaluationCreateSchema`

Fields
- project_id: str
- curriculum_id: str
- report_ids: list[str]
- name: str

### Schema/Class `BatchJobResponseSchema`

Fields
- model_config
- id: str
- evaluation_id: str
- status: JobStatus
- progress_percentage: float
- error_message: Optional[str]
- started_at: Optional[datetime]
- completed_at: Optional[datetime]

### Schema/Class `EvaluationResponseSchema`

Fields
- model_config
- id: str
- project_id: str
- curriculum_id: str
- name: str
- status: JobStatus
- created_at: datetime

### Schema/Class `GriffinResultResponseSchema`

Fields
- evaluation_id: str
- report_id: str
- griffin_result: Dict[str, Any]


## Schemas/projects.py

### Schema/Class `ProjectCreateSchema`

Fields
- workspace_id: str
- name: str
- description: Optional[str]

### Schema/Class `ProjectUpdateSchema`

Fields
- name: Optional[str]
- description: Optional[str]

### Schema/Class `ProjectResponseSchema`

Fields
- model_config
- id: str
- workspace_id: str
- name: str
- description: Optional[str]
- created_at: datetime
- updated_at: datetime

### Schema/Class `ProjectDetailResponseSchema`

Fields
- total_curriculums: int
- total_reports: int
- total_evaluations: int


## Schemas/report.py

### Schema/Class `ReportCreateSchema`

Fields
- project_id: str
- title: str
- student_name: Optional[str]

### Schema/Class `ReportUpdateSchema`

Fields
- title: Optional[str]
- student_name: Optional[str]

### Schema/Class `ReportResponseSchema`

Fields
- model_config
- id: str
- project_id: str
- title: str
- student_name: Optional[str]
- file_path: str
- total_pages: int
- created_at: datetime
- updated_at: datetime


## Schemas/schemas.py

### Schema/Class `CurriculumNodeType`

Fields
- COURSE
- METADATA
- OBJECTIVE
- UNIT
- TOPIC

### Schema/Class `HEEMNode`

Fields
- id: int
- type: CurriculumNodeType
- text: str
- page: int
- confidence: float
- attributes: Dict[str, Any]
- children: List['HEEMNode']

### Schema/Class `ReportMetadata`

Fields
- title: Optional[str]
- subtitle: Optional[str]
- author: Optional[str]
- institution: Optional[str]
- department: Optional[str]
- university: Optional[str]
- guide: Optional[str]
- supervisor: Optional[str]
- degree: Optional[str]
- semester: Optional[str]
- date: Optional[str]
- year: Optional[str]
- language: Optional[str]
- total_pages: int
- raw_metadata: Dict[str, Any]

### Schema/Class `InputTokenType`

Fields
- METADATA
- NAVIGATION
- REFERENCE
- COMPLIANCE
- QUALITY
- EVIDENCE

### Schema/Class `InputToken`

Fields
- token_id: str
- token_type: InputTokenType
- page_number: int
- text: str
- chapter: Optional[str]
- section: Optional[str]
- subsection: Optional[str]
- heading: Optional[str]
- bbox: Optional[List[float]]
- attributes: Dict[str, Any]

### Schema/Class `EvidenceToken`

Fields
- token_id: str
- page_number: int
- chapter: Optional[str]
- section: Optional[str]
- subsection: Optional[str]
- heading: Optional[str]
- text: str
- token_type: str
- category: str
- parent_token: Optional[str]
- concepts: List[str]
- entities: List[str]
- keywords: List[str]
- citations: List[str]
- figure_refs: List[str]
- table_refs: List[str]
- equation_refs: List[str]
- semantic_density: float
- technical_density: float
- information_gain: float
- priority: float
- confidence: float
- embedding: Optional[List[float]]
- embedding_model: Optional[str]
- embedding_dimension: Optional[int]
- source_page: Optional[int]
- source_bbox: Optional[List[float]]
- source_id: Optional[str]
- metadata: Dict[str, Any]

### Schema/Class `GriffinStatistics`

Fields
- total_pages: int
- total_input_tokens: int
- total_evidence_tokens: int
- total_figures: int
- total_tables: int
- total_equations: int
- total_citations: int

### Schema/Class `GriffinDocument`

Fields
- version: str
- metadata: ReportMetadata
- statistics: GriffinStatistics
- input_tokens: List[InputToken]
- tokens: List[EvidenceToken]

### Schema/Class `CandidateEvidence`

Fields
- topic_id: int
- token_id: str
- similarity_score: float

### Schema/Class `ValidatedEvidence`

Fields
- topic_id: int
- token_id: str
- page_number: int
- similarity: float
- confidence: float
- reasoning_score: float
- explanation: str

### Schema/Class `GraphNode`

Fields
- id: str
- label: str
- node_type: str
- attributes: Dict[str, Any]

### Schema/Class `GraphEdge`

Fields
- source: str
- target: str
- relation: str
- similarity: float
- confidence: float
- reasoning_score: float

### Schema/Class `EvidenceGraph`

Fields
- nodes: Dict[str, GraphNode]
- edges: List[GraphEdge]

#### EvidenceGraph.add_node

Input
- self: Any
- node: GraphNode

Output Type : `None`

Output
- None -> `No explicit return`

#### EvidenceGraph.add_edge

Input
- self: Any
- edge: GraphEdge

Output Type : `None`

Output
- None -> `No explicit return`

#### EvidenceGraph.get_node

Input
- self: Any
- node_id: str

Output Type : `Optional[GraphNode]`

Output
- self.nodes.get -> `self.nodes.get(node_id)`

#### EvidenceGraph.get_edges_by_relation

Input
- self: Any
- relation: str

Output Type : `List[GraphEdge]`

Output
- expression -> `[edge for edge in self.edges if edge.relation == relation]`

### Schema/Class `EvidenceNode`

Fields
- id: str
- node_type: str
- label: str
- page_number: Optional[int]
- heading: Optional[str]
- content: Optional[str]
- metadata: Dict[str, Any]

### Schema/Class `EvidenceEdge`

Fields
- source_id: str
- target_id: str
- relationship: str
- similarity: float
- validation_score: float

### Schema/Class `ValidatedEvidence`

Fields
- evidence_id: str
- topic_id: str
- page_number: Optional[int]
- heading: str
- similarity: float
- validation_score: float

### Schema/Class `Topic`

Fields
- id: str
- name: str
- unit_id: str

### Schema/Class `Unit`

Fields
- id: str
- name: str
- topic_ids: List[str]

### Schema/Class `EvidenceGraph`

Fields
- nodes: List[EvidenceNode]
- edges: List[EvidenceEdge]
- units: List[Unit]
- topics: List[Topic]
- evidence_nodes: List[EvidenceNode]
- validated_evidences: List[ValidatedEvidence]
- is_directed: bool

### Schema/Class `GriffinResult`

Fields
- summary: Dict[str, Any]
- curriculum_mapping: Dict[str, Any]
- unit_mapping: List[Dict[str, Any]]
- topic_mapping: List[Dict[str, Any]]
- evidence_mapping: List[Dict[str, Any]]
- coverage_statistics: Dict[str, Any]
- graph_statistics: Dict[str, Any]
- runtime: Dict[str, Any]
- recommendations: List[str]


## Schemas/settings.py

### Schema/Class `SettingsUpdateSchema`

Fields
- confidence_threshold: Optional[float]
- max_concurrent_jobs: Optional[int]
- llm_validation_active: Optional[bool]

### Schema/Class `SettingsResponseSchema`

Fields
- confidence_threshold: float
- max_concurrent_jobs: int
- vector_embedding_model: str
- llm_validation_active: bool


## Schemas/workspace.py

### Schema/Class `WorkspaceCreateSchema`

Fields
- name: str
- description: Optional[str]

### Schema/Class `WorkspaceUpdateSchema`

Fields
- name: Optional[str]
- description: Optional[str]

### Schema/Class `WorkspaceResponseSchema`

Fields
- model_config
- id: str
- name: str
- description: Optional[str]
- owner_id: Optional[str]
- created_at: datetime
- updated_at: datetime

### Schema/Class `WorkspaceDetailResponseSchema`

Fields
- project_count: int


## Services/evaluation_service.py

### Class `EvaluationService`

#### EvaluationService.create_evaluation

Input
- db: Session
- project_id: str
- curriculum_id: str
- name: str

Output Type : `Evaluation`

Output
- eval_obj -> `eval_obj`

#### EvaluationService.run_async_evaluation

Input
- db: Session
- evaluation_id: str
- report_ids: list[str]

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Services/griffin_services.py

### Class `GriffinService`

#### GriffinService.process_report

Input
- report_file_path: str
- curriculum_file_path: str
- metadata: Dict[str, Any]

Output Type : `Dict[str, Any]`

Output
- mock_result -> `mock_result`


## Services/project_services.py

### Class `ProjectService`

#### ProjectService.list_projects

Input
- db: Session
- workspace_id: Optional[str]

Output Type : `List[Project]`

Output
- query.order_by(Project.created_at.desc()).all -> `query.order_by(Project.created_at.desc()).all()`

#### ProjectService.get_project

Input
- db: Session
- project_id: str

Output Type : `Optional[Project]`

Output
- db.query(Project).filter(Project.id == project_id).first -> `db.query(Project).filter(Project.id == project_id).first()`

#### ProjectService.create_project

Input
- db: Session
- payload: ProjectCreateSchema

Output Type : `Project`

Output
- proj -> `proj`

#### ProjectService.update_project

Input
- db: Session
- project_id: str
- payload: ProjectUpdateSchema

Output Type : `Optional[Project]`

Output
- proj -> `proj`
- expression -> `None`

#### ProjectService.delete_project

Input
- db: Session
- project_id: str

Output Type : `bool`

Output
- expression -> `True`
- expression -> `False`


## Services/storage_services.py

### Class `StorageService`

#### StorageService.save_upload_file

Input
- upload_file: UploadFile
- subfolder: str

Output Type : `str`

Output
- file_path -> `file_path`


## Services/workspace_services.py

### Class `WorkspaceService`

#### WorkspaceService.list_workspaces

Input
- db: Session

Output Type : `List[Workspace]`

Output
- db.query(Workspace).order_by(Workspace.created_at.desc()).all -> `db.query(Workspace).order_by(Workspace.created_at.desc()).all()`

#### WorkspaceService.get_workspace

Input
- db: Session
- workspace_id: str

Output Type : `Optional[Workspace]`

Output
- db.query(Workspace).filter(Workspace.id == workspace_id).first -> `db.query(Workspace).filter(Workspace.id == workspace_id).first()`

#### WorkspaceService.create_workspace

Input
- db: Session
- payload: WorkspaceCreateSchema

Output Type : `Workspace`

Output
- ws -> `ws`

#### WorkspaceService.update_workspace

Input
- db: Session
- workspace_id: str
- payload: WorkspaceUpdateSchema

Output Type : `Optional[Workspace]`

Output
- ws -> `ws`
- expression -> `None`

#### WorkspaceService.delete_workspace

Input
- db: Session
- workspace_id: str

Output Type : `bool`

Output
- expression -> `True`
- expression -> `False`


## Tests/evaluation_methodology.py

#### code

Input
- node: Any

Output Type : `Unknown`

Output
- ast.unparse -> `ast.unparse(node)`
- expression -> `'<unknown>'`

#### get_doc

Input
- node: Any

Output Type : `Unknown`

Output
- expression -> `ast.get_docstring(node) or ''`

#### collect_returns

Input
- fn: Any

Output Type : `Unknown`

Output
- list -> `list(dict.fromkeys(vals))`

#### collect_calls

Input
- fn: Any

Output Type : `Unknown`

Output
- list -> `list(dict.fromkeys(calls))`

#### collect_formulas

Input
- fn: Any

Output Type : `Unknown`

Output
- formulas -> `formulas`

### Class `EvaluationVisitor`

#### EvaluationVisitor.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvaluationVisitor.visit_ClassDef

Input
- self: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### EvaluationVisitor.visit_FunctionDef

Input
- self: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Tests/file_struct.py

#### generate_tree

Input
- path: Any
- prefix: Any

Output Type : `Unknown`

Output
- lines -> `lines`

#### main

Input
- None

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Tests/methods_info.py

#### src

Input
- node: Any

Output Type : `Unknown`

Output
- ast.unparse -> `ast.unparse(node)`
- expression -> `'<unknown>'`

#### fmt_args

Input
- fn: Any

Output Type : `Unknown`

Output
- expression -> `args or ['None']`

#### outputs

Input
- fn: Any

Output Type : `Unknown`

Output
- final -> `final`

#### schema_fields

Input
- cls: Any

Output Type : `Unknown`

Output
- fields -> `fields`

### Class `Visitor`

#### Visitor.__init__

Input
- self: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### Visitor.visit_ClassDef

Input
- self: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### Visitor.visit_FunctionDef

Input
- self: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### Visitor.visit_AsyncFunctionDef

Input
- self: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### Visitor.func

Input
- self: Any
- node: Any
- async_: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Tests/Models/test.py

*No classes or methods.*

## Tests/Models/test_griffin.py

#### serialize

Input
- obj: Any

Output Type : `Unknown`

Output
- obj -> `obj`
- obj.model_dump -> `obj.model_dump()`
- obj.dict -> `obj.dict()`

#### test_griffin_core

Input
- None

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Tests/Models/test_griffin_core.py

#### mock_heem_tree

Input
- None

Output Type : `Unknown`

Output
- dict -> `{'roots': [{'id': 100, 'type': 'COURSE', 'text': 'Database Systems', 'page': 1, 'children': [{'id': 101, 'type': 'METADATA', 'text': 'Course Code: CS301', 'page': 1, 'children': []}, {'id': 102, 'type': 'OBJECTIVE', 'text': 'Understand RDBMS concepts', 'page': 1, 'children': []}, {'id': 103, 'type': 'CO', 'text': 'CO1: Design Relational Schemas', 'page': 2, 'children': []}, {'id': 104, 'type': 'PO', 'text': 'PO1: Engineering Knowledge', 'page': 2, 'children': []}, {'id': 105, 'type': 'PSO', 'text': 'PSO1: Data Science Expertise', 'page': 2, 'children': []}, {'id': 1, 'type': 'UNIT', 'text': 'Unit 1: Relational Model', 'page': 3, 'children': [{'id': 2, 'type': 'TOPIC', 'text': 'Relational Algebra and SQL', 'page': 3, 'children': []}, {'id': 106, 'type': 'PRACTICAL', 'text': 'Lab 1', 'page': 4, 'children': []}, {'id': 107, 'type': 'PEDAGOGY', 'text': 'Slides', 'page': 4, 'children': []}, {'id': 108, 'type': 'RESOURCE', 'text': 'Silberschatz', 'page': 4, 'children': []}, {'id': 109, 'type': 'ASSESSMENT', 'text': 'Mid-term', 'page': 5, 'children': []}]}]}]}`

#### sample_report_pages

Input
- None

Output Type : `Unknown`

Output
- list -> `[{'blocks': [{'text': 'Relational algebra provides the mathematical foundation of SQL.'}]}]`

#### test_pipeline_execution_and_node_filtering

Input
- mock_curriculum_cls: Any
- mock_metadata_cls: Any
- mock_doc_parser_cls: Any
- mock_report_encoder_cls: Any
- mock_topic_encoder_cls: Any
- mock_retriever_cls: Any
- mock_validator_cls: Any
- mock_graph_builder_cls: Any
- mock_heem_tree: Any
- sample_report_pages: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`


## Tests/Models/test_tokenizer_pipeline.py

#### serialize

Input
- obj: Any

Output Type : `Unknown`

Output
- obj -> `obj`
- obj.model_dump -> `obj.model_dump()`
- obj.dict -> `obj.dict()`

#### save_json

Input
- path: Path
- data: dict

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### summarize_metadata

Input
- metadata: Any

Output Type : `Unknown`

Output
- None -> `None`

#### summarize_input_tokens

Input
- tokens: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### summarize_evidence_tokens

Input
- tokens: Any

Output Type : `Unknown`

Output
- None -> `None`

#### print_summary

Input
- result: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### main

Input
- None

Output Type : `Unknown`

Output
- None -> `None`


## Tokenizers/knowledge_tokenizer.py

*No classes or methods.*

## Tokenizers/pdf_tokenizer.py

*No classes or methods.*

## Tokenizers/report_tokenizer.py

### Class `GriffinReportTokenizer`

#### GriffinReportTokenizer.tokenize

Input
- self: Any
- path: Any

Output Type : `Unknown`

Output
- GriffinDocument -> `GriffinDocument(version='1.0', metadata=metadata, statistics=self._build_statistics(metadata, input_tokens, griffin_tokens), input_tokens=input_tokens, tokens=griffin_tokens)`


## Utils/file_handler.py

*No classes or methods.*

## Visualise/griffin_core_knowledge_visualiser.py

*No classes or methods.*

## Visualise/knowledge_visualisation.py

#### shorten

Input
- text: Any
- limit: Any

Output Type : `Unknown`

Output
- expression -> `text[:limit - 3] + '...'`
- text -> `text`

#### add_visual_node

Input
- net: Any
- node: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

#### traverse

Input
- node: Any
- parent: Any

Output Type : `Unknown`

Output
- None -> `No explicit return`

