import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { AlertCircle, LoaderCircle } from "lucide-react";

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

function unwrapStoredResult(response) {
  if (!response) return null;
  if (response.griffin_result) return response.griffin_result;
  if (Array.isArray(response)) {
    return response[0]?.griffin_result || response[0] || null;
  }
  if (Array.isArray(response.results)) {
    const first = response.results[0];
    return first?.griffin_result || first || null;
  }
  return response;
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
  const [loadingResult, setLoadingResult] = useState(false);
  const [resultError, setResultError] = useState(null);

  const result = externalResult || fetchedResult;

  useEffect(() => {
    setFetchedResult(null);
    setResultError(null);
  }, [evaluationId]);

  useEffect(() => {
    if (!evaluationId || evaluationId === "new" || externalResult) return;

    const status = String(analysis?.status || "").toUpperCase();
    if (["PENDING", "PROCESSING"].includes(status)) return;

    let cancelled = false;

    async function loadResult() {
      try {
        setLoadingResult(true);
        setResultError(null);
        const response = await api.evaluations.result(evaluationId);
        if (!cancelled) setFetchedResult(unwrapStoredResult(response));
      } catch (error) {
        if (!cancelled) setResultError(error.message || "Unable to load evaluation result.");
      } finally {
        if (!cancelled) setLoadingResult(false);
      }
    }

    loadResult();
    return () => {
      cancelled = true;
    };
  }, [evaluationId, externalResult, analysis?.status]);

  const hasResult = Boolean(result);
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
    return evaluationId === "new" ? "ready" : "ready";
  }, [evaluationId, loadingResult, resultError, hasAnalysis, hasResult, processing, result]);

  if (workspaceState === "empty") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#f7f9fb]">
        <EmptyAnalysis />
      </section>
    );
  }

  if (workspaceState === "loading") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#f7f9fb] px-6">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-xl border border-slate-200 bg-white">
            <LoaderCircle size={22} className="animate-spin text-slate-700" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">Loading Griffin analysis</p>
            <p className="mt-1 text-xs text-slate-500">Fetching the stored evaluation result…</p>
          </div>
        </div>
      </section>
    );
  }

  if (workspaceState === "error") {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#f7f9fb] px-6">
        <div className="w-full max-w-md rounded-xl border border-red-200 bg-white p-6 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-red-50">
              <AlertCircle size={18} className="text-red-600" />
            </div>
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-slate-900">Unable to load analysis</h2>
              <p className="mt-2 text-xs leading-5 text-slate-500">{resultError}</p>
              {evaluationId && (
                <p className="mt-3 break-all font-mono text-[10px] text-slate-400">Evaluation: {evaluationId}</p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#f7f9fb]">
      <AnalysisHeader analysis={analysis} result={result} processing={processing} />
      <WorkspaceTabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} disabled={!hasResult} />

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
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
              <div className="flex items-center gap-4">
                <LoaderCircle size={22} className="animate-spin text-slate-700" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">Griffin is evaluating the submitted work</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Progress reported by the backend: {analysis?.progress ?? 0}%
                  </p>
                </div>
              </div>
              {analysis?.logs?.length > 0 && (
                <div className="mt-6 max-h-48 overflow-auto rounded-xl bg-slate-50 p-4 font-mono text-[11px] text-slate-500">
                  {analysis.logs.map((log, index) => (
                    <div key={`${index}-${log}`}>{log}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {workspaceState === "result" && (
            <>
              {activeTab === "overview" && <Overview result={result} />}
              {activeTab === "curriculum" && <CurriculumMapping result={result} />}
              {activeTab === "topics" && <TopicMapping result={result} />}
              {activeTab === "evidence" && <EvidencePanel result={result} />}
              {activeTab === "coverage" && <CoveragePanel result={result} />}
              {activeTab === "graph" && <GraphPanel result={result} />}
              {activeTab === "report" && <ReportPanel result={result} />}
            </>
          )}
        </div>
      </div>
    </section>
  );
}
