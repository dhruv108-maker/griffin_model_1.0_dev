"""
presentation/schema.py
Defines the hierarchical Pydantic models for griffin_result.json.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    report_title: str
    student: str
    university: str
    total_pages: int
    processing_time_seconds: float
    timestamp: str


class OverallSummary(BaseModel):
    overall_coverage_pct: float
    overall_confidence: float
    total_units: int
    covered_units: int
    total_topics: int
    covered_topics: int
    missing_topics_count: int
    total_evidence: int
    validated_evidence: int


class UnitMappingDetail(BaseModel):
    unit_id: str
    unit_name: str
    coverage_percentage: float
    topics_covered: List[str]
    topics_missing: List[str]
    evidence_count: int
    average_confidence: float
    significance_score: float


class TopicMappingDetail(BaseModel):
    topic_id: str
    topic_name: str
    unit_id: str
    matched: bool
    confidence: float
    evidence_count: int
    supporting_pages: List[int]
    supporting_headings: List[str]
    evidence_ids: List[str]


class EvidenceDetail(BaseModel):
    evidence_id: str
    topic_id: str
    page_number: int
    heading: str
    similarity_score: float
    validation_score: float


class EvidenceAnalysis(BaseModel):
    strongest_evidence: List[EvidenceDetail]
    weakest_evidence: List[EvidenceDetail]
    evidence_density_per_page: Dict[int, int]
    evidence_distribution_by_unit: Dict[str, int]


class CoverageAnalysis(BaseModel):
    covered_topics: List[str]
    uncovered_topics: List[str]
    partially_covered_topics: List[str]


class DepthAndSignificance(BaseModel):
    breadth_score: float
    depth_score: float
    evidence_richness_pct: float
    curriculum_completeness_pct: float
    report_comprehensiveness_score: float
    average_evidence_per_topic: float
    average_evidence_per_unit: float


class GraphStatistics(BaseModel):
    total_nodes: int
    total_edges: int
    unit_nodes: int
    topic_nodes: int
    evidence_nodes: int
    graph_density: float
    average_degree: float


class VisualizationPayload(BaseModel):
    unit_coverage_bar_chart: Dict[str, Any]
    topic_coverage_pie_chart: Dict[str, Any]
    page_evidence_distribution: Dict[str, Any]
    confidence_histogram: Dict[str, Any]
    curriculum_treemap: Dict[str, Any]
    curriculum_sunburst: Dict[str, Any]


class GriffinResult(BaseModel):
    report_information: ReportMetadata
    overall_summary: OverallSummary
    curriculum_mapping: List[UnitMappingDetail]
    topic_mapping: List[TopicMappingDetail]
    evidence_analysis: EvidenceAnalysis
    coverage_analysis: CoverageAnalysis
    depth_and_significance: DepthAndSignificance
    graph_statistics: GraphStatistics
    visualizations: VisualizationPayload