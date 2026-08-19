from typing import Any, Dict, List

from backend.Schemas.schemas import (
    EvidenceGraph,
    EvidenceToken,
    GraphEdge,
    GraphNode,
    ValidatedEvidence,
)


class EvidenceGraphBuilder:
    """Build the explainable Unit -> Topic -> Evidence -> Token graph."""

    def __init__(self):
        self.graph = EvidenceGraph()

    def build(
        self,
        units: List[Dict[str, Any]],
        topics: List[Dict[str, Any]],
        validated_evidences: List[ValidatedEvidence],
        evidence_tokens: List[EvidenceToken],
    ) -> EvidenceGraph:
        self.graph = EvidenceGraph()

        token_map = {token.token_id: token for token in evidence_tokens}

        for unit in units:
            unit_id = f"unit_{unit['id']}"
            self.graph.add_node(
                GraphNode(
                    id=unit_id,
                    label=unit["text"],
                    node_type="UNIT",
                    attributes={"type": unit.get("type")},
                )
            )

        for topic in topics:
            topic_id = f"topic_{topic['id']}"
            self.graph.add_node(
                GraphNode(
                    id=topic_id,
                    label=topic["text"],
                    node_type="TOPIC",
                    attributes={
                        "type": topic.get("type"),
                        "unit_id": topic.get("unit_id"),
                    },
                )
            )

            unit_id = topic.get("unit_id")
            if unit_id is not None:
                source_unit_id = f"unit_{unit_id}"
                if source_unit_id in self.graph.nodes:
                    self.graph.add_edge(
                        GraphEdge(
                            source=source_unit_id,
                            target=topic_id,
                            relation="CONTAINS_TOPIC",
                            similarity=1.0,
                            confidence=1.0,
                            reasoning_score=1.0,
                        )
                    )

        for index, evidence in enumerate(validated_evidences):
            token = token_map.get(evidence.token_id)
            if token is None:
                continue

            evidence_id = f"evidence_{index}"
            page_id = f"page_{token.page_number}"
            topic_id = f"topic_{evidence.topic_id}"

            self.graph.add_node(
                GraphNode(
                    id=evidence_id,
                    label=evidence.explanation,
                    node_type="EVIDENCE",
                    attributes={
                        "confidence": evidence.confidence,
                        "reasoning_score": evidence.reasoning_score,
                        "similarity": evidence.similarity,
                    },
                )
            )

            if token.token_id not in self.graph.nodes:
                self.graph.add_node(
                    GraphNode(
                        id=token.token_id,
                        label=token.text[:120] + "..." if len(token.text) > 120 else token.text,
                        node_type="TOKEN",
                        attributes={
                            "page": token.page_number,
                            "chapter": token.chapter,
                            "section": token.section,
                            "subsection": token.subsection,
                            "heading": token.heading,
                            "category": token.category,
                            "token_type": token.token_type,
                            "confidence": token.confidence,
                            "priority": token.priority,
                            "concepts": token.concepts,
                            "entities": token.entities,
                            "keywords": token.keywords,
                            "citations": token.citations,
                            "figure_refs": token.figure_refs,
                            "table_refs": token.table_refs,
                            "equation_refs": token.equation_refs,
                            "semantic_density": token.semantic_density,
                            "technical_density": token.technical_density,
                            "information_gain": token.information_gain,
                            "embedding_model": token.embedding_model,
                            "embedding_dimension": token.embedding_dimension,
                            "full_text": token.text,
                        },
                    )
                )

            if page_id not in self.graph.nodes:
                self.graph.add_node(
                    GraphNode(
                        id=page_id,
                        label=f"Page {token.page_number}",
                        node_type="PAGE",
                        attributes={"page_number": token.page_number},
                    )
                )

            if topic_id in self.graph.nodes:
                self.graph.add_edge(
                    GraphEdge(
                        source=topic_id,
                        target=evidence_id,
                        relation="HAS_EVIDENCE",
                        similarity=evidence.similarity,
                        confidence=evidence.confidence,
                        reasoning_score=evidence.reasoning_score,
                    )
                )

            self.graph.add_edge(
                GraphEdge(
                    source=evidence_id,
                    target=token.token_id,
                    relation="SUPPORTED_BY",
                    similarity=evidence.similarity,
                    confidence=evidence.confidence,
                    reasoning_score=evidence.reasoning_score,
                )
            )

            self.graph.add_edge(
                GraphEdge(
                    source=token.token_id,
                    target=page_id,
                    relation="LOCATED_ON",
                    similarity=1.0,
                    confidence=1.0,
                    reasoning_score=1.0,
                )
            )

            if token.parent_token and token.parent_token in token_map:
                self.graph.add_edge(
                    GraphEdge(
                        source=token.parent_token,
                        target=token.token_id,
                        relation="PARENT_OF",
                        similarity=1.0,
                        confidence=1.0,
                        reasoning_score=1.0,
                    )
                )

        return self.graph
