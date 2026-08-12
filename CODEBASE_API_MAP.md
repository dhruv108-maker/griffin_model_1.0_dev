# Codebase Frontend / Backend API Map

Generated automatically for frontend/backend integration analysis.

# 1. Project Structure

- Project root: `C:\Users\Dhruv Verma\Desktop\code_playground\griffin-model-1.0`
- Frontend: `C:\Users\Dhruv Verma\Desktop\code_playground\griffin-model-1.0\src`
- Backend: `C:\Users\Dhruv Verma\Desktop\code_playground\griffin-model-1.0\backend`

# 2. Backend

## `backend\config.py`

## `backend\main.py`

### Functions

- `root()` (line 72)

### API Routes

- `GET /` (line 71)

## `backend\__init__.py`

## `backend\compute\cpu.py`

### Functions

- `submit(task)` (line 6)

## `backend\compute\device.py`

### Classes

- `Device` (line 3)

## `backend\compute\executor.py`

### Classes

- `ComputeExecutor` (line 5)

### Functions

- `__init__(self)` (line 7)
- `execute(self, task)` (line 10)

## `backend\compute\gpu.py`

### Functions

- `submit(task)` (line 1)

## `backend\compute\runner.py`

## `backend\compute\scheduler.py`

### Classes

- `Scheduler` (line 5)

### Functions

- `run(self, task)` (line 7)

## `backend\compute\task.py`

### Classes

- `ComputeTask` (line 6)

### Functions

- `__post_init__(self)` (line 13)

## `backend\Database\database.py`

## `backend\Database\models.py`

### Classes

- `TimestampMixin` (line 11)
- `JobStatus` (line 15)
- `Workspace` (line 21)
- `Project` (line 33)
- `Curriculum` (line 47)
- `Report` (line 59)
- `Evaluation` (line 72)
- `BatchJob` (line 86)
- `GeneratedReport` (line 99)
- `Chat` (line 110)
- `Message` (line 121)

### Functions

- `generate_uuid()` (line 8)

## `backend\Dependencies\database_dep.py`

### Functions

- `get_db()` (line 11)

## `backend\EvidenceModel\EvidenceExtractor.py`

### Classes

- `CurriculumEvidenceExtractor` (line 8)

### Functions

- `__init__(self)` (line 13)
- `_next_id(self)` (line 17)
- `_create_node(self, node_type, text, page, confidence, attributes)` (line 22)
- `_clean_layout_artifacts(self, text)` (line 36)
- `_is_noise(self, line)` (line 44)
- `_parse_attributes_and_cos(self, raw_text)` (line 54)
- `_extract_metadata(self, line, course_node)` (line 85)
- `parse_pdf(self, pdf_path)` (line 102)

## `backend\EvidenceModel\model.py`

## `backend\EvidenceModel\pipeline.py`

### Classes

- `GriffinCore` (line 13)

### Functions

- `__init__(self)` (line 51)
- `process(self, curriculum_pdf_path, report_input)` (line 70)

### API Routes

- `GET dynamic` (line 127)
- `GET dynamic` (line 132)

## `backend\EvidenceModel\Transformers.py`

### Classes

- `EvidenceTransformer` (line 6)

### Functions

- `__init__(self)` (line 11)
- `transform(self, tree)` (line 14)
- `_canonicalize_roots(self, roots)` (line 36)
- `_process_node(self, node)` (line 52)
- `_reindex_node(self, node)` (line 83)

### API Routes

- `GET children` (line 87)
- `GET children` (line 54)
- `GET children` (line 46)

## `backend\EvidenceModel\encoders\report_encoder.py`

### Classes

- `ReportEncoder` (line 10)

### Functions

- `__init__(self, model_name, device)` (line 32)
- `encode(self, tokens, batch_size)` (line 46)
- `_mean_pooling(token_embeddings, attention_mask)` (line 108)

## `backend\EvidenceModel\encoders\topic_encoder.py`

### Classes

- `TopicEncoder` (line 7)

### Functions

- `__init__(self, model_name, device)` (line 11)
- `extract_filtered_topics(self, heem_tree)` (line 21)
- `encode(self, heem_tree)` (line 44)
- `recurse(nodes)` (line 24)

### API Routes

- `GET roots` (line 41)
- `GET type` (line 26)
- `GET page` (line 34)

## `backend\EvidenceModel\evaluation\benchmark_runner.py`

### Classes

- `BenchmarkRunner` (line 11)

### Functions

- `__init__(self, benchmark_config_path)` (line 16)
- `run_benchmark(self, experiment_name, griffin_pipeline)` (line 23)
- `save_results(self, eval_result, output_path)` (line 75)

## `backend\EvidenceModel\evaluation\evaluator.py`

### Classes

- `EvaluationResult` (line 14)
- `Evaluator` (line 22)

### Functions

- `evaluate(self, experiment_name, graph, all_topic_ids, retrieval_candidates, retrieval_ground_truth, validator_ground_truth, runtime_result)` (line 28)

## `backend\EvidenceModel\evaluation\graph_metrics.py`

### Classes

- `GraphMetricsResult` (line 8)

### Functions

- `calculate_graph_metrics(graph, all_topic_ids, ground_truth_map)` (line 16)

### API Routes

- `GET dynamic` (line 48)
- `GET dynamic` (line 60)

## `backend\EvidenceModel\evaluation\report_generator.py`

### Classes

- `EvaluationReportData` (line 12)
- `EvaluationReportGenerator` (line 20)

### Functions

- `__init__(self, data)` (line 23)
- `to_dict(self)` (line 26)
- `to_json(self, indent)` (line 29)
- `render_console_report(self)` (line 32)

### API Routes

- `GET 1` (line 84)

## `backend\EvidenceModel\evaluation\retrieval_metrics.py`

### Classes

- `RetrievalMetricsResult` (line 8)

### Functions

- `precision_at_k(retrieved, ground_truth, k)` (line 15)
- `recall_at_k(retrieved, ground_truth, k)` (line 26)
- `mean_reciprocal_rank(all_retrieved, all_ground_truth)` (line 35)
- `ndcg_at_k(retrieved, ground_truth, k)` (line 52)
- `calculate_retrieval_metrics(retrieved_map, ground_truth_map, k_list)` (line 75)

### API Routes

- `GET dynamic` (line 91)

## `backend\EvidenceModel\evaluation\runtime_metrics.py`

### Classes

- `RuntimeMetricsResult` (line 10)
- `RuntimeTracker` (line 19)

### Functions

- `__init__(self)` (line 40)
- `start(self)` (line 46)
- `start_stage(self, stage_name)` (line 64)
- `stop_stage(self, stage_name)` (line 72)
- `stop(self)` (line 86)

### API Routes

- `GET dynamic` (line 81)

## `backend\EvidenceModel\evaluation\validator_metrics.py`

### Classes

- `ValidatorMetricsResult` (line 8)

### Functions

- `calculate_validator_metrics(y_true, y_pred, y_prob)` (line 16)
- `_compute_roc_auc(y_true, y_prob)` (line 51)

## `backend\EvidenceModel\evaluation\__init__.py`

## `backend\EvidenceModel\experiments\compare_baselines.py`

### Functions

- `run_baseline_comparison()` (line 21)

## `backend\EvidenceModel\experiments\experiment_01.py`

### Functions

- `run_experiment()` (line 70)
- `main()` (line 113)

## `backend\EvidenceModel\experiments\experiment_02.py`

### Functions

- `run_experiment_02()` (line 15)

## `backend\EvidenceModel\parsers\document_parser.py`

### Classes

- `DocumentStructureParser` (line 14)

### Functions

- `parse(self, pdf_pages, metadata)` (line 44)
- `_is_heading(text)` (line 171)
- `_heading_level(text)` (line 191)

### API Routes

- `GET blocks` (line 64)
- `GET bbox` (line 74)
- `GET text` (line 66)

## `backend\EvidenceModel\parsers\metadata_extractor.py`

### Classes

- `ReportMetadataExtractor` (line 5)

### Functions

- `__init__(self, model_name_or_path)` (line 6)
- `extract(self, cover_page_image, raw_tokens, bbox)` (line 11)

## `backend\EvidenceModel\presentation\builder.py`

### Classes

- `GriffinResultBuilder` (line 26)

### Functions

- `__init__(self, confidence_threshold)` (line 29)
- `build(self, evidence_graph, metadata)` (line 32)
- `_build_visualizations(self, units, topics, page_density, units_map, topics_map)` (line 293)

### API Routes

- `GET nodes` (line 40)
- `GET edges` (line 41)
- `GET attributes` (line 50)
- `GET source` (line 75)
- `GET target` (line 76)
- `GET attributes` (line 77)
- `GET similarity` (line 85)
- `GET validation_score` (line 86)
- `GET dynamic` (line 192)
- `GET label` (line 54)
- `GET node_type` (line 49)
- `GET label` (line 60)
- `GET unit_id` (line 61)
- `GET title` (line 272)
- `GET student` (line 273)
- `GET university` (line 274)
- `GET total_pages` (line 275)
- `GET processing_time` (line 276)
- `GET page_number` (line 67)
- `GET heading` (line 68)
- `GET similarity` (line 69)
- `GET validation_score` (line 70)

## `backend\EvidenceModel\presentation\exporter.py`

### Functions

- `export_griffin_result(evidence_graph, metadata, output_path)` (line 10)

## `backend\EvidenceModel\presentation\schema.py`

### Classes

- `ReportMetadata` (line 10)
- `OverallSummary` (line 19)
- `UnitMappingDetail` (line 31)
- `TopicMappingDetail` (line 42)
- `EvidenceDetail` (line 54)
- `EvidenceAnalysis` (line 63)
- `CoverageAnalysis` (line 70)
- `DepthAndSignificance` (line 76)
- `GraphStatistics` (line 86)
- `VisualizationPayload` (line 96)
- `GriffinResult` (line 105)

## `backend\EvidenceModel\report_tokenizer\duplicate_detector.py`

### Classes

- `DuplicateDetector` (line 14)

### Functions

- `__init__(self, hamming_threshold)` (line 17)
- `is_duplicate(self, text)` (line 21)
- `filter_margin_duplicates(self, margin_blocks)` (line 34)
- `_hamming_distance(hex1, hex2)` (line 51)

### API Routes

- `GET dynamic` (line 39)
- `GET dynamic` (line 45)

## `backend\EvidenceModel\report_tokenizer\evidence_builder.py`

### Classes

- `EvidenceBuilder` (line 27)

### Functions

- `build_evidence_tokens(self, sections)` (line 30)
- `_extract_concepts(self, text)` (line 102)
- `_extract_entities(self, text)` (line 111)
- `_extract_keywords(self, text)` (line 126)
- `_infer_category(self, section)` (line 150)

## `backend\EvidenceModel\report_tokenizer\evidence_ranker.py`

### Classes

- `EvidenceRanker` (line 39)

### Functions

- `rank_and_score_tokens(self, tokens)` (line 45)
- `_calculate_technical_density(self, token)` (line 66)
- `_calculate_semantic_density(self, token)` (line 93)
- `_calculate_information_gain(self, token, technical_density, semantic_density)` (line 133)

### API Routes

- `GET dynamic` (line 140)

## `backend\EvidenceModel\report_tokenizer\layout_analyzer.py`

### Classes

- `LayoutAnalyzer` (line 13)

### Functions

- `__init__(self, header_margin_ratio, footer_margin_ratio)` (line 16)
- `analyze_page_layout(self, page)` (line 20)
- `detect_heading_level(self, block, mean_font_size)` (line 39)

## `backend\EvidenceModel\report_tokenizer\metadata_extractor.py`

### Classes

- `MetadataExtractor` (line 20)

### Functions

- `extract_metadata(self, pages)` (line 30)
- `_extract_title(self, blocks)` (line 130)
- `_extract_regex(self, text, pattern)` (line 148)
- `_extract_field(self, text, labels)` (line 165)

## `backend\EvidenceModel\report_tokenizer\model.py`

### Classes

- `PipelineStage` (line 44)
- `GriffinTokenizerPipeline` (line 51)

### Functions

- `print_pipeline(cls)` (line 100)

## `backend\EvidenceModel\report_tokenizer\parser.py`

### Classes

- `StructuralParser` (line 22)

### Functions

- `__init__(self)` (line 25)
- `parse_pdf(self, pdf_input)` (line 29)
- `_build_structural_sections(self, pages)` (line 81)

### API Routes

- `GET lines` (line 46)
- `GET type` (line 43)
- `GET spans` (line 47)
- `GET flags` (line 61)
- `GET text` (line 48)
- `GET font` (line 68)
- `GET size` (line 69)
- `GET font` (line 62)
- `GET font` (line 63)

## `backend\EvidenceModel\report_tokenizer\schemas.py`

### Classes

- `SectionType` (line 14)
- `LayoutBoundingBox` (line 42)
- `TextBlock` (line 52)
- `RawPage` (line 64)
- `ReportMetadata` (line 72)
- `ParsedSection` (line 89)
- `EvidenceToken` (line 101)
- `StructuredReportDocument` (line 124)

## `backend\EvidenceModel\report_tokenizer\section_classifier.py`

### Classes

- `SectionClassifier` (line 28)

### Functions

- `classify_heading(self, heading_text)` (line 56)
- `is_administrative_noise(self, section_type)` (line 64)

## `backend\EvidenceModel\report_tokenizer\tokenizer.py`

### Classes

- `GriffinReportTokenizer` (line 50)

### Functions

- `__init__(self)` (line 55)
- `tokenize(self, pdf_input)` (line 63)

### API Routes

- `GET lines` (line 95)
- `GET type` (line 92)
- `GET spans` (line 97)
- `GET text` (line 101)
- `GET font` (line 110)
- `GET size` (line 111)
- `GET font` (line 113)
- `GET font` (line 115)

## `backend\EvidenceModel\report_tokenizer\utils.py`

### Functions

- `calculate_shannon_entropy(text)` (line 31)
- `extract_formulas(text)` (line 48)
- `extract_figure_and_table_refs(text)` (line 64)
- `extract_academic_citations(text)` (line 74)
- `compute_simhash_signature(text)` (line 87)

### API Routes

- `GET dynamic` (line 39)

## `backend\EvidenceModel\report_tokenizer\__init__.py`

## `backend\EvidenceModel\retrieval\evidence_retriever.py`

### Classes

- `EvidenceRetriever` (line 11)

### Functions

- `__init__(self, top_k)` (line 24)
- `retrieve(self, encoded_topics, encoded_tokens)` (line 27)

### API Routes

- `GET embedding` (line 43)

## `backend\EvidenceModel\validation\evidence_validator.py`

### Classes

- `EvidenceValidator` (line 14)

### Functions

- `__init__(self, model_name, device)` (line 32)
- `validate(self, topic_text, token, similarity_score)` (line 51)

## `backend\graph\evidence_graph.py`

### Classes

- `EvidenceGraphBuilder` (line 12)

### Functions

- `__init__(self)` (line 27)
- `build(self, units, topics, validated_evidences, evidence_tokens)` (line 30)

### API Routes

- `GET dynamic` (line 89)
- `GET type` (line 59)
- `GET type` (line 78)

## `backend\KnowledgeBase\knowledge_evidence.py`

### Classes

- `EvidenceTransformer` (line 6)
- `CurriculumEvidenceExtractor` (line 91)

### Functions

- `__init__(self)` (line 11)
- `transform(self, tree)` (line 14)
- `_canonicalize_roots(self, roots)` (line 36)
- `_process_node(self, node)` (line 52)
- `_reindex_node(self, node)` (line 83)
- `__init__(self)` (line 96)
- `_next_id(self)` (line 100)
- `_create_node(self, node_type, text, page, confidence, attributes)` (line 105)
- `_clean_layout_artifacts(self, text)` (line 119)
- `_is_noise(self, line)` (line 127)
- `_parse_attributes_and_cos(self, raw_text)` (line 137)
- `_extract_metadata(self, line, course_node)` (line 168)
- `parse_pdf(self, pdf_path)` (line 185)

### API Routes

- `GET children` (line 87)
- `GET children` (line 54)
- `GET children` (line 46)

## `backend\KnowledgeBase\model.py`

## `backend\llm\config.py`

## `backend\llm\prompts.py`

## `backend\llm\__init__.py`

## `backend\llm\Client\ollama_client.py`

### Classes

- `OllamaClient` (line 6)

### Functions

- `__init__(self, model)` (line 7)
- `chat(self, messages, temperature)` (line 10)

## `backend\llm\Client\__init__.py`

## `backend\llm\Services\chat_service.py`

### Functions

- `chat(message, history, system_prompt)` (line 8)

## `backend\llm\Services\__init__.py`

## `backend\rl\agent.py`

### Classes

- `ActorCritic` (line 55)

### Functions

- `__init__(self, state_dim, action_dim)` (line 57)
- `forward(self, state)` (line 154)

## `backend\rl\environment.py`

### Classes

- `GriffinSearchEnv` (line 5)

### Functions

- `__init__(self, topics, paragraphs)` (line 13)
- `reset(self, seed, options)` (line 25)
- `_get_obs(self)` (line 32)
- `step(self, action)` (line 39)

## `backend\Routes\chat.py`

### Functions

- `send_chat_message(chat_id, content, db)` (line 9)

### API Routes

- `POST /message` (line 8)

## `backend\Routes\evaluation.py`

### Functions

- `start_evaluation(payload, background_tasks, db)` (line 13)
- `get_job_status(evaluation_id, db)` (line 33)
- `get_evaluation_result(evaluation_id, db)` (line 40)

### API Routes

- `POST /run` (line 12)
- `GET /{evaluation_id}/status` (line 32)
- `GET /{evaluation_id}/result` (line 39)

## `backend\Routes\health.py`

### Functions

- `check_health(db)` (line 9)

### API Routes

- `GET ` (line 8)

## `backend\Routes\history.py`

### Functions

- `get_evaluation_history(project_id, db)` (line 9)

### API Routes

- `GET ` (line 8)

## `backend\Routes\projects.py`

### Functions

- `list_projects(workspace_id, db)` (line 9)

### API Routes

- `GET ` (line 8)

## `backend\Routes\reports.py`

### Functions

- `upload_report(project_id, student_name, file, db)` (line 9)

### API Routes

- `POST /upload` (line 8)

## `backend\Routes\settings.py`

### Functions

- `get_system_settings()` (line 6)

### API Routes

- `GET ` (line 5)

## `backend\Routes\workspace.py`

### Functions

- `workspaces(db)` (line 9)
- `create_workspace(name, description, db)` (line 13)

### API Routes

- `GET ` (line 8)
- `POST ` (line 12)

## `backend\Schemas\chat.py`

### Classes

- `MessageCreateSchema` (line 11)
- `MessageResponseSchema` (line 16)
- `ChatCreateSchema` (line 26)
- `ChatResponseSchema` (line 32)
- `ChatDetailResponseSchema` (line 43)

## `backend\Schemas\common.py`

### Classes

- `APIResponse` (line 12)
- `StatusResponse` (line 19)
- `PaginationParams` (line 25)
- `PaginatedResponse` (line 31)

## `backend\Schemas\curriculum.py`

### Classes

- `CurriculumCreateSchema` (line 11)
- `CurriculumResponseSchema` (line 16)

## `backend\Schemas\evaluation.py`

### Classes

- `EvaluationCreateSchema` (line 6)
- `BatchJobResponseSchema` (line 12)
- `EvaluationResponseSchema` (line 23)
- `GriffinResultResponseSchema` (line 33)

## `backend\Schemas\projects.py`

### Classes

- `ProjectCreateSchema` (line 11)
- `ProjectUpdateSchema` (line 17)
- `ProjectResponseSchema` (line 22)
- `ProjectDetailResponseSchema` (line 33)

## `backend\Schemas\report.py`

### Classes

- `ReportCreateSchema` (line 11)
- `ReportUpdateSchema` (line 17)
- `ReportResponseSchema` (line 22)

## `backend\Schemas\schemas.py`

### Classes

- `CurriculumNodeType` (line 51)
- `HEEMNode` (line 59)
- `ReportMetadata` (line 87)
- `InputTokenType` (line 121)
- `InputToken` (line 130)
- `EvidenceToken` (line 160)
- `GriffinStatistics` (line 243)
- `GriffinDocument` (line 263)
- `CandidateEvidence` (line 287)
- `ValidatedEvidence` (line 299)
- `GraphNode` (line 323)
- `GraphEdge` (line 337)
- `EvidenceGraph` (line 355)
- `EvidenceNode` (line 406)
- `EvidenceEdge` (line 417)
- `ValidatedEvidence` (line 426)
- `Topic` (line 436)
- `Unit` (line 443)
- `EvidenceGraph` (line 450)
- `GriffinResult` (line 461)

### Functions

- `add_node(self, node)` (line 364)
- `add_edge(self, edge)` (line 367)
- `get_node(self, node_id)` (line 370)
- `get_edges_by_relation(self, relation)` (line 373)

### API Routes

- `GET dynamic` (line 371)

## `backend\Schemas\settings.py`

### Classes

- `SettingsUpdateSchema` (line 10)
- `SettingsResponseSchema` (line 22)

## `backend\Schemas\workspace.py`

### Classes

- `WorkspaceCreateSchema` (line 11)
- `WorkspaceUpdateSchema` (line 16)
- `WorkspaceResponseSchema` (line 21)
- `WorkspaceDetailResponseSchema` (line 32)

## `backend\Schemas\__init__.py`

## `backend\Services\evaluation_service.py`

### Classes

- `EvaluationService` (line 8)

### Functions

- `create_evaluation(db, project_id, curriculum_id, name)` (line 11)
- `run_async_evaluation(db, evaluation_id, report_ids)` (line 24)

## `backend\Services\griffin_services.py`

### Classes

- `GriffinService` (line 4)

### Functions

- `process_report(report_file_path, curriculum_file_path, metadata)` (line 8)

### API Routes

- `GET title` (line 29)
- `GET student_name` (line 30)
- `GET total_pages` (line 32)

## `backend\Services\project_services.py`

### Classes

- `ProjectService` (line 12)

### Functions

- `list_projects(db, workspace_id)` (line 15)
- `get_project(db, project_id)` (line 22)
- `create_project(db, payload)` (line 26)
- `update_project(db, project_id, payload)` (line 38)
- `delete_project(db, project_id)` (line 53)

### API Routes

- `DELETE dynamic` (line 57)

## `backend\Services\storage_services.py`

### Classes

- `StorageService` (line 13)

### Functions

- `save_upload_file(upload_file, subfolder)` (line 16)

## `backend\Services\workspace_services.py`

### Classes

- `WorkspaceService` (line 12)

### Functions

- `list_workspaces(db)` (line 15)
- `get_workspace(db, workspace_id)` (line 19)
- `create_workspace(db, payload)` (line 23)
- `update_workspace(db, workspace_id, payload)` (line 34)
- `delete_workspace(db, workspace_id)` (line 49)

### API Routes

- `DELETE dynamic` (line 53)

## `backend\Tests\code_base_api.py`

### Functions

- `should_ignore(path)` (line 32)
- `read_file(path)` (line 36)
- `analyze_python_file(path)` (line 47)
- `scan_backend()` (line 128)
- `analyze_frontend_file(path)` (line 154)
- `scan_frontend()` (line 214)
- `generate_markdown(frontend, backend)` (line 253)
- `main()` (line 511)

## `backend\Tests\evaluation_methodology.py`

### Classes

- `EvaluationVisitor` (line 71)

### Functions

- `code(node)` (line 15)
- `get_doc(node)` (line 22)
- `collect_returns(fn)` (line 26)
- `collect_calls(fn)` (line 36)
- `collect_formulas(fn)` (line 49)
- `__init__(self)` (line 73)
- `visit_ClassDef(self, node)` (line 77)
- `visit_FunctionDef(self, node)` (line 92)

## `backend\Tests\file_struct.py`

### Functions

- `generate_tree(path, prefix)` (line 27)
- `main()` (line 58)

## `backend\Tests\methods_info.py`

### Classes

- `Visitor` (line 126)

### Functions

- `src(node)` (line 18)
- `fmt_args(fn)` (line 25)
- `outputs(fn)` (line 45)
- `schema_fields(cls)` (line 101)
- `__init__(self)` (line 128)
- `visit_ClassDef(self, node)` (line 132)
- `visit_FunctionDef(self, node)` (line 153)
- `visit_AsyncFunctionDef(self, node)` (line 156)
- `func(self, node, async_)` (line 159)

## `backend\Tests\Models\test.py`

## `backend\Tests\Models\test_griffin.py`

### Functions

- `serialize(obj)` (line 89)
- `test_griffin_core()` (line 104)

## `backend\Tests\Models\test_griffin_core.py`

### Functions

- `mock_heem_tree()` (line 8)
- `sample_report_pages()` (line 102)
- `test_pipeline_execution_and_node_filtering(mock_curriculum_cls, mock_metadata_cls, mock_doc_parser_cls, mock_report_encoder_cls, mock_topic_encoder_cls, mock_retriever_cls, mock_validator_cls, mock_graph_builder_cls, mock_heem_tree, sample_report_pages)` (line 122)

## `backend\Tests\Models\test_tokenizer_pipeline.py`

### Functions

- `serialize(obj)` (line 73)
- `save_json(path, data)` (line 85)
- `summarize_metadata(metadata)` (line 96)
- `summarize_input_tokens(tokens)` (line 108)
- `summarize_evidence_tokens(tokens)` (line 123)
- `print_summary(result)` (line 152)
- `main()` (line 179)

## `backend\Tokenizers\knowledge_tokenizer.py`

## `backend\Tokenizers\pdf_tokenizer.py`

## `backend\Tokenizers\report_tokenizer.py`

### Classes

- `GriffinReportTokenizer` (line 1)

### Functions

- `tokenize(self, path)` (line 3)

## `backend\Utils\file_handler.py`

## `backend\Visualise\griffin_core_knowledge_visualiser.py`

### API Routes

- `GET node_type` (line 71)
- `GET label` (line 72)
- `GET dynamic` (line 76)
- `GET dynamic` (line 86)

## `backend\Visualise\knowledge_visualisation.py`

### Functions

- `shorten(text, limit)` (line 35)
- `add_visual_node(net, node)` (line 40)
- `traverse(node, parent)` (line 99)

### API Routes

- `GET text` (line 43)
- `GET dynamic` (line 46)
- `GET dynamic` (line 47)
- `GET children` (line 113)
- `GET type` (line 44)

# 3. Frontend

## `src\App.jsx`

### Functions

- Line 13: `function App() {`

## `src\main.jsx`

## `src\api\apis.js`

### API Calls

- Line 34: `const response = await fetch(`
- Line 41: `const contentType = response.headers.get("content-type");`

## `src\api\griffin.js`

## `src\components\console\AnalysisItem.jsx`

### Functions

- Line 68: `const handleKeyDown = (event) => {`

## `src\components\console\AnalysisList.jsx`

## `src\components\console\GriffinConsole.jsx`

## `src\components\console\Sidebar.jsx`

## `src\components\console\Topbar.jsx`

## `src\components\results\CoveragePanel.jsx`

### Functions

- Line 9: `function TopicGroup({ title, items = [], tone = "neutral", icon: Icon }) {`

## `src\components\results\CurriculumMapping.jsx`

## `src\components\results\EvidencePanel.jsx`

### Functions

- Line 8: `function Score({ label, value }) {`
- Line 24: `function EvidenceCard({`
- Line 85: `function EvidenceList({`

## `src\components\results\GraphPanel.jsx`

### Functions

- Line 8: `function GraphMetric({`
- Line 27: `function VisualizationPreview({`

## `src\components\results\MetricCard.jsx`

## `src\components\results\Overview.jsx`

### Functions

- Line 12: `function formatPercentage(value) {`
- Line 22: `function getNumber(...values) {`

## `src\components\results\ReportPanel.jsx`

### Functions

- Line 11: `function formatValue(value) {`
- Line 35: `function JsonBlock({ value }) {`
- Line 43: `function SummaryRow({ label, value }) {`
- Line 86: `const handleCopy = async () => {`
- Line 101: `const handleDownload = () => {`

## `src\components\results\TopicMapping.jsx`

### Functions

- Line 11: `function normalizeStatus(topic) {`
- Line 56: `function normalizeTopics(mapping) {`
- Line 100: `function StatusIcon({ status }) {`
- Line 136: `function StatusLabel({ status }) {`
- Line 154: `function TopicRow({ topic }) {`
- Line 308: `const filteredTopics = useMemo(() => {`
- Line 349: `const counts = useMemo(() => {`

## `src\components\results\UnitMapping.jsx`

### Functions

- Line 12: `function normalizeStatus(unit) {`
- Line 57: `function normalizeUnits(mapping) {`
- Line 109: `function getTopics(unit) {`
- Line 125: `function getTopicName(topic) {`
- Line 140: `function getTopicStatus(topic) {`
- Line 188: `function StatusIcon({ status }) {`
- Line 224: `function StatusLabel({ status }) {`
- Line 242: `function TopicMiniRow({ topic }) {`
- Line 254: `function UnitCard({ unit }) {`
- Line 427: `const counts = useMemo(() => {`
- Line 446: `const filteredUnits = useMemo(() => {`

## `src\components\upload\AnalysisUpload.jsx`

### Functions

- Line 12: `function formatBytes(bytes) {`
- Line 26: `function FileRow({`
- Line 65: `function UploadZone({`
- Line 87: `const handleDrop = (event) => {`
- Line 96: `const handleChange = (event) => {`
- Line 190: `const validatePdfFiles = (files) => {`
- Line 208: `const handleCurriculumFiles = (files) => {`
- Line 219: `const handleReportFiles = (files) => {`
- Line 258: `const removeCurriculum = () => {`
- Line 263: `const removeReport = (fileToRemove) => {`
- Line 278: `const handleStart = async () => {`

## `src\components\workspace\AnalysisHeader.jsx`

## `src\components\workspace\AnalysisWorkspace.jsx`

### Functions

- Line 217: `const workspaceState = useMemo(() => {`

## `src\components\workspace\EmptyAnalysis.jsx`

## `src\components\workspace\WorkspaceTabs.jsx`

# 4. Frontend ↔ Backend Alignment Review

Claude should use this codebase map to investigate the following:

1. Frontend API calls with no matching backend route.
2. Backend routes that are never called by the frontend.
3. HTTP method mismatches.
4. URL/path mismatches.
5. Parameter name mismatches.
6. Request body mismatches.
7. Response structure mismatches.
8. Authentication/header mismatches.
9. Missing frontend methods.
10. Missing backend methods.
11. Incorrect imports or function names.
12. Potential 401 / 403 / 404 / 422 / 500 causes.
13. Duplicate or conflicting API implementations.
14. Dead or unreferenced endpoints.
15. Frontend/backend architectural inconsistencies.
16. Potential async/sync mismatches.
17. Potential type mismatches.
18. Potential naming inconsistencies.

# 5. Claude Investigation Instructions


Use this document as a codebase map.

IMPORTANT RULES:

- Do not modify business logic.
- Do not rewrite working functionality unnecessarily.
- Do not assume an endpoint is broken only because it cannot
  be statically matched.
- Verify the actual implementation before recommending changes.
- Identify the root cause before suggesting a fix.
- Prefer minimal, targeted fixes.
- Preserve existing API contracts unless a mismatch is confirmed.
- Distinguish confirmed errors from potential issues.
- Do not invent missing endpoints or functions.

For every confirmed or highly probable mismatch, report:

### Issue

- Frontend file:
- Frontend function:
- Frontend line:
- Backend file:
- Backend function/route:
- Backend line:
- HTTP method:
- Endpoint:
- Expected behavior:
- Actual behavior:
- Root cause:
- Recommended fix:
- Confidence:

Classify each issue as:

- CONFIRMED
- LIKELY
- POSSIBLE
- NO ISSUE

Prioritize:

1. Runtime-breaking errors
2. API contract mismatches
3. Authentication problems
4. Request/response schema mismatches
5. Incorrect imports/functions
6. Performance problems
7. Architectural inconsistencies

