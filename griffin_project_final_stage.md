# Griffin v1.0 — Product Finalisation Contract

## 1. Product Definition

Griffin is an explainable curriculum-mapping and academic report evaluation platform.

Core flow:

```text
Curriculum PDF
+
Student Report(s)
        ↓
Griffin Core
        ↓
GriffinResult
        ↓
Analysis + Report
```

Griffin Core already exists and works.

This finalisation phase must build the **product wrapper around Griffin Core**, not modify Griffin Core itself.

The remaining work is:

1. Product backend
2. Database persistence
3. FastAPI routes/services
4. Frontend application
5. Report presentation/export

---

# 2. Strict Development Rules

## Griffin Core Is Frozen

Do NOT rewrite or redesign:

* Griffin Core
* Curriculum parser
* Report tokenizer
* Encoders
* Retrieval
* Validation
* Evidence graph
* Evaluation logic
* Existing result generation
* Existing GriffinResult schemas

Existing Griffin output is the source of truth.

## Forbidden

Do NOT:

* Create fake Griffin results
* Create mock evaluation statistics
* Fabricate processing progress
* Calculate evaluation conclusions in the frontend
* Duplicate Griffin logic in product services
* Reimplement model logic in API routes
* Add unrelated admin functionality
* Add model-monitoring dashboards
* Add benchmark/model explorer screens
* Introduce unnecessary microservices
* Add unnecessary queues or orchestration
* Over-engineer the frontend
* Create duplicate API clients
* Create duplicate state-management systems
* Add features outside this specification

The product layer should be a **thin, readable wrapper around the existing Griffin engine**.

---

# 3. Technology

## Backend

* FastAPI
* Python
* SQLAlchemy
* PostgreSQL
* Pydantic
* Existing Griffin Core

## Frontend

* React
* Vite
* TypeScript
* TailwindCSS
* React Router
* TanStack Query
* Axios
* Recharts

## Authentication

* Firebase Authentication

---

# 4. Required Architecture

```text
React UI
   ↓
Frontend API Client
   ↓
FastAPI Routes
   ↓
Product Services
   ↓
Existing Griffin Core
   ↓
GriffinResult
   ↓
Database
   ↓
FastAPI
   ↓
Frontend Presentation
```

Routes must remain thin.

Services only coordinate product operations and existing Griffin functionality.

No ML/evaluation logic belongs in routes or product services.

The frontend must never reproduce Griffin's evaluation logic.

---

# 5. Frontend Architecture

Keep the frontend simple and predictable.

Recommended structure:

```text
src/
├── api/
│   ├── client.ts
│   ├── auth.ts
│   ├── projects.ts
│   ├── curricula.ts
│   ├── reports.ts
│   ├── evaluations.ts
│   └── results.ts
│
├── components/
│   ├── ui/
│   ├── projects/
│   ├── evaluation/
│   ├── reports/
│   └── analytics/
│
├── pages/
│   ├── LandingPage.tsx
│   ├── LoginPage.tsx
│   ├── SignupPage.tsx
│   ├── ProjectsPage.tsx
│   ├── ConsolePage.tsx
│   ├── ProjectDashboardPage.tsx
│   ├── ReportsPage.tsx
│   ├── EvaluationReportPage.tsx
│   └── CurriculumGraphPage.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useProjects.ts
│   ├── useCurriculum.ts
│   ├── useReports.ts
│   ├── useEvaluations.ts
│   └── useGriffinResult.ts
│
├── context/
│   └── AuthContext.tsx
│
└── types/
```

Do not create additional architectural layers unless they solve a real problem.

---

# 6. Frontend API Wrapper

There must be one central HTTP client.

```text
UI
 ↓
Feature API Function
 ↓
api/client.ts
 ↓
FastAPI
```

The UI must not directly call Axios/fetch.

Do not scatter API URLs throughout components.

## Core API Wrapper

The API client must provide:

```ts
request()
get()
post()
put()
delete()
upload()
```

It must centrally handle:

* Base URL
* Firebase authentication token
* JSON headers
* Multipart uploads
* HTTP errors
* Response parsing
* Timeout handling where required

The client must preserve the real backend error.

Never convert every failure into a generic message such as:

```text
Failed to fetch data
```

Errors should retain:

```text
status
endpoint
backend detail
```

---

# 7. Frontend API Functions

Create small feature-level functions.

## Authentication

```ts
getCurrentUser()
```

```text
Firebase ID Token
        ↓
GET /auth/me
        ↓
Current application user
```

Firebase remains the authentication authority.

Do not create a second frontend authentication system.

Do not create fallback/fake users when `/auth/me` fails.

---

## Projects

Provide:

```ts
getProjects()
getProject(projectId)
createProject(data)
updateProject(projectId, data)
deleteProject(projectId)
```

---

## Curriculum

Provide:

```ts
uploadCurriculum(projectId, file)
getProjectCurriculum(projectId)
selectExistingCurriculum(projectId, curriculumId)
deleteCurriculum(projectId, curriculumId)
```

---

## Reports

Provide:

```ts
uploadReport(projectId, file)
uploadReports(projectId, files)
getReports(projectId, params)
getReport(projectId, reportId)
deleteReport(projectId, reportId)
```

---

## Evaluation

Provide:

```ts
startEvaluation(projectId, data)
getEvaluation(projectId, evaluationId)
getEvaluationStatus(projectId, evaluationId)
cancelEvaluation(projectId, evaluationId)
```

For bulk evaluation:

```ts
startBulkEvaluation(projectId, data)
getBatchStatus(projectId, batchId)
```

---

## Griffin Results

Provide:

```ts
getGriffinResult(projectId, evaluationId)
getProjectResults(projectId, params)
```

The frontend displays stored GriffinResults.

It must never recompute Griffin results.

---

## Downloads

Provide:

```ts
downloadEvaluationPdf(projectId, evaluationId)
downloadEvaluationCsv(projectId, evaluationId)
downloadEvaluationTxt(projectId, evaluationId)
```

Downloads must use stored results.

They must never rerun evaluation.

---

# 8. React Query Usage

Use TanStack Query for server state.

Do not create manual global state for server data.

Use query keys based on project identity.

Example:

```ts
["projects"]

["project", projectId]

["curriculum", projectId]

["reports", projectId]

["evaluations", projectId]

["evaluation", projectId, evaluationId]

["griffin-result", projectId, evaluationId]

["project-results", projectId]
```

Mutations should invalidate only the affected queries.

Do not refetch the entire application after every mutation.

---

# 9. Authentication Flow

```text
Firebase Login
      ↓
Firebase Auth State
      ↓
Firebase ID Token
      ↓
GET /api/v1/auth/me
      ↓
Current Application User
      ↓
Protected Application
```

Authentication state should have only three meaningful states:

```text
loading
authenticated
unauthenticated
```

Do not use fake application users when backend authentication fails.

If Firebase authentication succeeds but `/auth/me` fails, show the actual backend authentication error.

Do not silently continue into the application with incomplete user state.

---

# 10. Exact User Flow

```text
Landing Page
      ↓
Try Griffin
      ↓
Authentication
      ↓
Projects
      ↓
Create Project / Open Project
      ↓
Project Griffin Console
      ↓
Curriculum Input
+
Report Input
      ↓
Evaluation
      ↓
Processing
      ↓
Stored GriffinResult
      ↓
Project Dashboard / Individual Report
      ↓
Download
```

Do not introduce additional mandatory steps.

---

# 11. Landing Page

Public product website.

Purpose:

Explain Griffin clearly and convince serious academic users to try it.

Primary message:

```text
Curriculum + Student Work
        ↓
Evidence Mapping
        ↓
Explainable Evaluation
```

Primary action:

```text
Try Griffin
```

The landing page must be:

* Professional
* Minimal
* Informative
* Visually thoughtful
* Credible for academic/institutional users

It must not look like a generic AI SaaS template.

---

# 12. Authentication UI

Support:

* Sign in
* Sign up
* Google sign-in
* Password reset
* Logout

Authentication is only the gateway to Griffin.

Protected application routes must require authenticated application state.

---

# 13. Projects

Projects are the primary organizational unit.

Users can:

* Create project
* Open project
* Rename project
* Delete project
* View existing projects

Each project owns:

```text
Project
├── Curriculum
├── Reports
├── Evaluations
└── GriffinResults
```

Database relationships must preserve project ownership.

---

# 14. Griffin Console

Every project opens its own Griffin Console.

This is the primary application screen.

The console must not become a generic dashboard.

Primary interaction:

```text
Curriculum
+
Report(s)
      ↓
Evaluate
```

---

# 15. Curriculum Input

Support:

* Curriculum PDF upload
* Existing project curriculum selection

One project curriculum can evaluate multiple reports.

Frontend responsibilities:

```text
Select/upload curriculum
        ↓
Send to backend
        ↓
Display stored curriculum
```

The frontend must not parse or interpret curriculum content.

---

# 16. Report Input

## Single Evaluation

Support:

* PDF upload
* Existing report selection
* Valid backend-supported report path

## Bulk Evaluation

Support:

* Multiple PDF upload
* Folder upload/path where supported by backend

Every report must be evaluated independently.

Every report receives its own GriffinResult.

---

# 17. Evaluation

Start Evaluation must execute the real existing Griffin pipeline.

## Single

```text
Curriculum + Report
        ↓
Griffin Core
        ↓
GriffinResult
```

## Bulk

```text
Curriculum + Report 1 → GriffinResult 1
Curriculum + Report 2 → GriffinResult 2
Curriculum + Report N → GriffinResult N
```

Never merge separate report evaluations into one evaluation result.

---

# 18. Evaluation Frontend Wrapper

The frontend evaluation wrapper should contain only orchestration.

```text
User Action
    ↓
startEvaluation()
    ↓
FastAPI
    ↓
Evaluation Job
    ↓
Existing Griffin Core
    ↓
Stored GriffinResult
    ↓
React Query refresh/invalidation
    ↓
Result UI
```

The frontend must not:

* calculate mapping
* calculate significance
* calculate Bloom level
* calculate confidence
* generate verdicts
* reproduce evidence logic
* calculate evaluation scores

All evaluation conclusions come from GriffinResult.

---

# 19. Processing UI

Display only real backend state.

Allowed states:

```text
Queued
Processing
Completed
Failed
```

If the backend exposes real stages, display them.

Never fabricate:

* Percentages
* Logs
* Stage completion
* Processing times
* AI thoughts
* Evaluation conclusions

For bulk evaluation:

```text
Total Reports
Completed
Processing
Queued
Failed
```

All values must come from backend state.

---

# 20. Database

Persist product data.

Required entities:

```text
users
projects
curricula
reports
evaluations
griffin_results
batch_jobs
```

Store GriffinResult after evaluation.

Completed evaluations must not be recomputed whenever a user opens the project.

Frontend reads stored results.

---

# 21. Project Dashboard

Every project has a dashboard based only on its evaluated reports.

Display:

* Total reports
* Evaluated reports
* Average curriculum mapping
* Average Griffin score where available
* Subject mapping
* Significance distribution
* Bloom distribution where available
* Top 5 curriculum-mapped reports
* Report ranking
* Recent evaluations

Charts are limited to:

* Bar
* Pie
* Radial

All values must come from stored GriffinResults.

The dashboard may aggregate existing numeric result fields.

It must never invent evaluation conclusions.

---

# 22. Reports Library

A project contains a report library.

Display:

* Report name
* Metadata
* Evaluation status
* Mapping percentage
* Significance
* Bloom level
* Evaluation date

Support:

* Search
* Sort
* Filter
* Open report
* Download
* Delete where appropriate

---

# 23. Individual Griffin Report

Each evaluated student report opens a dedicated Griffin Report.

## Header

Display:

* Griffin
* Report title
* Evaluation timestamp

## Metadata

Display only available fields:

* Student
* Program
* Semester
* Course
* Subject
* Report information

Do not invent missing metadata.

---

# 24. Executive Summary

Use the existing GriffinResult summary.

Do not generate a new frontend summary.

---

# 25. Curriculum Mapping

Show:

* Overall mapping percentage
* Subject-wise mapping

Use:

* Bar chart
* Pie chart
* Radial chart

Values must come from GriffinResult.

---

# 26. Curriculum Mapping Table

Columns:

```text
Sr. No.
Subject
Unit
Topic
Evidence
Mapped %
Contribution %
Confidence
Significance
```

Only display fields actually available from GriffinResult.

Do not fabricate missing values.

---

# 27. Evidence

Display the evidence supporting mapped curriculum topics.

Evidence must come directly from GriffinResult.

The frontend must not generate, rewrite, or infer evidence.

---

# 28. Significance

Display Griffin-generated:

* Significance
* Depth
* Contribution
* Verdict

Do not calculate or reinterpret these values in the frontend.

---

# 29. Bloom Taxonomy

Display:

```text
Remember
Understand
Apply
Analyze
Evaluate
Create
```

Highlight the level produced by GriffinResult.

Do not independently classify the report.

---

# 30. Final Verdict

Display the existing Griffin evaluation output.

Do not generate a new frontend verdict.

---

# 31. Report Download

Support:

* PDF
* CSV
* TXT

PDF must use a professional A4 layout.

Structure:

```text
Header
Metadata
Executive Summary
Charts
Curriculum Mapping Table
Evidence / Significance
Bloom Taxonomy
Final Verdict
Footer
```

Footer:

```text
Generated by Griffin
Timestamp
Page Number
```

Downloads are presentation/export functions.

They must not rerun Griffin evaluation.

---

# 32. Application Navigation

Keep navigation minimal.

Required:

```text
Projects
Current Project / Griffin Console
Reports
Project Analytics
Curriculum Graph
Account
```

Do not add unrelated modules.

---

# 33. Curriculum Graph

Reuse the existing Griffin curriculum visualization.

It is a secondary visualization feature.

It must not become the primary Griffin interface.

Open it from the current project.

Keep the graph lightweight and responsive.

---

# 34. Console UI Design

The Console should be:

* Light
* Minimal
* Clean
* Fast
* Modern
* Technical
* Visually interesting

Do not make it a generic enterprise dashboard.

Keep existing Griffin identity.

Keep existing meaningful animations.

Keep the neural-network/cognitive visualization.

Make them lightweight.

Prefer:

* CSS animation
* SVG
* Lightweight Canvas
* Subtle transitions
* Small node counts
* Meaningful state animation

Avoid:

* Heavy glassmorphism
* Excessive gradients
* Huge shadows
* Excessive blur
* Particle-heavy backgrounds
* Hundreds of animated DOM elements
* Continuous unnecessary animation

The neural network should feel:

```text
Alive, intelligent, and lightweight.
```

not:

```text
Busy, decorative, and expensive.
```

Pause unnecessary animation when components are hidden or the tab is inactive.

---

# 35. Frontend Performance

Audit the Console for:

* Unnecessary re-renders
* Duplicate API requests
* Excessive useEffect chains
* Unnecessary state
* Expensive rendering
* Excessive DOM nodes
* Continuous animations
* Unnecessary polling

Do not blindly add:

```text
useMemo
useCallback
React.memo
```

Simplify the architecture first.

The UI must remain responsive during evaluation.

---

# 36. Backend Work Remaining

Add only product infrastructure around the existing model.

Required:

* FastAPI application
* Authentication integration
* Project service
* Curriculum service
* Report service
* Evaluation service
* Batch service
* Result service
* Download endpoints
* Database models
* Repositories where genuinely required
* File/project storage
* Processing status

Do not modify Griffin evaluation internals.

---

# 37. Frontend Work Remaining

Build:

* Landing page
* Authentication UI
* Projects page
* Project Griffin Console
* Curriculum input
* Single report input
* Bulk report input
* Processing UI
* Project dashboard
* Reports library
* Individual evaluation report
* Charts
* Curriculum graph integration
* PDF/CSV/TXT export

Nothing else is required for Griffin v1.0.

---

# 38. Product Completion Criteria

Griffin v1.0 is complete when a user can:

1. Open the landing page.
2. Authenticate.
3. Create a project.
4. Upload/select curriculum.
5. Upload one report or multiple reports/folder where supported.
6. Run the real Griffin pipeline.
7. See real processing status.
8. Persist every GriffinResult.
9. Open project analytics.
10. See report statistics and Top 5 mapped reports.
11. Open an individual evaluation.
12. Inspect curriculum mapping and evidence.
13. View significance and Bloom analysis.
14. Download PDF, CSV, or TXT.
15. Return later and access stored project results.

---

# 39. Final Engineering Principle

Build Griffin as a **thin product wrapper around existing intelligence**.

```text
Simple Frontend
      ↓
Clean API Client
      ↓
Thin FastAPI Routes
      ↓
Simple Product Services
      ↓
Existing Griffin Core
      ↓
GriffinResult
      ↓
Database
      ↓
Simple Presentation Layer
```

The goal is not architectural sophistication.

The goal is:

**Reliable → Readable → Maintainable → Fast → Production-ready**

Remove redundant code and overengineering wherever possible.

Do not replace existing working intelligence.

Do not add features outside this specification.

Anything outside this specification must NOT be implemented unless explicitly requested.
