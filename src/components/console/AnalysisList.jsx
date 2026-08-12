import AnalysisItem from "./AnalysisItem";

export default function AnalysisList({
  analyses = [],
  activeEvaluationId = null,
  onSelect,
}) {
  if (!analyses.length) {
    return (
      <div className="griffin-analysis-empty">
        <span>No analyses yet</span>
        <small>Start an analysis to see it here.</small>
      </div>
    );
  }

  return (
    <div className="griffin-analysis-list">
      {analyses.map((analysis) => {
        const id =
          analysis?.evaluation_id ??
          analysis?.evaluationId ??
          analysis?.id;

        return (
          <AnalysisItem
            key={id}
            analysis={analysis}
            active={id === activeEvaluationId}
            onClick={() => onSelect?.(analysis)}
          />
        );
      })}
    </div>
  );
}