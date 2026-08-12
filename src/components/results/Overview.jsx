import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  FileCheck2,
  Layers3,
  Target,
} from "lucide-react";

import MetricCard from "./MetricCard";

function formatPercentage(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `${number.toFixed(1)}%`;
}

function getNumber(...values) {
  for (const value of values) {
    const number = Number(value);

    if (Number.isFinite(number)) {
      return number;
    }
  }

  return null;
}

export default function Overview({ result }) {
  const summary = result?.overall_summary || {};
  const report = result?.report_information || {};
  const curriculum = result?.curriculum_mapping || {};
  const topics = result?.topic_mapping || {};
  const evidence = result?.evidence_analysis || {};
  const depth = result?.depth_and_significance || {};

  /*
   * Prefer values explicitly returned by Griffin.
   * Only use counts from nested result structures when
   * the summary does not expose the corresponding value.
   */

  const coverage = getNumber(
    summary.overall_coverage_pct,
    summary.coverage_percentage,
    summary.coverage
  );

  const confidence = getNumber(
    summary.overall_confidence,
    summary.confidence,
    evidence.overall_confidence
  );

  const coveredUnits = getNumber(
    summary.covered_units,
    curriculum.covered_units
  );

  const totalUnits = getNumber(
    summary.total_units,
    curriculum.total_units
  );

  const coveredTopics = getNumber(
    summary.covered_topics,
    topics.covered_topics
  );

  const totalTopics = getNumber(
    summary.total_topics,
    topics.total_topics
  );

  const evidenceCount = getNumber(
    summary.evidence_count,
    evidence.total_evidence,
    evidence.evidence_count
  );

  const missingUnits = getNumber(
    summary.missing_units,
    curriculum.missing_units
  );

  const missingTopics = getNumber(
    summary.missing_topics,
    topics.missing_topics
  );

  const reportName =
    report.report_name ||
    report.filename ||
    report.file_name ||
    report.name ||
    "Analysis Result";

  const reportCount = Array.isArray(
    report.reports
  )
    ? report.reports.length
    : null;

  const completeness = getNumber(
    depth.curriculum_completeness_pct,
    depth.completeness_percentage
  );

  const coverageDescription =
    coverage !== null
      ? `${formatPercentage(coverage)} of evaluated curriculum`
      : "No coverage percentage returned";

  const confidenceDescription =
    confidence !== null
      ? "Overall Griffin confidence"
      : "No confidence score returned";

  const unitValue =
    coveredUnits !== null && totalUnits !== null
      ? `${coveredUnits}/${totalUnits}`
      : coveredUnits !== null
        ? String(coveredUnits)
        : "—";

  const topicValue =
    coveredTopics !== null && totalTopics !== null
      ? `${coveredTopics}/${totalTopics}`
      : coveredTopics !== null
        ? String(coveredTopics)
        : "—";

  return (
    <section className="griffin-result-section griffin-overview">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            ANALYSIS OVERVIEW
          </span>

          <h2>Evaluation summary</h2>

          <p>
            High-level results from the Griffin
            curriculum and evidence evaluation.
          </p>
        </div>

        <div className="griffin-overview-status">
          <CheckCircle2 size={16} />
          <span>Evaluation result</span>
        </div>
      </div>

      <div className="griffin-overview-report">
        <div className="griffin-overview-report-icon">
          <FileCheck2 size={20} />
        </div>

        <div className="griffin-overview-report-info">
          <span className="griffin-overview-report-label">
            ANALYZED REPORT
          </span>

          <strong>{reportName}</strong>

          {reportCount !== null && (
            <small>
              {reportCount}{" "}
              {reportCount === 1
                ? "report"
                : "reports"}{" "}
              evaluated
            </small>
          )}
        </div>

        {result?.evaluation_id && (
          <div className="griffin-overview-evaluation-id">
            <span>Evaluation</span>
            <code>{result.evaluation_id}</code>
          </div>
        )}
      </div>

      <div className="griffin-metric-grid">
        <MetricCard
          label="Overall coverage"
          value={
            coverage !== null
              ? formatPercentage(coverage)
              : "—"
          }
          description={coverageDescription}
          icon="coverage"
          tone={
            coverage !== null && coverage >= 70
              ? "success"
              : "neutral"
          }
        />

        <MetricCard
          label="Confidence"
          value={
            confidence !== null
              ? confidence.toFixed(3)
              : "—"
          }
          description={confidenceDescription}
          icon="confidence"
          tone="neutral"
        />

        <MetricCard
          label="Units covered"
          value={unitValue}
          description={
            missingUnits !== null
              ? `${missingUnits} unit${
                  missingUnits === 1 ? "" : "s"
                } not covered`
              : "Curriculum unit coverage"
          }
          icon="units"
          tone="neutral"
        />

        <MetricCard
          label="Topics covered"
          value={topicValue}
          description={
            missingTopics !== null
              ? `${missingTopics} topic${
                  missingTopics === 1 ? "" : "s"
                } not covered`
              : "Curriculum topic coverage"
          }
          icon="topics"
          tone="neutral"
        />

        <MetricCard
          label="Evidence"
          value={
            evidenceCount !== null
              ? evidenceCount.toLocaleString()
              : "—"
          }
          description="Evidence items identified"
          icon="evidence"
          tone="neutral"
        />

        <MetricCard
          label="Completeness"
          value={
            completeness !== null
              ? formatPercentage(completeness)
              : "—"
          }
          description="Curriculum completeness"
          icon="success"
          tone={
            completeness !== null &&
            completeness >= 70
              ? "success"
              : "neutral"
          }
        />
      </div>

      <div className="griffin-overview-lower-grid">
        <div className="griffin-overview-panel">
          <div className="griffin-overview-panel-header">
            <div className="griffin-overview-panel-icon">
              <Target size={17} />
            </div>

            <div>
              <h3>Coverage snapshot</h3>
              <p>
                Current curriculum alignment at a glance.
              </p>
            </div>
          </div>

          <div className="griffin-overview-bars">
            <div className="griffin-overview-bar-row">
              <div className="griffin-overview-bar-label">
                <span>Coverage</span>
                <strong>
                  {coverage !== null
                    ? formatPercentage(coverage)
                    : "—"}
                </strong>
              </div>

              <div className="griffin-overview-bar-track">
                <div
                  className="griffin-overview-bar-fill"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(100, coverage || 0)
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="griffin-overview-bar-row">
              <div className="griffin-overview-bar-label">
                <span>Completeness</span>
                <strong>
                  {completeness !== null
                    ? formatPercentage(completeness)
                    : "—"}
                </strong>
              </div>

              <div className="griffin-overview-bar-track">
                <div
                  className="griffin-overview-bar-fill"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(
                        100,
                        completeness || 0
                      )
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="griffin-overview-panel">
          <div className="griffin-overview-panel-header">
            <div className="griffin-overview-panel-icon">
              <BarChart3 size={17} />
            </div>

            <div>
              <h3>Evaluation breakdown</h3>
              <p>
                Structural coverage counts returned by Griffin.
              </p>
            </div>
          </div>

          <div className="griffin-overview-breakdown">
            <div className="griffin-overview-breakdown-row">
              <span>
                <Layers3 size={14} />
                Covered units
              </span>

              <strong>
                {coveredUnits ?? "—"}
              </strong>
            </div>

            <div className="griffin-overview-breakdown-row">
              <span>
                <BarChart3 size={14} />
                Covered topics
              </span>

              <strong>
                {coveredTopics ?? "—"}
              </strong>
            </div>

            <div className="griffin-overview-breakdown-row">
              <span>
                <AlertTriangle size={14} />
                Missing units
              </span>

              <strong>
                {missingUnits ?? "—"}
              </strong>
            </div>

            <div className="griffin-overview-breakdown-row">
              <span>
                <AlertTriangle size={14} />
                Missing topics
              </span>

              <strong>
                {missingTopics ?? "—"}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}