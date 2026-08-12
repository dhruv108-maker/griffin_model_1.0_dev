import { useMemo, useState } from "react";
import {
  Braces,
  CheckCircle2,
  Clipboard,
  Download,
  FileJson,
  FileText,
} from "lucide-react";

function formatValue(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "number") {
    return Number.isInteger(value)
      ? value.toLocaleString()
      : value.toLocaleString(undefined, {
          maximumFractionDigits: 4,
        });
  }

  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value);
}

function JsonBlock({ value }) {
  return (
    <pre className="griffin-report-json">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div className="griffin-report-summary-row">
      <span>{label}</span>
      <strong>{formatValue(value)}</strong>
    </div>
  );
}

export default function ReportPanel({
  result = null,
}) {
  const [copied, setCopied] = useState(false);
  const [view, setView] = useState("summary");

  const report = result?.report_information || {};
  const summary = result?.overall_summary || {};

  const reportName =
    report.report_name ||
    report.filename ||
    report.file_name ||
    report.name ||
    "Griffin Analysis Report";

  const reportId =
    result?.evaluation_id ||
    result?.id ||
    report.report_id ||
    "—";

  const generatedAt =
    result?.generated_at ||
    result?.created_at ||
    result?.timestamp ||
    report.generated_at ||
    null;

  const resultJson = useMemo(
    () => JSON.stringify(result || {}, null, 2),
    [result]
  );

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(resultJson);

      setCopied(true);

      window.setTimeout(
        () => setCopied(false),
        1800
      );
    } catch {
      setCopied(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob(
      [resultJson],
      { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);

    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = `${reportName
      .replace(/[^a-z0-9]+/gi, "_")
      .replace(/^_+|_+$/g, "")
      .toLowerCase() || "griffin_result"}.json`;

    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    URL.revokeObjectURL(url);
  };

  const summaryRows = [
    {
      label: "Overall coverage",
      value:
        summary.overall_coverage_pct ??
        summary.coverage_percentage,
    },
    {
      label: "Overall confidence",
      value:
        summary.overall_confidence ??
        summary.confidence,
    },
    {
      label: "Covered units",
      value: summary.covered_units,
    },
    {
      label: "Total units",
      value: summary.total_units,
    },
    {
      label: "Covered topics",
      value: summary.covered_topics,
    },
    {
      label: "Total topics",
      value: summary.total_topics,
    },
    {
      label: "Evidence count",
      value: summary.evidence_count,
    },
  ];

  return (
    <section className="griffin-result-section griffin-report-panel">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            ANALYSIS REPORT
          </span>

          <h2>Griffin result</h2>

          <p>
            Inspect the evaluation summary or the
            complete structured result returned by
            Griffin.
          </p>
        </div>

        <div className="griffin-report-actions">
          <button
            type="button"
            className="griffin-secondary-button"
            onClick={handleCopy}
            disabled={!result}
          >
            {copied ? (
              <CheckCircle2 size={15} />
            ) : (
              <Clipboard size={15} />
            )}

            <span>
              {copied ? "Copied" : "Copy JSON"}
            </span>
          </button>

          <button
            type="button"
            className="griffin-secondary-button"
            onClick={handleDownload}
            disabled={!result}
          >
            <Download size={15} />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      <div className="griffin-report-document">
        <div className="griffin-report-document-icon">
          <FileText size={20} />
        </div>

        <div className="griffin-report-document-info">
          <span className="griffin-report-document-kicker">
            EVALUATION RESULT
          </span>

          <h3>{reportName}</h3>

          <div className="griffin-report-document-meta">
            <span>
              Evaluation ID: {formatValue(reportId)}
            </span>

            {generatedAt && (
              <>
                <span className="griffin-report-meta-separator">
                  /
                </span>

                <span>
                  Generated:{" "}
                  {formatValue(generatedAt)}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="griffin-report-tabs">
        <button
          type="button"
          className={`griffin-report-tab ${
            view === "summary" ? "is-active" : ""
          }`}
          onClick={() => setView("summary")}
        >
          <FileText size={15} />
          Summary
        </button>

        <button
          type="button"
          className={`griffin-report-tab ${
            view === "json" ? "is-active" : ""
          }`}
          onClick={() => setView("json")}
        >
          <Braces size={15} />
          Raw JSON
        </button>
      </div>

      {view === "summary" ? (
        <div className="griffin-report-summary">
          <div className="griffin-report-summary-card">
            <div className="griffin-report-card-heading">
              <FileJson size={17} />

              <div>
                <h3>Evaluation summary</h3>
                <p>
                  Values returned by the Griffin
                  evaluation result.
                </p>
              </div>
            </div>

            <div className="griffin-report-summary-grid">
              {summaryRows.map((row) => (
                <SummaryRow
                  key={row.label}
                  label={row.label}
                  value={row.value}
                />
              ))}
            </div>
          </div>

          <div className="griffin-report-summary-card">
            <div className="griffin-report-card-heading">
              <Braces size={17} />

              <div>
                <h3>Result structure</h3>
                <p>
                  Top-level sections available in
                  this Griffin result.
                </p>
              </div>
            </div>

            <div className="griffin-report-sections">
              {Object.keys(result || {}).map(
                (key) => (
                  <div
                    key={key}
                    className="griffin-report-section-chip"
                  >
                    <span>{key}</span>
                    <CheckCircle2 size={13} />
                  </div>
                )
              )}

              {!result && (
                <span className="griffin-muted">
                  No result data available.
                </span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="griffin-report-json-container">
          {result ? (
            <JsonBlock value={result} />
          ) : (
            <div className="griffin-report-empty">
              No Griffin result is available.
            </div>
          )}
        </div>
      )}
    </section>
  );
}