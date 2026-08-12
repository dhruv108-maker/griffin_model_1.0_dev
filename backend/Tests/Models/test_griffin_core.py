import pytest
from unittest.mock import MagicMock, patch

from backend.EvidenceModel.pipeline import GriffinCore


@pytest.fixture
def mock_heem_tree():
    return {
        "roots": [
            {
                "id": 100,
                "type": "COURSE",
                "text": "Database Systems",
                "page": 1,
                "children": [
                    {
                        "id": 101,
                        "type": "METADATA",
                        "text": "Course Code: CS301",
                        "page": 1,
                        "children": []
                    },
                    {
                        "id": 102,
                        "type": "OBJECTIVE",
                        "text": "Understand RDBMS concepts",
                        "page": 1,
                        "children": []
                    },
                    {
                        "id": 103,
                        "type": "CO",
                        "text": "CO1: Design Relational Schemas",
                        "page": 2,
                        "children": []
                    },
                    {
                        "id": 104,
                        "type": "PO",
                        "text": "PO1: Engineering Knowledge",
                        "page": 2,
                        "children": []
                    },
                    {
                        "id": 105,
                        "type": "PSO",
                        "text": "PSO1: Data Science Expertise",
                        "page": 2,
                        "children": []
                    },
                    {
                        "id": 1,
                        "type": "UNIT",
                        "text": "Unit 1: Relational Model",
                        "page": 3,
                        "children": [
                            {
                                "id": 2,
                                "type": "TOPIC",
                                "text": "Relational Algebra and SQL",
                                "page": 3,
                                "children": []
                            },
                            {
                                "id": 106,
                                "type": "PRACTICAL",
                                "text": "Lab 1",
                                "page": 4,
                                "children": []
                            },
                            {
                                "id": 107,
                                "type": "PEDAGOGY",
                                "text": "Slides",
                                "page": 4,
                                "children": []
                            },
                            {
                                "id": 108,
                                "type": "RESOURCE",
                                "text": "Silberschatz",
                                "page": 4,
                                "children": []
                            },
                            {
                                "id": 109,
                                "type": "ASSESSMENT",
                                "text": "Mid-term",
                                "page": 5,
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_report_pages():
    return [
        {
            "blocks": [
                {
                    "text": "Relational algebra provides the mathematical foundation of SQL."
                }
            ]
        }
    ]


@patch("backend.EvidenceModel.pipeline.EvidenceGraphBuilder")
@patch("backend.EvidenceModel.pipeline.EvidenceValidator")
@patch("backend.EvidenceModel.pipeline.EvidenceRetriever")
@patch("backend.EvidenceModel.pipeline.TopicEncoder")
@patch("backend.EvidenceModel.pipeline.ReportEncoder")
@patch("backend.EvidenceModel.pipeline.DocumentStructureParser")
@patch("backend.EvidenceModel.pipeline.ReportMetadataExtractor")
@patch("backend.EvidenceModel.pipeline.CurriculumEvidenceExtractor")
def test_pipeline_execution_and_node_filtering(
    mock_curriculum_cls,
    mock_metadata_cls,
    mock_doc_parser_cls,
    mock_report_encoder_cls,
    mock_topic_encoder_cls,
    mock_retriever_cls,
    mock_validator_cls,
    mock_graph_builder_cls,
    mock_heem_tree,
    sample_report_pages,
):

    # Curriculum extractor
    curriculum = MagicMock()
    curriculum.parse_pdf.return_value = mock_heem_tree
    mock_curriculum_cls.return_value = curriculum

    # Metadata extractor
    metadata = MagicMock()
    metadata.extract.return_value = MagicMock()
    mock_metadata_cls.return_value = metadata

    # Parsed document
    parsed_doc = MagicMock()
    parsed_doc.paragraphs = []
    parser = MagicMock()
    parser.parse.return_value = parsed_doc
    mock_doc_parser_cls.return_value = parser

    # Topic encoder
    encoded_topics = [
        {
            "id": 1,
            "type": "UNIT",
            "text": "Unit 1: Relational Model"
        },
        {
            "id": 2,
            "type": "TOPIC",
            "text": "Relational Algebra and SQL"
        }
    ]

    topic_encoder = MagicMock()
    topic_encoder.encode.return_value = encoded_topics
    mock_topic_encoder_cls.return_value = topic_encoder

    # Report encoder
    report_encoder = MagicMock()
    report_encoder.encode.return_value = []
    mock_report_encoder_cls.return_value = report_encoder

    # Retriever
    retriever = MagicMock()
    retriever.retrieve.return_value = []
    mock_retriever_cls.return_value = retriever

    # Validator
    validator = MagicMock()
    validator.validate.return_value = MagicMock()
    mock_validator_cls.return_value = validator

    # Fake graph
    graph = MagicMock()

    graph.nodes = {
        1: MagicMock(label="Unit 1: Relational Model"),
        2: MagicMock(label="Relational Algebra and SQL"),
    }

    builder = MagicMock()
    builder.build.return_value = graph
    mock_graph_builder_cls.return_value = builder

    core = GriffinCore()

    curriculum_path = r"backend\rl\Database\Samples\curr_test.pdf"

    result = core.process(
        curriculum_pdf_path=curriculum_path,
        report_input=sample_report_pages,
    )

    curriculum.parse_pdf.assert_called_once_with(curriculum_path)

    labels = [n.label for n in result.nodes.values()]

    assert "Unit 1: Relational Model" in labels
    assert "Relational Algebra and SQL" in labels

    prohibited = [
        "Database Systems",
        "Course Code: CS301",
        "Understand RDBMS concepts",
        "CO1: Design Relational Schemas",
        "PO1: Engineering Knowledge",
        "PSO1: Data Science Expertise",
        "Lab 1",
        "Slides",
        "Silberschatz",
        "Mid-term",
    ]

    for item in prohibited:
        assert item not in labels

    assert len(result.nodes) == 2