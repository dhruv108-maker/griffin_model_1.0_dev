# Project Structure

```text
backend
├── Databases
│   └── Workspace_1
│       ├── Knowledge
│       └── Samples
├── EvidenceModel
│   ├── benchmarks
│   │   └── benchmark.json
│   ├── encoders
│   │   ├── report_encoder.py
│   │   └── topic_encoder.py
│   ├── evaluation
│   │   ├── __init__.py
│   │   ├── benchmark_runner.py
│   │   ├── evaluator.py
│   │   ├── graph_metrics.py
│   │   ├── report_generator.py
│   │   ├── retrieval_metrics.py
│   │   ├── runtime_metrics.py
│   │   └── validator_metrics.py
│   ├── experiments
│   │   ├── results
│   │   │   └── exp_01_results.json
│   │   ├── compare_baselines.py
│   │   ├── experiment_01.py
│   │   └── experiment_02.py
│   ├── parsers
│   │   ├── document_parser.py
│   │   └── metadata_extractor.py
│   ├── presentation
│   │   ├── builder.py
│   │   ├── exporter.py
│   │   └── schema.py
│   ├── report_tokenizer
│   │   ├── __init__.py
│   │   ├── duplicate_detector.py
│   │   ├── evidence_builder.py
│   │   ├── evidence_ranker.py
│   │   ├── layout_analyzer.py
│   │   ├── metadata_extractor.py
│   │   ├── model.py
│   │   ├── parser.py
│   │   ├── schemas.py
│   │   ├── section_classifier.py
│   │   ├── tokenizer.py
│   │   └── utils.py
│   ├── retrieval
│   │   └── evidence_retriever.py
│   ├── validation
│   │   └── evidence_validator.py
│   ├── EvidenceExtractor.py
│   ├── model.py
│   ├── pipeline.py
│   └── Transformers.py
├── graph
│   └── evidence_graph.py
├── KnowledgeBase
│   ├── knowledge_evidence.py
│   └── model.py
├── llm
│   ├── Client
│   │   ├── __init__.py
│   │   └── ollama_client.py
│   ├── Services
│   │   ├── __init__.py
│   │   └── chat_service.py
│   ├── __init__.py
│   ├── config.py
│   └── prompts.py
├── Results
│   └── Evaluation
├── rl
│   ├── Database
│   │   ├── Results
│   │   │   ├── curriculum_evidence_final.json
│   │   │   ├── MajorProjectReport@2026_griffin_tokens.json
│   │   │   └── MajorProjectReport@2026_tokens.json
│   │   └── Samples
│   │       ├── curr_test.pdf
│   │       └── MajorProjectReport@2026.pdf
│   ├── agent.py
│   └── environment.py
├── Routes
├── Schemas
│   ├── __init__.py
│   └── schemas.py
├── Tests
│   ├── Models
│   │   ├── test.py
│   │   ├── test_griffin.py
│   │   ├── test_griffin_core.py
│   │   └── test_tokenizer_pipeline.py
│   ├── Results
│   │   └── griffin_core_result.json
│   └── file_struct.py
├── Tokenizers
│   ├── knowledge_tokenizer.py
│   ├── pdf_tokenizer.py
│   └── report_tokenizer.py
├── Visualise
│   ├── griffin_core_knowledge_visualiser.py
│   └── knowledge_visualisation.py
├── __init__.py
├── config.py
└── mian.py
```
