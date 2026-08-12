from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.Database.database import Base, engine
from backend.Database import models

from backend.Routes import (
    health,
    projects,
    reports,
    chat,
    history,
    settings,
    evaluation,
    curriculum,
)

from backend.Routes import workspace


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)

# Dynamically add logs column to batch_jobs table if it does not exist
try:
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "batch_jobs" in inspector.get_table_names():
        cols = [c["name"] for c in inspector.get_columns("batch_jobs")]
        if "logs" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE batch_jobs ADD COLUMN logs JSON NULL"))
                conn.commit()
                print("Successfully added 'logs' column to batch_jobs table.")
except Exception as e:
    print(f"Warning: Could not dynamically add logs column on startup: {e}")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Griffin Core v1.0 API Engine",
    description=(
        "Backend service exposing Griffin curriculum "
        "evaluation capabilities."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(settings.router)
app.include_router(evaluation.router)
app.include_router(curriculum.router)

# Workspace routes
app.include_router(workspace.router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Griffin Core v1.0",
        "status": "online",
        "service": "API Engine",
        "version": "1.0.0",
    }


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )