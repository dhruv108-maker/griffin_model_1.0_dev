import {
  CheckCircle2,
  CircleDashed,
  Layers3,
  Target,
  TriangleAlert,
} from "lucide-react";

function TopicGroup({ title, items = [], tone = "neutral", icon: Icon }) {
  return (
    <div className={`griffin-coverage-group is-${tone}`}>
      <div className="griffin-coverage-group-header">
        <div className="griffin-coverage-group-title">
          <Icon size={15} />
          <span>{title}</span>
        </div>

        <span className="griffin-coverage-count">
          {items.length}
        </span>
      </div>

      {items.length === 0 ? (
        <div className="griffin-coverage-empty">
          None
        </div>
      ) : (
        <div className="griffin-coverage-topic-list">
          {items.map((topic, index) => (
            <div
              key={`${topic}-${index}`}
              className="griffin-coverage-topic"
            >
              {topic}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CoveragePanel({
  result,
  coverage,
}) {
  const data =
    coverage ||
    result?.coverage_analysis ||
    {};

  const coveredTopics =
    Array.isArray(data.covered_topics)
      ? data.covered_topics
      : [];

  const uncoveredTopics =
    Array.isArray(data.uncovered_topics)
      ? data.uncovered_topics
      : [];

  const partiallyCoveredTopics =
    Array.isArray(data.partially_covered_topics)
      ? data.partially_covered_topics
      : [];

  const summary =
    result?.overall_summary || {};

  const completeness =
    result?.depth_and_significance
      ?.curriculum_completeness_pct;

  const total =
    coveredTopics.length +
    uncoveredTopics.length +
    partiallyCoveredTopics.length;

  const calculatedCoverage =
    total > 0
      ? (coveredTopics.length / total) * 100
      : null;

  const coveragePercentage =
    Number.isFinite(Number(summary.overall_coverage_pct))
      ? Number(summary.overall_coverage_pct)
      : calculatedCoverage;

  return (
    <section className="griffin-result-section griffin-coverage-panel">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            COVERAGE ANALYSIS
          </span>

          <h2>Curriculum coverage</h2>

          <p>
            Distribution of topics identified as covered,
            partially covered, or uncovered.
          </p>
        </div>

        <div className="griffin-coverage-score">
          <span>
            {coveragePercentage !== null
              ? `${coveragePercentage.toFixed(1)}%`
              : "—"}
          </span>

          <small>overall coverage</small>
        </div>
      </div>

      <div className="griffin-coverage-overview">
        <div className="griffin-coverage-progress">
          <div className="griffin-coverage-progress-track">
            <div
              className="griffin-coverage-progress-value"
              style={{
                width: `${Math.max(
                  0,
                  Math.min(
                    100,
                    coveragePercentage || 0
                  )
                )}%`,
              }}
            />
          </div>

          <div className="griffin-coverage-progress-meta">
            <span>
              {summary.covered_topics ?? coveredTopics.length}{" "}
              covered
            </span>

            <span>
              {summary.total_topics ?? total} total topics
            </span>
          </div>
        </div>

        <div className="griffin-coverage-completeness">
          <Layers3 size={17} />

          <div>
            <span>Curriculum completeness</span>

            <strong>
              {Number.isFinite(Number(completeness))
                ? `${Number(completeness).toFixed(1)}%`
                : "—"}
            </strong>
          </div>
        </div>
      </div>

      <div className="griffin-coverage-grid">
        <TopicGroup
          title="Covered"
          items={coveredTopics}
          tone="success"
          icon={CheckCircle2}
        />

        <TopicGroup
          title="Partially covered"
          items={partiallyCoveredTopics}
          tone="warning"
          icon={CircleDashed}
        />

        <TopicGroup
          title="Uncovered"
          items={uncoveredTopics}
          tone="danger"
          icon={TriangleAlert}
        />
      </div>

      <div className="griffin-coverage-footer">
        <Target size={16} />

        <span>
          Coverage is based on Griffin's returned
          coverage analysis and overall summary.
        </span>
      </div>
    </section>
  );
}