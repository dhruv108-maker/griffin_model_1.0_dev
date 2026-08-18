// src/components/workspace/AnalysisWorkspace.jsx

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { useParams } from "react-router-dom";
import {
  AlertCircle,
  LoaderCircle,
} from "lucide-react";

import api from "../../api/apis";

import AnalysisHeader from "./AnalysisHeader";
import WorkspaceTabs from "./WorkspaceTabs";
import EmptyAnalysis from "./EmptyAnalysis";

import AnalysisUpload from "../upload/AnalysisUpload";

import Overview from "../results/Overview";
import CurriculumMapping from "../results/CurriculumMapping";
import TopicMapping from "../results/TopicMapping";
import EvidencePanel from "../results/EvidencePanel";
import CoveragePanel from "../results/CoveragePanel";
import GraphPanel from "../results/GraphPanel";
import ReportPanel from "../results/ReportPanel";


const TABS = [
  { id: "overview", label: "Overview" },
  { id: "curriculum", label: "Curriculum" },
  { id: "topics", label: "Topics" },
  { id: "evidence", label: "Evidence" },
  { id: "coverage", label: "Coverage" },
  { id: "graph", label: "Graph" },
  { id: "report", label: "Report" },
];

function normalizeResultResponse(response) {
  if (!response) return { result: null, reportResults: [] };

  if (Array.isArray(response.results)) {
    const reportResults = response.results
      .map((entry) => {
        if (entry?.griffin_result) {
          return {
            report_id: entry.report_id,
            result: entry.griffin_result,
          };
        }
        return {
          report_id: entry?.report_id,
          result: entry,
        };
      })
      .filter((entry) => entry.result);

    return {
      result: reportResults[0]?.result || null,
      reportResults,
    };
  }

  return { result: response, reportResults: [] };
}

export default function AnalysisWorkspace({
  analysis = null,
  result: externalResult = null,
  processing: externalProcessing = false,
  uploadError = null,
  onStartAnalysis,
  onUpload,
}) {
  const { evaluationId: paramEvaluationId } = useParams();

  const evaluationId = analysis?.id || analysis?.evaluation_id || paramEvaluationId;

  const [activeTab, setActiveTab] = useState("overview");
  const [fetchedResult, setFetchedResult] = useState(null);
  const [reportResults, setReportResults] = useState([]);
  const [activeReportId, setActiveReportId] = useState(null);
  const [loadingResult, setLoadingResult] = useState(false);
  const [resultError, setResultError] = useState(null);

  const result = externalResult || fetchedResult;

  useEffect(() => {
    setFetchedResult(null);
    setReportResults([]);
    setActiveReportId(null);
    setResultError(null);
  }, [evaluationId]);

  useEffect(() => {
    if (!evaluationId || evaluationId === "new" || externalResult) return;

    const isCurrentProcessing =
      analysis?.status === "PENDING" || analysis?.status === "PROCESSING";
    if (isCurrentProcessing) return;

    let cancelled = false;

    async function loadResult() {
      try {
        setLoadingResult(true);
        setResultError(null);

        const response = await api.evaluations.result(evaluationId);
        if (cancelled) return;

        const normalized = normalizeResultResponse(response);
        setFetchedResult(normalized.result);
        setReportResults(normalized.reportResults);
        setActiveReportId(normalized.reportResults[0]?.report_id || null);
      } catch (error) {
        if (cancelled) return;
        console.error("Failed to load evaluation result:", error);
        setResultError(error?.message || "Unable to load evaluation result.");
      } finally {
        if (!cancelled) setLoadingResult(false);
      }
    }

    loadResult();
    return () => {
      cancelled = true;
    };
  }, [evaluationId, externalResult, analysis?.status]);

  const selectedReportResult =
    reportResults.find((entry) => String(entry.report_id) === String(activeReportId))?.result ||
    result;

  const hasResult = Boolean(selectedReportResult);
  const hasAnalysis = Boolean(analysis);
  const processing =
    externalProcessing ||
    analysis?.status === "PENDING" ||
    analysis?.status === "PROCESSING" ||
    loadingResult;

  const workspaceState = useMemo(() => {
    if (resultError) return "error";
    if (evaluationId && evaluationId !== "new" && loadingResult && !result) return "loading";
    if (!hasAnalysis && !result) return "empty";
    if (processing && !result) return "processing";
    if (hasResult) return "result";
    if (evaluationId === "new") return "ready";
    return "ready";
  }, [evaluationId, loadingResult, resultError, hasAnalysis, hasResult, processing, result]);

  if (workspaceState === "empty") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#090b0f]">
        <EmptyAnalysis />
      </section>
    );
  }

  if (workspaceState === "loading") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#090b0f] px-6">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-xl border border-zinc-800 bg-zinc-900">
            <LoaderCircle size={22} className="animate-spin text-lime-300" />
          </div>
          <div>
            <p className="text-sm font-semibold text-zinc-200">Loading Griffin analysis</p>
            <p className="mt-1 text-xs text-zinc-500">Fetching stored evaluation results...</p>
          </div>
        </div>
      </section>
    );
  }

  if (workspaceState === "error") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#090b0f] px-6">
        <div className="w-full max-w-md rounded-xl border border-red-500/20 bg-red-500/5 p-6">
          <div className="flex items-start gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-red-500/10">
              <AlertCircle size={18} className="text-red-400" />
            </div>
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-zinc-100">Unable to load analysis</h2>
              <p className="mt-2 text-xs leading-5 text-zinc-500">{resultError}</p>
              {evaluationId && (
                <p className="mt-3 break-all font-mono text-[10px] text-zinc-600">Evaluation: {evaluationId}</p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-5 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-xs font-semibold text-zinc-300 transition hover:border-zinc-600 hover:bg-zinc-800 hover:text-zinc-100"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#090b0f]">
      <AnalysisHeader analysis={analysis} result={selectedReportResult} processing={processing} />

      {reportResults.length > 1 && (
        <div className="border-b border-zinc-900 bg-zinc-950/60 px-4 py-3 sm:px-6">
          <div className="mx-auto flex w-full max-w-[1600px] items-center gap-3 overflow-x-auto">
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
              Reports
            </span>
            {reportResults.map((entry, index) => (
              <button
                key={entry.report_id || index}
                type="button"
                onClick={() => setActiveReportId(entry.report_id)}
                className={`shrink-0 rounded-lg border px-3 py-2 text-xs transition ${
                  String(entry.report_id) === String(activeReportId)
                    ? "border-lime-400/30 bg-lime-400/10 text-lime-200"
                    : "border-zinc-800 bg-zinc-900 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                }`}
              >
                Report {index + 1}
              </button>
            ))}
          </div>
        </div>
      )}

      <WorkspaceTabs
        tabs={TABS}
        activeTab={activeTab}
        onChange={setActiveTab}
        disabled={!hasResult}
      />

      <div className="min-w-0 flex-1 px-4 pb-8 pt-4 sm:px-6">
        <div className="mx-auto w-full max-w-[1600px]">
          {workspaceState === "ready" && (
            <AnalysisUpload
              analysis={analysis}
              onUpload={onUpload}
              onStartAnalysis={onStartAnalysis}
              error={uploadError}
            />
          )}

          {workspaceState === "processing" && (
            <div className="flex min-h-[460px] flex-col rounded-xl border border-zinc-800 bg-zinc-900/30 p-6">
              <div className="mb-6 flex flex-col items-center gap-4 text-center">
                <div className="grid h-12 w-12 place-items-center rounded-xl border border-zinc-800 bg-zinc-900">
                  <LoaderCircle size={22} className="animate-spin text-lime-300" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-zinc-200">Griffin Core Pipeline Execution</p>
                  <p className="mt-1 text-xs text-zinc-500">Strict Curriculum + Student Report Evaluation Contract</p>
                </div>
              </div>

              <div className="mx-auto mb-6 w-full max-w-xl">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Overall Pipeline Progress</span>
                  <span className="text-xs font-semibold text-lime-300">{Math.round(analysis?.progress || 0)}%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full border border-zinc-800/50 bg-zinc-950">
                  <div
                    className="h-full bg-gradient-to-r from-lime-400 to-emerald-400 transition-all duration-300 ease-out"
                    style={{ width: `${analysis?.progress || 0}%` }}
                  />
                </div>
              </div>

              <div className="flex min-h-[220px] flex-1 flex-col rounded-lg border border-zinc-800/80 bg-zinc-950 p-4 font-mono text-[11px] leading-relaxed text-zinc-300 shadow-inner">
                <div className="mb-3 flex items-center justify-between border-b border-zinc-800/60 pb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-500/80 animate-pulse" />
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Live Pipeline Logs</span>
                  </div>
                  <span className="text-[9px] text-zinc-600">backend Griffin stage updates</span>
                </div>
                <div className="max-h-[180px] flex-1 space-y-1.5 overflow-y-auto">
                  {analysis?.logs && analysis.logs.length > 0 ? (
                    analysis.logs.map((log, lidx) => (
                      <div key={lidx} className="flex items-start gap-2">
                        <span className="shrink-0 select-none text-zinc-600">›</span>
                        <span className="whitespace-pre-wrap text-zinc-300">{log}</span>
                      </div>
                    ))
                  ) : (
                    <div className="italic text-zinc-600">Waiting for Griffin Core stage updates...</div>
                  )}
                </div>
              </div>
            </div>
          )}

          {workspaceState === "result" && (
            <div className="min-w-0">
              {activeTab === "overview" && <Overview result={selectedReportResult} />}
              {activeTab === "curriculum" && (
                <CurriculumMapping result={selectedReportResult} mapping={selectedReportResult?.curriculum_mapping} />
              )}
              {activeTab === "topics" && (
                <TopicMapping result={selectedReportResult} mapping={selectedReportResult?.topic_mapping} />
              )}
              {activeTab === "evidence" && (
                <EvidencePanel result={selectedReportResult} evidence={selectedReportResult?.evidence_analysis} />
              )}
              {activeTab === "coverage" && (
                <CoveragePanel result={selectedReportResult} coverage={selectedReportResult?.coverage_analysis} />
              )}
              {activeTab === "graph" && (
                <GraphPanel
                  result={selectedReportResult}
                  statistics={selectedReportResult?.graph_statistics}
                  visualizations={selectedReportResult?.visualizations}
                />
              )}
              {activeTab === "report" && <ReportPanel result={selectedReportResult} />}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
