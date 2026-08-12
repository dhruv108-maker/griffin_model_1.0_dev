"""
backend/Dependencies/database_dep.py
FastAPI dependency for database session lifecycle management.
"""

from typing import Generator
from sqlalchemy.orm import Session
from backend.Database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    
    Yields:
        Session: SQLAlchemy database session instance.
        
    Guarantees:
        The session is closed cleanly after the request finishes, 
        even if an unhandled exception occurs during execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()