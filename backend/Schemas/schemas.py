"""
Griffin Core v1.0
=================

Canonical data contracts for the Griffin Core Evidence Intelligence Framework.

Architecture
------------
Curriculum PDF
    ↓
Curriculum Parser
    ↓
HEEM Curriculum Tree
    ↓
Topic Encoder

Report PDF
    ↓
Griffin Report Tokenizer
    ↓
GriffinDocument
    ├── Metadata
    ├── Input Tokens
    └── Evidence Tokens
    ↓
Report Encoder
    ↓
Embedded Evidence Tokens
    ↓
Evidence Retrieval
    ↓
Evidence Validation
    ↓
Evidence Graph

These schemas are the single source of truth across the Griffin pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ==============================================================================
# 1. CURRICULUM (HEEM)
# ==============================================================================

class CurriculumNodeType(str, Enum):
    COURSE = "COURSE"
    METADATA = "METADATA"
    OBJECTIVE = "OBJECTIVE"
    UNIT = "UNIT"
    TOPIC = "TOPIC"


class HEEMNode(BaseModel):
    """
    Hierarchical Evidence Extraction Model (HEEM).

    Represents the curriculum knowledge hierarchy extracted from
    syllabus documents.
    """

    id: int
    type: CurriculumNodeType
    text: str
    page: int

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    attributes: Dict[str, Any] = Field(default_factory=dict)

    children: List["HEEMNode"] = Field(default_factory=list)


# ==============================================================================
# 2. REPORT METADATA
# ==============================================================================

class ReportMetadata(BaseModel):
    """
    Document-level metadata extracted from the report.
    """

    title: Optional[str] = None
    subtitle: Optional[str] = None

    author: Optional[str] = None
    institution: Optional[str] = None

    department: Optional[str] = None
    university: Optional[str] = None

    guide: Optional[str] = None
    supervisor: Optional[str] = None

    degree: Optional[str] = None
    semester: Optional[str] = None

    date: Optional[str] = None
    year: Optional[str] = None

    language: Optional[str] = None

    total_pages: int = 0

    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 3. INPUT TOKEN
# ==============================================================================

class InputTokenType(str, Enum):
    METADATA = "METADATA"
    NAVIGATION = "NAVIGATION"
    REFERENCE = "REFERENCE"
    COMPLIANCE = "COMPLIANCE"
    QUALITY = "QUALITY"
    EVIDENCE = "EVIDENCE"


class InputToken(BaseModel):
    """
    Intermediate token generated immediately after document parsing.

    These tokens preserve document structure before semantic enrichment.
    """

    token_id: str

    token_type: InputTokenType

    page_number: int

    text: str

    chapter: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None

    heading: Optional[str] = None

    bbox: Optional[List[float]] = None

    attributes: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 4. GRIFFIN EVIDENCE TOKEN
# ==============================================================================

class EvidenceToken(BaseModel):
    """
    Canonical semantic token used throughout Griffin Core.

    Every downstream module consumes EvidenceToken objects.
    """

    token_id: str

    page_number: int

    chapter: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None

    heading: Optional[str] = None

    text: str

    token_type: str
    category: str

    parent_token: Optional[str] = None

    # -------------------------------------------------------------------------
    # Semantic Enrichment
    # -------------------------------------------------------------------------

    concepts: List[str] = Field(default_factory=list)

    entities: List[str] = Field(default_factory=list)

    keywords: List[str] = Field(default_factory=list)

    citations: List[str] = Field(default_factory=list)

    figure_refs: List[str] = Field(default_factory=list)

    table_refs: List[str] = Field(default_factory=list)

    equation_refs: List[str] = Field(default_factory=list)

    # -------------------------------------------------------------------------
    # Semantic Scores
    # -------------------------------------------------------------------------

    semantic_density: float = 0.0

    technical_density: float = 0.0

    information_gain: float = 0.0

    priority: float = 0.0

    confidence: float = 1.0

    # -------------------------------------------------------------------------
    # Embedding
    # -------------------------------------------------------------------------

    embedding: Optional[List[float]] = None

    embedding_model: Optional[str] = None

    embedding_dimension: Optional[int] = None

    # -------------------------------------------------------------------------
    # Traceability
    # -------------------------------------------------------------------------

    source_page: Optional[int] = None

    source_bbox: Optional[List[float]] = None

    source_id: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 5. GRIFFIN DOCUMENT
# ==============================================================================

class GriffinStatistics(BaseModel):
    """
    Pipeline statistics.
    """

    total_pages: int = 0

    total_input_tokens: int = 0

    total_evidence_tokens: int = 0

    total_figures: int = 0

    total_tables: int = 0

    total_equations: int = 0

    total_citations: int = 0


class GriffinDocument(BaseModel):
    """
    Final tokenizer output.

    This object is consumed by Griffin Core.
    """

    version: str = "1.0"

    metadata: ReportMetadata

    statistics: GriffinStatistics = Field(
        default_factory=GriffinStatistics
    )

    input_tokens: List[InputToken] = Field(default_factory=list)

    tokens: List[EvidenceToken] = Field(default_factory=list)


# ==============================================================================
# 6. RETRIEVAL
# ==============================================================================

class CandidateEvidence(BaseModel):
    """
    Retrieved semantic candidate.
    """

    topic_id: int

    token_id: str

    similarity_score: float


class ValidatedEvidence(BaseModel):
    """
    Cross-encoder validated evidence.
    """

    topic_id: int

    token_id: str

    page_number: int

    similarity: float

    confidence: float

    reasoning_score: float

    explanation: str


# ==============================================================================
# 7. GRAPH
# ==============================================================================

class GraphNode(BaseModel):
    """
    Evidence Graph node.
    """

    id: str

    label: str

    node_type: str

    attributes: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """
    Evidence Graph edge.
    """

    source: str

    target: str

    relation: str

    similarity: float = 0.0

    confidence: float = 0.0

    reasoning_score: float = 0.0


class EvidenceGraph(BaseModel):
    """
    Explainable Evidence Graph.
    """

    nodes: Dict[str, GraphNode] = Field(default_factory=dict)

    edges: List[GraphEdge] = Field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_edges_by_relation(
        self,
        relation: str,
    ) -> List[GraphEdge]:
        return [
            edge
            for edge in self.edges
            if edge.relation == relation
        ]


# ==============================================================================
# PYDANTIC MODEL REBUILD
# ==============================================================================

HEEMNode.model_rebuild()