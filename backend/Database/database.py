from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://PwNnsYhQ3cRLKF8.root:11ewQx2OMpjuZNgL@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/griffin"
)

try:
    if "mysql" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL, 
            pool_size=10, 
            max_overflow=20, 
            pool_recycle=3600, 
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )
        inspector = inspect(engine)
        if "reports" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("reports")]
            if "project_id" not in columns:
                raise Exception("Missing project_id column in MySQL reports table")
    else:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
except Exception as e:
    print(f"Warning: Primary database error ({e}). Falling back to local SQLite.")
    sqlite_url = "sqlite:////tmp/griffin.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

