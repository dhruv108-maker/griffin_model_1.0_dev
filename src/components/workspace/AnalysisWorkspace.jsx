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
  {
    id: "overview",
    label: "Overview",
  },
  {
    id: "curriculum",
    label: "Curriculum",
  },
  {
    id: "topics",
    label: "Topics",
  },
  {
    id: "evidence",
    label: "Evidence",
  },
  {
    id: "coverage",
    label: "Coverage",
  },
  {
    id: "graph",
    label: "Graph",
  },
  {
    id: "report",
    label: "Report",
  },
];


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

  const [activeTab, setActiveTab] =
    useState("overview");

  const [fetchedResult, setFetchedResult] =
    useState(null);

  const [loadingResult, setLoadingResult] =
    useState(false);

  const [resultError, setResultError] =
    useState(null);


  /*
   * ----------------------------------------------------------
   * RESULT SOURCE
   * ----------------------------------------------------------
   *
   * If GriffinConsole already supplied a result,
   * use it.
   *
   * Otherwise, when opened through:
   *
   * /analysis/:evaluationId
   *
   * fetch the result directly from the backend.
   */

  const result =
    externalResult || fetchedResult;


  /*
   * ----------------------------------------------------------
   * RESET RESULT ON CHANGE
   * ----------------------------------------------------------
   */

  useEffect(() => {
    setFetchedResult(null);
    setResultError(null);
  }, [evaluationId]);


  /*
   * ----------------------------------------------------------
   * LOAD EVALUATION RESULT
   * ----------------------------------------------------------
   */

  useEffect(() => {
    if (!evaluationId || evaluationId === "new") {
      return;
    }

    // Don't refetch if parent already supplied result.
    if (externalResult) {
      return;
    }

    // If analysis status is explicitly pending or processing, wait.
    const isCurrentProcessing = analysis?.status === "PENDING" || analysis?.status === "PROCESSING";
    if (isCurrentProcessing) {
      return;
    }

    let cancelled = false;

    async function loadResult() {
      try {
        setLoadingResult(true);
        setResultError(null);

        const response =
          await api.evaluations.result(
            evaluationId
          );

        if (cancelled) {
          return;
        }

        /*
         * Backend result endpoint may return:
         *
         * {
         *   evaluation_id,
         *   results: [...]
         * }
         *
         * or a direct Griffin result payload.
         *
         * Normalize both cases.
         */

        let normalizedResult =
          response;

        if (
          response &&
          Array.isArray(response.results)
        ) {
          if (response.results.length === 1) {
            normalizedResult =
              response.results[0];
          } else {
            normalizedResult = {
              ...response,
              results: response.results,
            };
          }
        }

        setFetchedResult(
          normalizedResult
        );
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error(
          "Failed to load evaluation result:",
          error
        );

        setResultError(
          error?.message ||
            "Unable to load evaluation result."
        );
      } finally {
        if (!cancelled) {
          setLoadingResult(false);
        }
      }
    }

    loadResult();

    return () => {
      cancelled = true;
    };
  }, [evaluationId, externalResult, analysis?.status]);


  /*
   * ----------------------------------------------------------
   * WORKSPACE STATE
   * ----------------------------------------------------------
   */

  const hasResult =
    Boolean(result);

  const hasAnalysis =
    Boolean(analysis);

  const processing =
    (analysis?.status === "PENDING" || analysis?.status === "PROCESSING") ||
    loadingResult;


  const workspaceState = useMemo(() => {
    if (resultError) {
      return "error";
    }

    if (
      evaluationId &&
      evaluationId !== "new" &&
      loadingResult &&
      !result
    ) {
      return "loading";
    }

    if (!hasAnalysis && !result) {
      return "empty";
    }

    if (processing && !result) {
      return "processing";
    }

    if (hasResult) {
      return "result";
    }

    if (evaluationId === "new") {
      return "ready";
    }

    // Default for an active analysis that has no result yet (should rarely hit this directly if not loading)
    return "ready";
  }, [
    evaluationId,
    loadingResult,
    resultError,
    hasAnalysis,
    hasResult,
    processing,
    result,
  ]);


  /*
   * ----------------------------------------------------------
   * EMPTY STATE
   * ----------------------------------------------------------
   */

  if (
    workspaceState === "empty"
  ) {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#090b0f]">
        <EmptyAnalysis />
      </section>
    );
  }


  /*
   * ----------------------------------------------------------
   * LOADING STATE
   * ----------------------------------------------------------
   */

  if (
    workspaceState === "loading"
  ) {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#090b0f] px-6">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-xl border border-zinc-800 bg-zinc-900">
            <LoaderCircle
              size={22}
              className="animate-spin text-lime-300"
            />
          </div>

          <div>
            <p className="text-sm font-semibold text-zinc-200">
              Loading Griffin analysis
            </p>

            <p className="mt-1 text-xs text-zinc-500">
              Fetching evaluation results...
            </p>
          </div>
        </div>
      </section>
    );
  }


  /*
   * ----------------------------------------------------------
   * ERROR STATE
   * ----------------------------------------------------------
   */

  if (
    workspaceState === "error"
  ) {
    return (
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#090b0f] px-6">
        <div className="w-full max-w-md rounded-xl border border-red-500/20 bg-red-500/5 p-6">
          <div className="flex items-start gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-red-500/10">
              <AlertCircle
                size={18}
                className="text-red-400"
              />
            </div>

            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-zinc-100">
                Unable to load analysis
              </h2>

              <p className="mt-2 text-xs leading-5 text-zinc-500">
                {resultError}
              </p>

              {evaluationId && (
                <p className="mt-3 break-all font-mono text-[10px] text-zinc-600">
                  Evaluation: {evaluationId}
                </p>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              window.location.reload();
            }}
            className="mt-5 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-xs font-semibold text-zinc-300 transition hover:border-zinc-600 hover:bg-zinc-800 hover:text-zinc-100"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }


  /*
   * ----------------------------------------------------------
   * WORKSPACE
   * ----------------------------------------------------------
   */

  return (
    <section className="flex min-h-[calc(100vh-4rem)] min-w-0 flex-col bg-[#090b0f]">

      {/* Analysis header */}
      <AnalysisHeader
        analysis={analysis}
        result={result}
        processing={processing}
      />

      {/* Tabs */}
      <WorkspaceTabs
        tabs={TABS}
        activeTab={activeTab}
        onChange={setActiveTab}
        disabled={!hasResult}
      />

      {/* Content */}
      <div className="min-w-0 flex-1 px-4 pb-8 pt-4 sm:px-6">
        <div className="mx-auto w-full max-w-[1600px]">

          {/* READY */}
          {workspaceState === "ready" && (
            <AnalysisUpload
              analysis={analysis}
              onUpload={onUpload}
              onStartAnalysis={
                onStartAnalysis
              }
              error={uploadError}
            />
          )}


          {/* PROCESSING */}
          {workspaceState === "processing" && (
            <div className="flex min-h-[460px] flex-col rounded-xl border border-zinc-800 bg-zinc-900/30 p-6">
              <div className="flex flex-col items-center gap-4 text-center mb-6">
                <div className="grid h-12 w-12 place-items-center rounded-xl border border-zinc-800 bg-zinc-900">
                  <LoaderCircle
                    size={22}
                    className="animate-spin text-lime-300"
                  />
                </div>

                <div>
                  <p className="text-sm font-semibold text-zinc-200">
                    Griffin Core Pipeline Execution
                  </p>
                  <p className="mt-1 text-xs text-zinc-500">
                    Strict Curriculum + Student Report Evaluation Contract
                  </p>
                </div>
              </div>

              {/* Progress Bar Container */}
              <div className="w-full max-w-xl mx-auto mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[11px] font-medium text-zinc-400 uppercase tracking-wider">Overall Pipeline Progress</span>
                  <span className="text-xs font-semibold text-lime-300">{Math.round(analysis?.progress || 0)}%</span>
                </div>
                <div className="h-2 w-full bg-zinc-950 rounded-full overflow-hidden border border-zinc-800/50">
                  <div 
                    className="h-full bg-gradient-to-r from-lime-400 to-emerald-400 transition-all duration-300 ease-out"
                    style={{ width: `${analysis?.progress || 0}%` }}
                  />
                </div>
              </div>

              {/* Live Console Logs Terminal */}
              <div className="flex-1 flex flex-col min-h-[220px] rounded-lg border border-zinc-800/80 bg-zinc-950 p-4 font-mono text-[11px] leading-relaxed text-zinc-300 shadow-inner">
                <div className="flex items-center justify-between border-b border-zinc-800/60 pb-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-500/80 animate-pulse" />
                    <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">Live Pipeline Logs</span>
                  </div>
                  <span className="text-[9px] text-zinc-600">pipeline.py only</span>
                </div>
                <div className="flex-1 overflow-y-auto space-y-1.5 scrollbar-thin scrollbar-thumb-zinc-800 max-h-[180px]">
                  {analysis?.logs && analysis.logs.length > 0 ? (
                    analysis.logs.map((log, lidx) => (
                      <div key={lidx} className="flex gap-2 items-start">
                        <span className="text-zinc-600 shrink-0 select-none">›</span>
                        <span className="text-zinc-300 whitespace-pre-wrap">{log}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-zinc-600 italic">Initializing pipeline workers and loading PDF resources...</div>
                  )}
                </div>
              </div>
            </div>
          )}


          {/* RESULTS */}
          {workspaceState === "result" && (
            <div
              id={`panel-${activeTab}`}
              role="tabpanel"
              aria-labelledby={`tab-${activeTab}`}
              tabIndex={0}
              className="min-w-0 focus:outline-none"
            >

              {activeTab === "overview" && (
                <Overview
                  result={result}
                />
              )}

              {activeTab === "curriculum" && (
                <CurriculumMapping
                  result={result}
                  mapping={
                    result?.curriculum_mapping
                  }
                />
              )}

              {activeTab === "topics" && (
                <TopicMapping
                  result={result}
                  mapping={
                    result?.topic_mapping
                  }
                />
              )}

              {activeTab === "evidence" && (
                <EvidencePanel
                  result={result}
                  evidence={
                    result?.evidence_analysis
                  }
                />
              )}

              {activeTab === "coverage" && (
                <CoveragePanel
                  result={result}
                  coverage={
                    result?.coverage_analysis
                  }
                />
              )}

              {activeTab === "graph" && (
                <GraphPanel
                  result={result}
                  statistics={
                    result?.graph_statistics
                  }
                  visualizations={
                    result?.visualizations
                  }
                />
              )}

              {activeTab === "report" && (
                <ReportPanel
                  result={result}
                />
              )}

            </div>
          )}

        </div>
      </div>
    </section>
  );
}