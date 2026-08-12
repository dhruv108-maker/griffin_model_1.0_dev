import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  FileText,
  LoaderCircle,
} from "lucide-react";

const STATUS_CONFIG = {
  COMPLETED: {
    label: "Completed",
    Icon: CheckCircle2,
    iconClass: "text-emerald-400",
  },

  PROCESSING: {
    label: "Processing",
    Icon: LoaderCircle,
    iconClass: "text-lime-300 animate-spin",
  },

  PENDING: {
    label: "Pending",
    Icon: Clock3,
    iconClass: "text-zinc-500",
  },

  FAILED: {
    label: "Failed",
    Icon: AlertCircle,
    iconClass: "text-red-400",
  },
};

export default function AnalysisItem({
  analysis,
  active = false,
  onClick,
}) {
  const status = String(
    analysis?.status || "PENDING"
  ).toUpperCase();

  const config =
    STATUS_CONFIG[status] ||
    STATUS_CONFIG.PENDING;

  const {
    Icon: StatusIcon,
    label: statusLabel,
    iconClass,
  } = config;

  const title =
    analysis?.name ||
    analysis?.title ||
    analysis?.project_name ||
    analysis?.projectName ||
    "Untitled Analysis";

  const subtitle =
    analysis?.report_title ||
    analysis?.curriculum_name ||
    analysis?.created_at ||
    analysis?.createdAt ||
    statusLabel;

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();
      onClick?.(analysis);
    }
  };

  return (
    <button
      type="button"
      onClick={() => onClick?.(analysis)}
      onKeyDown={handleKeyDown}
      title={title}
      aria-current={active ? "true" : undefined}
      className={[
        "group flex w-full items-center gap-3 rounded-lg border px-3 py-2.5",
        "text-left transition-all duration-150",
        "focus:outline-none focus:ring-1 focus:ring-lime-300/50",

        active
          ? "border-zinc-700 bg-zinc-800/80"
          : [
              "border-transparent",
              "hover:border-zinc-800",
              "hover:bg-zinc-800/50",
            ].join(" "),
      ].join(" ")}
    >
      {/* Active indicator */}
      <div
        className={[
          "h-7 w-1 shrink-0 rounded-full transition-colors",
          active
            ? "bg-lime-300"
            : "bg-zinc-800 group-hover:bg-zinc-700",
        ].join(" ")}
      />

      {/* Document icon */}
      <div
        className={[
          "grid h-8 w-8 shrink-0 place-items-center rounded-md",
          active
            ? "bg-lime-300/10 text-lime-300"
            : "bg-zinc-800 text-zinc-500",
        ].join(" ")}
      >
        <FileText size={15} />
      </div>

      {/* Analysis information */}
      <div className="min-w-0 flex-1">
        <span
          className={[
            "block truncate text-xs font-semibold",
            active
              ? "text-zinc-100"
              : "text-zinc-300 group-hover:text-zinc-100",
          ].join(" ")}
        >
          {title}
        </span>

        <span className="mt-1 block truncate text-[10px] text-zinc-500">
          {subtitle}
        </span>
      </div>

      {/* Status */}
      <StatusIcon
        size={14}
        className={`shrink-0 ${iconClass}`}
        aria-label={statusLabel}
      />
    </button>
  );
}