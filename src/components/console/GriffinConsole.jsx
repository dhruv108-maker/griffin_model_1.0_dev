import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import AnalysisWorkspace from "../workspace/AnalysisWorkspace";
import api from "../../api/apis";

export default function GriffinConsole() {
  const [analyses, setAnalyses] = useState([]);
  const [activeEvaluationId, setActiveEvaluationId] = useState(null);
  const [newAnalysis, setNewAnalysis] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [workspaceId, setWorkspaceId] = useState(null);
  const streams = useRef({});

  const activeAnalysis =
    analyses.find((analysis) => String(analysis.id) === String(activeEvaluationId)) ||
    newAnalysis;

  const closeStream = (evaluationId) => {
    const stream = streams.current[evaluationId];
    if (stream) {
      stream.close();
      delete streams.current[evaluationId];
    }
  };

  const subscribeToEvaluation = (evaluationId) => {
    if (!evaluationId || streams.current[evaluationId]) return;

    const stream = new EventSource(api.evaluations.streamUrl(evaluationId));

    stream.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const status = String(payload.status || "").toUpperCase();

        setAnalyses((prev) =>
          prev.map((analysis) =>
            String(analysis.id) === String(evaluationId)
              ? {
                  ...analysis,
                  status,
                  progress: payload.progress ?? analysis.progress ?? 0,
                  logs: payload.logs || analysis.logs || [],
                  error: payload.error || null,
                  activeReportId: payload.report_id || null,
                  activeStage: payload.stage || null,
                }
              : analysis,
          ),
        );

        if (["COMPLETED", "FAILED", "CANCELLED"].includes(status)) {
          closeStream(evaluationId);
          setProcessing(false);
        }
      } catch (error) {
        setUploadError(`Invalid evaluation status event: ${error.message}`);
      }
    };

    stream.onerror = () => {
      // EventSource automatically reconnects. Keep the stream registered and
      // preserve the processing state during transient network interruptions.
      setUploadError("Live evaluation connection interrupted; reconnecting…");
      setProcessing(true);
    };

    streams.current[evaluationId] = stream;
  };

  useEffect(() => {
    let cancelled = false;

    async function initWorkspace() {
      try {
        let workspaces = await api.workspaces.list();
        if (!Array.isArray(workspaces)) {
          throw new Error("Backend returned an invalid workspace response");
        }

        if (workspaces.length === 0) {
          const workspace = await api.workspaces.create({
            name: "My Griffin Workspace",
            description: "OBL evaluation workspace",
          });
          workspaces = [workspace];
        }

        if (!cancelled) setWorkspaceId(workspaces[0].id);
      } catch (error) {
        if (!cancelled) setUploadError(error.message);
      }
    }

    initWorkspace();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await api.history.project("");
        if (!Array.isArray(history)) return;

        setAnalyses(history);
        history.forEach((analysis) => {
          const status = String(analysis.status || "").toUpperCase();
          if (["PENDING", "PROCESSING"].includes(status)) {
            setProcessing(true);
            subscribeToEvaluation(analysis.id);
          }
        });
      } catch (error) {
        setUploadError(error.message);
      }
    }

    loadHistory();
  }, []);

  useEffect(() => {
    return () => {
      Object.keys(streams.current).forEach(closeStream);
    };
  }, []);

  const handleSelectAnalysis = (analysis) => {
    setActiveEvaluationId(analysis.id);
    setNewAnalysis(null);

    const status = String(analysis.status || "").toUpperCase();
    if (["PENDING", "PROCESSING"].includes(status)) {
      setProcessing(true);
      subscribeToEvaluation(analysis.id);
    }
  };

  const handleNewAnalysis = () => {
    setNewAnalysis({ id: "new", status: "READY" });
    setActiveEvaluationId("new");
    setUploadError(null);
  };

  const handleStartAnalysis = async ({ curriculum, reports }) => {
    if (!workspaceId) {
      setUploadError("No Griffin workspace is available. Check the backend connection.");
      return;
    }

    if (!curriculum || !reports?.length) {
      setUploadError("A curriculum PDF and at least one report PDF are required.");
      return;
    }

    try {
      setUploading(true);
      setUploadError(null);

      const project = await api.projects.create({
        workspace_id: workspaceId,
        name: `OBL Evaluation — ${new Date().toLocaleString()}`,
        description: "Griffin outcome-based learning evaluation",
      });

      const curriculumRecord = await api.curriculum.upload({
        projectId: project.id,
        title: curriculum.name,
        file: curriculum,
      });

      const reportRecords = [];
      for (const report of reports) {
        reportRecords.push(
          await api.reports.upload({
            projectId: project.id,
            studentName: report.name.replace(/\.pdf$/i, ""),
            file: report,
          }),
        );
      }

      const evaluation = await api.evaluations.start({
        project_id: project.id,
        curriculum_id: curriculumRecord.id,
        report_ids: reportRecords.map((report) => report.id),
        name: `Griffin OBL Evaluation — ${new Date().toLocaleString()}`,
      });

      const analysis = {
        ...evaluation,
        id: evaluation.id,
        status: evaluation.status || "PENDING",
        progress: 0,
        logs: [],
        project_id: project.id,
        curriculum_id: curriculumRecord.id,
      };

      setAnalyses((prev) => [analysis, ...prev]);
      setActiveEvaluationId(analysis.id);
      setNewAnalysis(null);
      setProcessing(true);
      subscribeToEvaluation(analysis.id);
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full overflow-hidden bg-[#f7f9fb] text-slate-900">
      <Sidebar
        analyses={analyses}
        activeEvaluationId={activeEvaluationId}
        onSelectAnalysis={handleSelectAnalysis}
        onNewAnalysis={handleNewAnalysis}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="min-w-0 flex-1 overflow-y-auto">
          {activeEvaluationId ? (
            <AnalysisWorkspace
              analysis={activeAnalysis}
              processing={processing || uploading}
              onStartAnalysis={handleStartAnalysis}
              uploadError={uploadError}
            />
          ) : (
            <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6 text-center text-slate-500">
              Select an evaluation from the sidebar or start a new Griffin OBL evaluation.
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
