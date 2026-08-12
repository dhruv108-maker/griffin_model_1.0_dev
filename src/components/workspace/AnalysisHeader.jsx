import {
  CheckCircle2,
  Clock3,
  LoaderCircle,
  AlertCircle,
  FileText,
} from "lucide-react";

const STATUS_CONFIG = {
  COMPLETED: {
    label: "Completed",
    icon: CheckCircle2,
    className: "success",
  },
  PROCESSING: {
    label: "Processing",
    icon: LoaderCircle,
    className: "processing",
  },
  PENDING: {
    label: "Pending",
    icon: Clock3,
    className: "pending",
  },
  FAILED: {
    label: "Failed",
    icon: AlertCircle,
    className: "failed",
  },
};

export default function AnalysisHeader({
  analysis,
  processing = false,
}) {
  const rawStatus = processing
    ? "PROCESSING"
    : String(analysis?.status || "PENDING").toUpperCase();

  const config =
    STATUS_CONFIG[rawStatus] || STATUS_CONFIG.PENDING;

  const StatusIcon = config.icon;

  const title =
    analysis?.name ||
    analysis?.title ||
    analysis?.project_name ||
    "Untitled Analysis";

  const evaluationId =
    analysis?.evaluation_id ||
    analysis?.id ||
    analysis?.evaluationId;

  return (
    <header className="griffin-analysis-header">
      <div className="griffin-analysis-header-main">
        <div className="griffin-analysis-document-icon">
          <FileText size={19} />
        </div>

        <div className="griffin-analysis-heading">
          <div className="griffin-analysis-breadcrumb">
            Analysis
            {evaluationId && (
              <>
                <span>/</span>
                <span>{evaluationId}</span>
              </>
            )}
          </div>

          <h1>{title}</h1>
        </div>
      </div>

      <div
        className={`griffin-analysis-status is-${config.className}`}
      >
        <StatusIcon
          size={15}
          className={
            config.className === "processing"
              ? "griffin-spin"
              : ""
          }
        />

        <span>{config.label}</span>
      </div>
    </header>
  );
}