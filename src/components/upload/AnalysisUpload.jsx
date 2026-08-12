import { useCallback, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  FileText,
  FolderOpen,
  Play,
  Trash2,
  UploadCloud,
} from "lucide-react";

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );

  return `${(bytes / 1024 ** index).toFixed(
    index === 0 ? 0 : 1
  )} ${units[index]}`;
}

function FileRow({
  file,
  type,
  onRemove,
}) {
  return (
    <div className="griffin-upload-file">
      <div className="griffin-upload-file-icon">
        <FileText size={18} />
      </div>

      <div className="griffin-upload-file-info">
        <span className="griffin-upload-file-name">
          {file.name}
        </span>

        <span className="griffin-upload-file-meta">
          {type} · {formatBytes(file.size)}
        </span>
      </div>

      <CheckCircle2
        size={16}
        className="griffin-upload-file-valid"
      />

      <button
        type="button"
        className="griffin-upload-remove"
        onClick={() => onRemove(file)}
        aria-label={`Remove ${file.name}`}
        title="Remove file"
      >
        <Trash2 size={15} />
      </button>
    </div>
  );
}

function UploadZone({
  title,
  description,
  accept,
  multiple = false,
  onFiles,
  disabled = false,
}) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const files = Array.from(fileList || []);

      if (!files.length) return;

      onFiles(files);
    },
    [onFiles]
  );

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);

    if (disabled) return;

    handleFiles(event.dataTransfer.files);
  };

  const handleChange = (event) => {
    handleFiles(event.target.files);

    // Allow selecting the same file again.
    event.target.value = "";
  };

  return (
    <div
      className={`griffin-upload-zone ${
        dragging ? "is-dragging" : ""
      } ${disabled ? "is-disabled" : ""}`}
      onDragEnter={(event) => {
        event.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={(event) => {
        event.preventDefault();

        if (
          event.currentTarget === event.target ||
          !event.currentTarget.contains(event.relatedTarget)
        ) {
          setDragging(false);
        }
      }}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        disabled={disabled}
        hidden
      />

      <div className="griffin-upload-zone-icon">
        <UploadCloud size={22} />
      </div>

      <div className="griffin-upload-zone-content">
        <strong>{title}</strong>

        <span>{description}</span>

        <button
          type="button"
          className="griffin-upload-browse"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
        >
          <FolderOpen size={15} />
          Browse files
        </button>
      </div>
    </div>
  );
}

export default function AnalysisUpload({
  analysis = null,
  curriculumFile = null,
  reportFiles = [],
  onCurriculumChange,
  onReportsChange,
  onUpload,
  onStartAnalysis,
  uploading = false,
  disabled = false,
  error = null,
}) {
  const [localCurriculum, setLocalCurriculum] =
    useState(curriculumFile);

  const [localReports, setLocalReports] =
    useState(reportFiles);

  const [validationError, setValidationError] =
    useState("");

  const curriculum =
    curriculumFile ?? localCurriculum;

  const reports =
    reportFiles?.length
      ? reportFiles
      : localReports;

  const validatePdfFiles = (files) => {
    const invalid = files.find(
      (file) =>
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    );

    if (invalid) {
      setValidationError(
        `"${invalid.name}" is not a PDF file. Griffin accepts PDF documents.`
      );
      return false;
    }

    setValidationError("");
    return true;
  };

  const handleCurriculumFiles = (files) => {
    const file = files[0];

    if (!file || !validatePdfFiles([file])) {
      return;
    }

    setLocalCurriculum(file);
    onCurriculumChange?.(file);
  };

  const handleReportFiles = (files) => {
    if (!validatePdfFiles(files)) {
      return;
    }

    setLocalReports((previous) => {
      const existing = new Map(
        previous.map((file) => [
          `${file.name}-${file.size}-${file.lastModified}`,
          file,
        ])
      );

      files.forEach((file) => {
        existing.set(
          `${file.name}-${file.size}-${file.lastModified}`,
          file
        );
      });

      return Array.from(existing.values());
    });

    const merged = [
      ...reports,
      ...files,
    ].filter(
      (file, index, array) =>
        array.findIndex(
          (item) =>
            item.name === file.name &&
            item.size === file.size &&
            item.lastModified === file.lastModified
        ) === index
    );

    onReportsChange?.(merged);
  };

  const removeCurriculum = () => {
    setLocalCurriculum(null);
    onCurriculumChange?.(null);
  };

  const removeReport = (fileToRemove) => {
    const next = reports.filter(
      (file) => file !== fileToRemove
    );

    setLocalReports(next);
    onReportsChange?.(next);
  };

  const canStart =
    Boolean(curriculum) &&
    reports.length > 0 &&
    !uploading &&
    !disabled;

  const handleStart = async () => {
    if (!canStart) return;

    setValidationError("");

    if (onStartAnalysis) {
      await onStartAnalysis({
        curriculum,
        reports,
        analysis,
      });
    }
  };

  return (
    <section className="griffin-upload-workspace">
      <div className="griffin-upload-heading">
        <div>
          <span className="griffin-eyebrow">
            NEW ANALYSIS
          </span>

          <h2>
            Prepare documents for Griffin
          </h2>

          <p>
            Provide the curriculum that defines the
            expected knowledge structure and the
            report documents Griffin should evaluate.
          </p>
        </div>
      </div>

      {(error || validationError) && (
        <div className="griffin-upload-error">
          <AlertCircle size={17} />

          <span>
            {validationError || error}
          </span>
        </div>
      )}

      <div className="griffin-upload-grid">
        <div className="griffin-upload-card">
          <div className="griffin-upload-card-header">
            <div>
              <span className="griffin-upload-card-kicker">
                REQUIRED
              </span>

              <h3>Curriculum</h3>

              <p>
                Upload the curriculum PDF Griffin
                should use as the reference structure.
              </p>
            </div>

            <div className="griffin-upload-card-number">
              01
            </div>
          </div>

          {!curriculum ? (
            <UploadZone
              title="Drop curriculum PDF here"
              description="One curriculum document"
              accept=".pdf,application/pdf"
              onFiles={handleCurriculumFiles}
              disabled={uploading || disabled}
            />
          ) : (
            <div className="griffin-upload-selected">
              <FileRow
                file={curriculum}
                type="Curriculum"
                onRemove={removeCurriculum}
              />
            </div>
          )}
        </div>

        <div className="griffin-upload-card">
          <div className="griffin-upload-card-header">
            <div>
              <span className="griffin-upload-card-kicker">
                REQUIRED
              </span>

              <h3>Reports</h3>

              <p>
                Upload one or more report PDFs for
                evidence and curriculum alignment.
              </p>
            </div>

            <div className="griffin-upload-card-number">
              02
            </div>
          </div>

          <UploadZone
            title="Drop report PDFs here"
            description="Multiple PDF documents supported"
            accept=".pdf,application/pdf"
            multiple
            onFiles={handleReportFiles}
            disabled={uploading || disabled}
          />

          {reports.length > 0 && (
            <div className="griffin-upload-selected-list">
              {reports.map((file) => (
                <FileRow
                  key={`${file.name}-${file.size}-${file.lastModified}`}
                  file={file}
                  type="Report"
                  onRemove={removeReport}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="griffin-upload-footer">
        <div className="griffin-upload-summary">
          <span>
            {curriculum
              ? "Curriculum ready"
              : "Curriculum required"}
          </span>

          <span>
            {reports.length}{" "}
            {reports.length === 1
              ? "report"
              : "reports"}{" "}
            selected
          </span>
        </div>

        <div className="griffin-upload-actions">
          <button
            type="button"
            className="griffin-primary-button"
            disabled={!canStart}
            onClick={handleStart}
          >
            <Play size={16} />

            <span>
              {uploading
                ? "Preparing…"
                : "Start Griffin Analysis"}
            </span>
          </button>
        </div>
      </div>
    </section>
  );
}