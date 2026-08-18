"""Database configuration for Griffin product services.

The production database URL must be supplied through DATABASE_URL. No
credentials are stored in source control and production never silently falls
back to SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
ALLOW_LOCAL_SQLITE = os.getenv("GRIFFIN_ALLOW_LOCAL_SQLITE", "false").lower() == "true"

if not DATABASE_URL:
    if not ALLOW_LOCAL_SQLITE:
        raise RuntimeError(
            "DATABASE_URL is required. Set GRIFFIN_ALLOW_LOCAL_SQLITE=true only for local development."
        )
    DATABASE_URL = "sqlite:////tmp/griffin.db"

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
