import {
  BookOpen,
  FileText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

function Score({ label, value }) {
  const numeric = Number(value);

  return (
    <div className="griffin-evidence-score">
      <span>{label}</span>

      <strong>
        {Number.isFinite(numeric)
          ? numeric.toFixed(3)
          : "—"}
      </strong>
    </div>
  );
}

function EvidenceCard({
  evidence,
  rank,
}) {
  const similarity =
    evidence?.similarity_score;

  const validation =
    evidence?.validation_score;

  return (
    <article className="griffin-evidence-card">
      <div className="griffin-evidence-card-header">
        <div className="griffin-evidence-rank">
          #{rank}
        </div>

        <div className="griffin-evidence-title">
          <span>
            {evidence?.heading ||
              "Untitled evidence"}
          </span>

          <small>
            {evidence?.evidence_id ||
              "Evidence"}
          </small>
        </div>

        <div className="griffin-evidence-page">
          <FileText size={14} />
          <span>
            Page {evidence?.page_number ?? "—"}
          </span>
        </div>
      </div>

      <div className="griffin-evidence-card-body">
        <div className="griffin-evidence-topic">
          <BookOpen size={14} />
          <span>
            Topic: {evidence?.topic_id || "—"}
          </span>
        </div>

        <div className="griffin-evidence-scores">
          <Score
            label="Similarity"
            value={similarity}
          />

          <Score
            label="Validation"
            value={validation}
          />
        </div>
      </div>
    </article>
  );
}

function EvidenceList({
  title,
  description,
  evidence = [],
  tone,
}) {
  return (
    <div className={`griffin-evidence-list is-${tone}`}>
      <div className="griffin-evidence-list-header">
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>

        <span>{evidence.length}</span>
      </div>

      {evidence.length === 0 ? (
        <div className="griffin-evidence-empty">
          No evidence returned.
        </div>
      ) : (
        evidence.map((item, index) => (
          <EvidenceCard
            key={
              item?.evidence_id ||
              `${tone}-${index}`
            }
            evidence={item}
            rank={index + 1}
          />
        ))
      )}
    </div>
  );
}

export default function EvidencePanel({
  result,
  evidence,
}) {
  const data =
    evidence ||
    result?.evidence_analysis ||
    {};

  const strongest =
    Array.isArray(data.strongest_evidence)
      ? data.strongest_evidence
      : [];

  const weakest =
    Array.isArray(data.weakest_evidence)
      ? data.weakest_evidence
      : [];

  const density =
    data.evidence_density_per_page || {};

  const distribution =
    data.evidence_distribution_by_unit || {};

  const densityEntries =
    Object.entries(density);

  const distributionEntries =
    Object.entries(distribution);

  return (
    <section className="griffin-result-section griffin-evidence-panel">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            EVIDENCE ANALYSIS
          </span>

          <h2>Evidence inspection</h2>

          <p>
            Inspect the strongest and weakest evidence
            returned by Griffin and its supporting scores.
          </p>
        </div>

        <div className="griffin-result-header-icon">
          <Sparkles size={19} />
        </div>
      </div>

      <div className="griffin-evidence-lists">
        <EvidenceList
          title="Strongest evidence"
          description="Highest-ranked supporting evidence."
          evidence={strongest}
          tone="strong"
        />

        <EvidenceList
          title="Weakest evidence"
          description="Evidence requiring closer inspection."
          evidence={weakest}
          tone="weak"
        />
      </div>

      <div className="griffin-evidence-analysis-grid">
        <div className="griffin-evidence-analysis-card">
          <div className="griffin-evidence-analysis-heading">
            <FileText size={16} />
            <span>Evidence density per page</span>
          </div>

          {densityEntries.length === 0 ? (
            <span className="griffin-muted">
              No page density data returned.
            </span>
          ) : (
            <div className="griffin-evidence-stat-list">
              {densityEntries.map(([page, count]) => (
                <div
                  key={page}
                  className="griffin-evidence-stat-row"
                >
                  <span>Page {page}</span>
                  <strong>{count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="griffin-evidence-analysis-card">
          <div className="griffin-evidence-analysis-heading">
            <ShieldCheck size={16} />
            <span>Evidence by unit</span>
          </div>

          {distributionEntries.length === 0 ? (
            <span className="griffin-muted">
              No unit distribution data returned.
            </span>
          ) : (
            <div className="griffin-evidence-stat-list">
              {distributionEntries.map(
                ([unit, count]) => (
                  <div
                    key={unit}
                    className="griffin-evidence-stat-row"
                  >
                    <span>{unit}</span>
                    <strong>{count}</strong>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}