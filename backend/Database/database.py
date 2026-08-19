"""Database configuration for Griffin product services.

The production database URL must be supplied through DATABASE_URL. No
credentials are stored in source control and production never silently falls
back to SQLite.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
ALLOW_LOCAL_SQLITE = os.getenv("GRIFFIN_ALLOW_LOCAL_SQLITE", "false").lower() == "true"

if not DATABASE_URL:
    if not ALLOW_LOCAL_SQLITE:
        raise RuntimeError(
            "DATABASE_URL is required. Set GRIFFIN_ALLOW_LOCAL_SQLITE=true only for local development."
        )

    local_db_path = Path(__file__).resolve().parents[2] / "data" / "griffin.db"
    local_db_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{local_db_path.as_posix()}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
