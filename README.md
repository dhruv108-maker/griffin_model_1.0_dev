# Griffin — OBL Evaluation AI v1.0

Griffin is an explainable academic evaluation platform for outcome-based learning (OBL). It maps curriculum topics to evidence in student reports and presents the stored GriffinResult for review.

## Product flow

```text
Curriculum PDF + Student Report(s)
            ↓
      Griffin Core (frozen)
            ↓
        GriffinResult
            ↓
      Persisted evaluation
            ↓
      Griffin Console / Report
```

The product layer deliberately does not reimplement Griffin evaluation logic. Curriculum parsing, tokenization, encoding, retrieval, validation, evidence graph construction, and result generation remain in Griffin Core.

## Stack

Backend: FastAPI, SQLAlchemy, PostgreSQL-compatible database, Pydantic, existing Griffin Core.

Frontend: React, Vite, TypeScript build tooling, Tailwind CSS, React Router.

## Backend configuration

Copy `.env.example` to the deployment environment and set a real `DATABASE_URL` and `CORS_ORIGINS`.

`GRIFFIN_ALLOW_LOCAL_SQLITE=true` is intended only for local development. Production must provide `DATABASE_URL` and must not rely on the SQLite fallback.

Uploaded PDFs are stored under `STORAGE_DIR` using generated filenames. Original filenames are retained only as report/curriculum metadata.

## Run locally

```bash
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

In a second terminal:

```bash
npm install
npm run dev
```

The Vite development proxy sends `/api/*` to the FastAPI service.

## Evaluation contract

A completed evaluation stores one `GriffinResult` for each submitted report. Opening an existing evaluation reads the stored result; it does not rerun Griffin Core.

Processing state comes from the backend job record. The UI does not fabricate completion percentages, model thoughts, evaluation verdicts, or evidence.

## Release boundary

This branch is the Griffin v1.0 release candidate. The frozen Griffin Core is treated as the source of truth; release work is limited to the product wrapper, persistence, API lifecycle, uploads, and presentation integration.

See `griffin_project_final_stage.md` for the product finalisation contract.
