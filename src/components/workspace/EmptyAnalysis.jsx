import {
  ArrowRight,
  FileSearch,
  Network,
  Sparkles,
} from "lucide-react";

export default function EmptyAnalysis({
  onStart,
}) {
  return (
    <section className="griffin-empty-analysis">
      <div className="griffin-empty-analysis-inner">
        <div className="griffin-empty-icon">
          <FileSearch size={28} />
        </div>

        <span className="griffin-eyebrow">
          GRIFFIN ANALYSIS ENGINE
        </span>

        <h1>
          Turn curriculum and reports
          <br />
          into structured evidence.
        </h1>

        <p>
          Upload a curriculum and supporting
          reports to evaluate coverage, evidence,
          confidence, and curriculum alignment.
        </p>

        <button
          type="button"
          className="griffin-primary-button"
          onClick={onStart}
        >
          <Sparkles size={16} />
          <span>Start New Analysis</span>
          <ArrowRight size={16} />
        </button>

        <div className="griffin-empty-capabilities">
          <div className="griffin-capability">
            <FileSearch size={17} />
            <span>Evidence mapping</span>
          </div>

          <div className="griffin-capability">
            <Network size={17} />
            <span>Curriculum graph</span>
          </div>

          <div className="griffin-capability">
            <Sparkles size={17} />
            <span>Semantic evaluation</span>
          </div>
        </div>
      </div>
    </section>
  );
}