from typing import Any, Dict, List, Union

from backend.EvidenceModel.encoders.report_encoder import ReportEncoder
from backend.EvidenceModel.encoders.topic_encoder import TopicEncoder
from backend.EvidenceModel.report_tokenizer import GriffinReportTokenizer
from backend.EvidenceModel.retrieval.evidence_retriever import EvidenceRetriever
from backend.EvidenceModel.validation.evidence_validator import EvidenceValidator
from backend.KnowledgeBase.knowledge_evidence import CurriculumEvidenceExtractor
from backend.Schemas.schemas import EvidenceGraph
from backend.graph.evidence_graph import EvidenceGraphBuilder


class GriffinCore:
    """Griffin Core v1.0 evaluation pipeline."""

    def __init__(self):
        self.curriculum_extractor = CurriculumEvidenceExtractor()
        self.report_tokenizer = GriffinReportTokenizer()
        self.topic_encoder = TopicEncoder()
        self.report_encoder = ReportEncoder()
        self.retriever = EvidenceRetriever(top_k=3)
        self.validator = EvidenceValidator()
        self.graph_builder = EvidenceGraphBuilder()

    def process(
        self,
        curriculum_pdf_path: str,
        report_input: Union[str, List[Dict[str, Any]]],
        on_stage_update=None,
        curriculum_schema: Dict[str, Any] | None = None,
    ) -> EvidenceGraph:
        if on_stage_update:
            on_stage_update("Stage 1: Loading normalized curriculum structure...", 10.0)

        if curriculum_schema and curriculum_schema.get("roots"):
            heem_tree = curriculum_schema
        else:
            heem_tree = self.curriculum_extractor.parse_pdf(curriculum_pdf_path)

        if on_stage_update:
            on_stage_update("Stage 1: Generating high-dimensional topic embeddings...", 25.0)

        encoded_topics = self.topic_encoder.encode(heem_tree)

        if on_stage_update:
            on_stage_update("Stage 2: Tokenizing report text blocks and sections...", 35.0)

        report = self.report_tokenizer.tokenize(report_input)

        if on_stage_update:
            on_stage_update("Stage 2: Structuring curriculum-aware report tokens...", 50.0)

        encoded_tokens = self.report_encoder.encode(report.tokens)

        if on_stage_update:
            on_stage_update("Stage 3: Running vector semantic retrieval for candidate mapping...", 65.0)

        candidates = self.retriever.retrieve(
            encoded_topics=encoded_topics,
            encoded_tokens=encoded_tokens,
        )

        if on_stage_update:
            on_stage_update("Stage 4: Executing evidence validation on candidate mappings...", 80.0)

        token_map = {token.token_id: token for token in encoded_tokens}
        topic_map = {topic["id"]: topic for topic in encoded_topics}
        validated = []

        for candidate in candidates:
            token = token_map.get(candidate.token_id)
            if token is None:
                continue

            topic = topic_map.get(candidate.topic_id)
            if topic is None:
                continue

            evidence = self.validator.validate(
                topic_text=topic["text"],
                token=token,
                similarity_score=candidate.similarity_score,
            )
            evidence.topic_id = candidate.topic_id
            validated.append(evidence)

        if on_stage_update:
            on_stage_update("Stage 5: Generating curriculum evidence coverage graph...", 95.0)

        units = [node for node in encoded_topics if node["type"] == "UNIT"]
        topics = [node for node in encoded_topics if node["type"] == "TOPIC"]

        graph = self.graph_builder.build(
            units=units,
            topics=topics,
            validated_evidences=validated,
            evidence_tokens=encoded_tokens,
        )

        if on_stage_update:
            on_stage_update("Evaluation complete. Organizing result graph.", 100.0)

        return graph
