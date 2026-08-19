import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.Database.database import Base, engine
from backend.Database import models  # noqa: F401
from backend.Routes import (
    health,
    projects,
    reports,
    chat,
    history,
    settings,
    evaluation,
    curriculum,
    workspace,
)
from backend.Services.griffin_services import GriffinService

# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Griffin OBL Evaluation API",
    description=(
        "Product API wrapping the frozen Griffin Core evidence-mapping engine "
        "for outcome-based learning evaluation."
    ),
    version="1.0.0",
)


@app.on_event("startup")
async def warm_griffin_models() -> None:
    """Load the configured Griffin model pool once when the API process starts."""
    GriffinService.warm_up()

# ============================================================
# CORS
# ============================================================

_allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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
app.include_router(workspace.router)


@app.get("/")
def root():
    return {
        "name": "Griffin",
        "product": "OBL Evaluation AI",
        "status": "online",
        "version": "1.0.0",
    }
