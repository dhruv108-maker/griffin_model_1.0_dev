import {
  Activity,
  BarChart3,
  CheckCircle2,
  CircleAlert,
  FileCheck2,
  Layers3,
  Target,
} from "lucide-react";

const ICONS = {
  coverage: Target,
  confidence: Activity,
  units: Layers3,
  topics: BarChart3,
  evidence: FileCheck2,
  missing: CircleAlert,
  success: CheckCircle2,
};

export default function MetricCard({
  label,
  value,
  description,
  icon = "coverage",
  trend,
  tone = "neutral",
}) {
  const Icon =
    typeof icon === "function"
      ? icon
      : ICONS[icon] || Target;

  return (
    <article
      className={`griffin-metric-card is-${tone}`}
    >
      <div className="griffin-metric-card-top">
        <div className="griffin-metric-icon">
          <Icon size={17} />
        </div>

        {trend && (
          <span className="griffin-metric-trend">
            {trend}
          </span>
        )}
      </div>

      <div className="griffin-metric-value">
        {value ?? "—"}
      </div>

      <div className="griffin-metric-label">
        {label}
      </div>

      {description && (
        <div className="griffin-metric-description">
          {description}
        </div>
      )}
    </article>
  );
}