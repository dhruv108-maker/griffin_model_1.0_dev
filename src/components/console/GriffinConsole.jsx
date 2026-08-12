import { useState, useEffect, useCallback, useRef } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import AnalysisWorkspace from "../workspace/AnalysisWorkspace";
import api from "../../api/apis";

export default function GriffinConsole() {
  const [analyses, setAnalyses] = useState([]);
  const [activeEvaluationId, setActiveEvaluationId] = useState(null);
  
  // Create a pseudo analysis for the 'New Analysis' form
  const [newAnalysis, setNewAnalysis] = useState(null);
  
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  
  const [workspaceId, setWorkspaceId] = useState(null);
  const pollingIntervals = useRef({});

  // Default analysis state
  const activeAnalysis = 
    analyses.find(a => String(a.id || a.evaluation_id) === String(activeEvaluationId)) || 
    newAnalysis;

  // Initialize workspace
  useEffect(() => {
    async function initWorkspace() {
      try {
        let wss = await api.workspaces.list();
        if (!wss || wss.length === 0) {
          const ws = await api.workspaces.create({ name: "Default Workspace", description: "Default Workspace" });
          wss = [ws];
        }
        setWorkspaceId(wss[0].id);
      } catch (err) {
        console.warn("Failed to initialize workspace from API, using fallback", err);
        setWorkspaceId("default-workspace-id");
      }
    }
    initWorkspace();
  }, []);

  const pollEvaluation = useCallback((evalId) => {
    if (pollingIntervals.current[evalId]) {
      clearInterval(pollingIntervals.current[evalId]);
    }

    const interval = setInterval(async () => {
      try {
        const statusRes = await api.evaluations.status(evalId);
        
        setAnalyses(prev => prev.map(a => {
          const aId = a.id || a.evaluation_id || a.evaluationId;
          if (String(aId) === String(evalId)) {
            return {
              ...a,
              status: statusRes.status,
              progress: statusRes.progress_percentage || 0,
              logs: statusRes.logs || []
            };
          }
          return a;
        }));

        if (statusRes.status === "COMPLETED" || statusRes.status === "FAILED") {
          clearInterval(interval);
          delete pollingIntervals.current[evalId];
          setProcessing(false);
        }
      } catch (err) {
        console.warn("Polling failed", err);
      }
    }, 2000);

    pollingIntervals.current[evalId] = interval;
  }, []);

  // Cleanup intervals on unmount
  useEffect(() => {
    return () => {
      Object.values(pollingIntervals.current).forEach(clearInterval);
    };
  }, []);

  // Fetch past analyses (History)
  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await api.history.project(""); 
        if (Array.isArray(history)) {
          setAnalyses(history);
          history.forEach(a => {
            const status = String(a.status || "").toUpperCase();
            if (status === "PENDING" || status === "PROCESSING") {
              setProcessing(true);
              pollEvaluation(a.id || a.evaluation_id || a.evaluationId);
            }
          });
        }
      } catch (err) {
        console.warn("Could not load history", err);
      }
    }
    loadHistory();
  }, [pollEvaluation]);

  const handleSelectAnalysis = (analysis) => {
    const id = analysis.id || analysis.evaluation_id || analysis.evaluationId;
    setActiveEvaluationId(id);
    setNewAnalysis(null);
  };

  const handleNewAnalysis = () => {
    setNewAnalysis({ id: "new", status: "READY" });
    setActiveEvaluationId("new");
  };

  const handleStartAnalysis = async ({ curriculum, reports }) => {
    if (!workspaceId) return;
    
    try {
      setUploading(true);
      setUploadError(null);
      
      // 1. Create a Project
      const project = await api.projects.create({
        workspace_id: workspaceId,
        name: `Analysis ${new Date().toLocaleString()}`,
        description: "Auto-generated project"
      });
      const projectId = project.id;
      
      // 2. Upload Curriculum
      const currRes = await api.curriculum.upload({
        projectId,
        title: curriculum.name,
        file: curriculum
      });
      const curriculumId = currRes.id;
      
      // 3. Upload Reports
      const reportIds = [];
      for (const report of reports) {
        const repRes = await api.reports.upload({
          projectId,
          studentName: report.name.replace('.pdf', ''),
          file: report
        });
        reportIds.push(repRes.id);
      }
      
      // 4. Start Evaluation
      setProcessing(true);
      const evalRes = await api.evaluations.start({
        project_id: projectId,
        curriculum_id: curriculumId,
        report_ids: reportIds,
        name: `Evaluation ${new Date().toLocaleString()}`
      });
      
      const newEval = {
        ...evalRes,
        id: evalRes.id,
        name: evalRes.name || project.name,
        status: evalRes.status || "PROCESSING",
        progress: 0,
        logs: []
      };
      
      setAnalyses(prev => [newEval, ...prev]);
      setActiveEvaluationId(newEval.id);
      setNewAnalysis(null);
      
      // 5. Poll for completion
      pollEvaluation(newEval.id);
      
    } catch (err) {
      console.error("Failed to start analysis", err);
      setUploadError(err?.message || "Failed to start analysis.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full overflow-hidden bg-[#090b0f] text-zinc-100">
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
            <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center text-zinc-500">
              Select an analysis from the sidebar or start a new one.
            </div>
          )}
        </main>
      </div>
    </div>
  );
}