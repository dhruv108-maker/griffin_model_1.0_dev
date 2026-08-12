"""
presentation/builder.py
Transforms EvidenceGraph and execution metadata into GriffinResult payload.
"""

import json
import math
from datetime import datetime
from typing import Dict, Any, List, Set

from .schema import (
    GriffinResult,
    ReportMetadata,
    OverallSummary,
    UnitMappingDetail,
    TopicMappingDetail,
    EvidenceDetail,
    EvidenceAnalysis,
    CoverageAnalysis,
    DepthAndSignificance,
    GraphStatistics,
    VisualizationPayload,
)


class GriffinResultBuilder:
    """Deterministic result generator for Griffin Core v1.0."""

    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold

    def build(
        self,
        evidence_graph: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> GriffinResult:
        """
        Parses EvidenceGraph dict representation and computes the presentation model.
        """
        nodes = evidence_graph.get("nodes", {})
        edges = evidence_graph.get("edges", [])

        # 1. Parse Nodes
        units_map: Dict[str, Dict[str, Any]] = {}
        topics_map: Dict[str, Dict[str, Any]] = {}
        evidence_map: Dict[str, Dict[str, Any]] = {}

        for n_id, n_data in nodes.items():
            n_type = str(n_data.get("node_type", "")).upper()
            attrs = n_data.get("attributes", {})
            if n_type == "UNIT":
                units_map[n_id] = {
                    "id": n_id,
                    "label": n_data.get("label", n_id),
                    "topics": [],
                }
            elif n_type == "TOPIC":
                topics_map[n_id] = {
                    "id": n_id,
                    "label": n_data.get("label", n_id),
                    "unit_id": attrs.get("unit_id"),
                    "evidence": [],
                }
            elif n_type == "EVIDENCE":
                evidence_map[n_id] = {
                    "id": n_id,
                    "page_number": attrs.get("page_number", 0),
                    "heading": attrs.get("heading", "N/A"),
                    "similarity": attrs.get("similarity", 0.0),
                    "validation_score": attrs.get("validation_score", 0.0),
                }

        # 2. Map Relationships from Edges
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            attrs = edge.get("attributes", {})

            if src in units_map and tgt in topics_map:
                units_map[src]["topics"].append(tgt)
                topics_map[tgt]["unit_id"] = src

            if src in topics_map and tgt in evidence_map:
                ev_item = dict(evidence_map[tgt])
                ev_item["similarity"] = attrs.get("similarity", ev_item["similarity"])
                ev_item["validation_score"] = attrs.get("validation_score", ev_item["validation_score"])
                topics_map[src]["evidence"].append(ev_item)

        # 3. Topic Mapping Extraction
        topic_details: List[TopicMappingDetail] = []
        covered_topics: List[str] = []
        uncovered_topics: List[str] = []
        partially_covered_topics: List[str] = []
        all_evidences_flat: List[EvidenceDetail] = []

        for t_id, t_data in topics_map.items():
            ev_list = t_data["evidence"]
            ev_count = len(ev_list)
            pages = sorted(list({e["page_number"] for e in ev_list}))
            headings = list({e["heading"] for e in ev_list})
            ev_ids = [e["id"] for e in ev_list]

            conf = max([e["validation_score"] for e in ev_list], default=0.0)
            is_matched = ev_count > 0 and conf >= self.confidence_threshold

            if is_matched:
                if conf >= 0.75:
                    covered_topics.append(t_data["label"])
                else:
                    partially_covered_topics.append(t_data["label"])
            else:
                uncovered_topics.append(t_data["label"])

            topic_details.append(
                TopicMappingDetail(
                    topic_id=t_id,
                    topic_name=t_data["label"],
                    unit_id=t_data["unit_id"] or "",
                    matched=is_matched,
                    confidence=round(conf, 4),
                    evidence_count=ev_count,
                    supporting_pages=pages,
                    supporting_headings=headings,
                    evidence_ids=ev_ids,
                )
            )

            for e in ev_list:
                all_evidences_flat.append(
                    EvidenceDetail(
                        evidence_id=e["id"],
                        topic_id=t_id,
                        page_number=e["page_number"],
                        heading=e["heading"],
                        similarity_score=round(e["similarity"], 4),
                        validation_score=round(e["validation_score"], 4),
                    )
                )

        # 4. Unit Mapping Extraction
        unit_details: List[UnitMappingDetail] = []
        unit_evidence_counts: Dict[str, int] = {}

        for u_id, u_data in units_map.items():
            u_topic_ids = u_data["topics"]
            u_topics = [topics_map[tid] for tid in u_topic_ids if tid in topics_map]
            
            u_covered_t = [
                t for t in u_topics 
                if len(t["evidence"]) > 0 and max([e["validation_score"] for e in t["evidence"]], default=0.0) >= self.confidence_threshold
            ]
            u_missing_t = [t for t in u_topics if t not in u_covered_t]

            tot_topics = len(u_topics)
            cov_pct = round((len(u_covered_t) / tot_topics * 100.0), 2) if tot_topics > 0 else 0.0

            u_ev_count = sum(len(t["evidence"]) for t in u_topics)
            unit_evidence_counts[u_data["label"]] = u_ev_count

            # Compute avg confidence
            all_u_conf = [
                max([e["validation_score"] for e in t["evidence"]], default=0.0)
                for t in u_topics
            ]
            avg_u_conf = sum(all_u_conf) / len(all_u_conf) if all_u_conf else 0.0

            # Deterministic Significance Score Formula
            sig_score = sum(
                max([e["validation_score"] for e in t["evidence"]], default=0.0) * math.log(1 + len(t["evidence"]))
                for t in u_topics
            ) / max(1, tot_topics)

            unit_details.append(
                UnitMappingDetail(
                    unit_id=u_id,
                    unit_name=u_data["label"],
                    coverage_percentage=cov_pct,
                    topics_covered=[t["label"] for t in u_covered_t],
                    topics_missing=[t["label"] for t in u_missing_t],
                    evidence_count=u_ev_count,
                    average_confidence=round(avg_u_conf, 4),
                    significance_score=round(sig_score, 4),
                )
            )

        # 5. Evidence Analysis & Page Density
        unique_evidences = {e.evidence_id: e for e in all_evidences_flat}.values()
        sorted_evidences = sorted(unique_evidences, key=lambda x: x.validation_score, reverse=True)

        page_density: Dict[int, int] = {}
        for ev in unique_evidences:
            page_density[ev.page_number] = page_density.get(ev.page_number, 0) + 1

        evidence_analysis = EvidenceAnalysis(
            strongest_evidence=list(sorted_evidences[:5]),
            weakest_evidence=list(sorted_evidences[-5:]),
            evidence_density_per_page=dict(sorted(page_density.items())),
            evidence_distribution_by_unit=unit_evidence_counts,
        )

        # 6. Overall Summary Metrics
        tot_units = len(units_map)
        cov_units = sum(1 for u in unit_details if u.coverage_percentage > 0)
        tot_topics = len(topics_map)
        cov_topics_count = len(covered_topics) + len(partially_covered_topics)
        overall_cov_pct = round((cov_topics_count / tot_topics * 100.0), 2) if tot_topics > 0 else 0.0

        overall_conf = (
            sum(t.confidence for t in topic_details) / len(topic_details)
            if topic_details else 0.0
        )

        overall_summary = OverallSummary(
            overall_coverage_pct=overall_cov_pct,
            overall_confidence=round(overall_conf, 4),
            total_units=tot_units,
            covered_units=cov_units,
            total_topics=tot_topics,
            covered_topics=cov_topics_count,
            missing_topics_count=len(uncovered_topics),
            total_evidence=len(evidence_map),
            validated_evidence=len(unique_evidences),
        )

        # 7. Depth & Significance Deterministic Scores
        avg_ev_topic = round(len(unique_evidences) / tot_topics, 2) if tot_topics > 0 else 0.0
        avg_ev_unit = round(len(unique_evidences) / tot_units, 2) if tot_units > 0 else 0.0
        breadth_score = round((cov_units / tot_units * 100.0), 2) if tot_units > 0 else 0.0
        
        target_density = 5.0
        depth_score = round(min(100.0, (avg_ev_topic / target_density) * 100.0), 2)
        ev_richness = round((len(unique_evidences) / max(1, len(evidence_map))) * 100.0, 2)
        
        comprehensiveness = round(
            (0.5 * overall_cov_pct) + (0.3 * depth_score) + (0.2 * overall_conf * 100.0), 2
        )

        depth_significance = DepthAndSignificance(
            breadth_score=breadth_score,
            depth_score=depth_score,
            evidence_richness_pct=ev_richness,
            curriculum_completeness_pct=overall_cov_pct,
            report_comprehensiveness_score=comprehensiveness,
            average_evidence_per_topic=avg_ev_topic,
            average_evidence_per_unit=avg_ev_unit,
        )

        # 8. Graph Topological Statistics
        n_count = len(nodes)
        e_count = len(edges) if isinstance(edges, list) else 0
        avg_deg = (2.0 * e_count / n_count) if n_count > 0 else 0.0
        density = (e_count / (n_count * (n_count - 1))) if n_count > 1 else 0.0

        graph_stats = GraphStatistics(
            total_nodes=n_count,
            total_edges=e_count,
            unit_nodes=tot_units,
            topic_nodes=tot_topics,
            evidence_nodes=len(evidence_map),
            graph_density=round(density, 4),
            average_degree=round(avg_deg, 4),
        )

        # 9. UI Visualization Pre-formatted Payloads
        visualizations = self._build_visualizations(
            unit_details, topic_details, page_density, units_map, topics_map
        )

        # Combine into GriffinResult
        return GriffinResult(
            report_information=ReportMetadata(
                report_title=metadata.get("title", "Curriculum Analysis Report"),
                student=metadata.get("student", "Unknown Student"),
                university=metadata.get("university", "GSFC University"),
                total_pages=metadata.get("total_pages", 0),
                processing_time_seconds=metadata.get("processing_time", 0.0),
                timestamp=datetime.utcnow().isoformat() + "Z",
            ),
            overall_summary=overall_summary,
            curriculum_mapping=unit_details,
            topic_mapping=topic_details,
            evidence_analysis=evidence_analysis,
            coverage_analysis=CoverageAnalysis(
                covered_topics=covered_topics,
                uncovered_topics=uncovered_topics,
                partially_covered_topics=partially_covered_topics,
            ),
            depth_and_significance=depth_significance,
            graph_statistics=graph_stats,
            visualizations=visualizations,
        )

    def _build_visualizations(
        self,
        units: List[UnitMappingDetail],
        topics: List[TopicMappingDetail],
        page_density: Dict[int, int],
        units_map: Dict[str, Any],
        topics_map: Dict[str, Any],
    ) -> VisualizationPayload:
        """Constructs UI component payloads directly consumed by dashboard charts."""
        # Bar Chart: Coverage per Unit
        unit_bar = {
            "labels": [u.unit_name for u in units],
            "datasets": [
                {
                    "label": "Coverage %",
                    "data": [u.coverage_percentage for u in units],
                }
            ],
        }

        # Pie Chart: Topic Coverage Categorization
        matched_cnt = sum(1 for t in topics if t.matched)
        unmatched_cnt = len(topics) - matched_cnt
        topic_pie = {
            "labels": ["Covered Topics", "Uncovered Topics"],
            "datasets": [{"data": [matched_cnt, unmatched_cnt]}],
        }

        # Page Distribution Chart
        page_dist = {
            "labels": [f"Page {p}" for p in page_density.keys()],
            "datasets": [{"label": "Evidence Count", "data": list(page_density.values())}],
        }

        # Confidence Histogram
        bins = [0.0, 0.25, 0.50, 0.75, 1.00]
        histogram_counts = [0, 0, 0, 0]
        for t in topics:
            c = t.confidence
            if c < 0.25:
                histogram_counts[0] += 1
            elif c < 0.50:
                histogram_counts[1] += 1
            elif c < 0.75:
                histogram_counts[2] += 1
            else:
                histogram_counts[3] += 1

        conf_hist = {
            "labels": ["0.0-0.25", "0.25-0.50", "0.50-0.75", "0.75-1.00"],
            "datasets": [{"label": "Topics Count", "data": histogram_counts}],
        }

        # Treemap & Sunburst Structures
        treemap_children = []
        sunburst_children = []

        for u_id, u_data in units_map.items():
            u_topics = [topics_map[t] for t in u_data["topics"] if t in topics_map]
            topic_children = []
            for t in u_topics:
                ev_cnt = len(t["evidence"])
                topic_children.append({
                    "name": t["label"],
                    "value": max(1, ev_cnt),
                    "confidence": max([e["validation_score"] for e in t["evidence"]], default=0.0)
                })

            node_data = {
                "name": u_data["label"],
                "children": topic_children
            }
            treemap_children.append(node_data)
            sunburst_children.append(node_data)

        return VisualizationPayload(
            unit_coverage_bar_chart=unit_bar,
            topic_coverage_pie_chart=topic_pie,
            page_evidence_distribution=page_dist,
            confidence_histogram=conf_hist,
            curriculum_treemap={"name": "Curriculum", "children": treemap_children},
            curriculum_sunburst={"name": "Curriculum", "children": sunburst_children},
        )