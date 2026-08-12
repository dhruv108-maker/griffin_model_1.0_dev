import {
  Activity,
  FilePlus2,
  PanelLeftClose,
  Settings,
} from "lucide-react";

import AnalysisList from "./AnalysisList";

export default function Sidebar({
  analyses = [],
  activeEvaluationId = null,
  onSelectAnalysis,
  onNewAnalysis,
}) {
  return (
    <aside className="flex h-screen w-[250px] shrink-0 flex-col border-r border-zinc-800 bg-[#0b0e13] text-zinc-100">
      {/* Header */}
      <div className="flex h-16 shrink-0 items-center justify-between border-b border-zinc-800 px-4">
        <div className="flex items-center gap-3">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-lime-300 text-sm font-black text-zinc-950">
            G
          </div>

          <div className="flex flex-col leading-tight">
            <strong className="text-sm font-bold tracking-tight text-zinc-100">
              Griffin
            </strong>

            <span className="mt-0.5 text-[10px] font-medium text-zinc-500">
              Intelligence Console
            </span>
          </div>
        </div>

        <button
          type="button"
          aria-label="Collapse sidebar"
          title="Collapse sidebar"
          className="grid h-8 w-8 place-items-center rounded-md text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200"
        >
          <PanelLeftClose size={17} />
        </button>
      </div>

      {/* Main */}
      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
        <button
          type="button"
          onClick={onNewAnalysis}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-lime-300 bg-lime-300 px-3 py-2.5 text-xs font-bold text-zinc-950 transition hover:bg-lime-200 active:scale-[0.99]"
        >
          <FilePlus2 size={16} />
          <span>New Analysis</span>
        </button>

        {/* Analyses */}
        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-zinc-500">
              Analyses
            </span>

            {analyses.length > 0 && (
              <span className="rounded-md bg-zinc-800 px-1.5 py-0.5 text-[9px] font-semibold text-zinc-400">
                {analyses.length}
              </span>
            )}
          </div>

          <AnalysisList
            analyses={analyses}
            activeEvaluationId={activeEvaluationId}
            onSelect={onSelectAnalysis}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="shrink-0 space-y-1 border-t border-zinc-800 p-3">
        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200"
        >
          <Activity size={17} />
          <span>System</span>

          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-400" />
        </button>

        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200"
        >
          <Settings size={17} />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
}