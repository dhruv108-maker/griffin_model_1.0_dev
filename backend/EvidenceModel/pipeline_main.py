from backend.KnowledgeBase.knowledge_evidence import CurriculumEvidenceExtractor
from backend.EvidenceModel.encoders.topic_encoder import TopicEncoder
from backend.EvidenceModel.report_tokenizer.tokenizer import GriffinReportTokenizer
from backend.EvidenceModel.encoders.report_encoder import ReportEncoder
from backend.EvidenceModel.retrieval.evidence_retriever import EvidenceRetriever
from backend.EvidenceModel.validation.evidence_validator import EvidenceValidator
from backend.graph.evidence_graph import EvidenceGraphBuilder

class GriffinCore:
    def __init__(self, config=None, progress_callback=None):
        self.config = config or {}
        self.progress_callback = progress_callback

        self.curriculum_extractor = CurriculumEvidenceExtractor()
        self.topic_encoder = TopicEncoder()
        self.report_tokenizer = GriffinReportTokenizer()
        self.report_encoder = ReportEncoder()
        self.retriever = EvidenceRetriever(top_k=3)
        self.validator = EvidenceValidator()
        self.graph_builder = EvidenceGraphBuilder()

    def _progress(self, stage, percent, message=""):
        if self.progress_callback:
            self.progress_callback(stage, percent, message)

    def process(self, curriculum_pdf_path, report_input):
        self._progress("Curriculum Parsing", 10, "Parsing curriculum PDF")
        heem_tree = self.curriculum_extractor.parse_pdf(curriculum_pdf_path)

        self._progress("Topic Encoding", 25, "Encoding curriculum topics")
        encoded_topics = self.topic_encoder.encode(heem_tree)

        self._progress("Report Tokenization", 40, "Tokenizing report PDF")
        report = self.report_tokenizer.tokenize(report_input)

        self._progress("Report Encoding", 55, "Encoding report evidence")
        encoded_tokens = self.report_encoder.encode(report.tokens)

        self._progress("Evidence Retrieval", 70, "Retrieving curriculum evidence")
        candidates = self.retriever.retrieve(
            encoded_topics=encoded_topics,
            encoded_tokens=encoded_tokens
        )

        self._progress("Evidence Validation", 82, "Validating candidate evidence")

        token_map = {token.token_id: token for token in encoded_tokens}
        topic_map = {topic["id"]: topic for topic in encoded_topics}

        validated = []

        for candidate in candidates:
            token = token_map.get(candidate.token_id)
            topic = topic_map.get(candidate.topic_id)

            if token is None or topic is None:
                continue

            evidence = self.validator.validate(
                topic_text=topic["text"],
                token=token,
                similarity_score=candidate.similarity_score
            )

            evidence.topic_id = candidate.topic_id
            validated.append(evidence)

        self._progress("Evidence Graph", 92, "Building EvidenceGraph")

        units = [
            node for node in encoded_topics
            if node["type"] == "UNIT"
        ]

        topics = [
            node for node in encoded_topics
            if node["type"] == "TOPIC"
        ]

        graph = self.graph_builder.build(
            units=units,
            topics=topics,
            validated_evidences=validated,
            evidence_tokens=encoded_tokens
        )

        self._progress("Complete", 100, "Griffin evaluation completed")

        return graph
