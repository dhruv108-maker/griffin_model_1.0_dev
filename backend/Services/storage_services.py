"""
backend/Services/storage_service.py
Handles disk storage operations for uploaded PDFs.
"""

import os
import uuid
import shutil
from fastapi import UploadFile

STORAGE_DIR = os.getenv("STORAGE_DIR", "/tmp/griffin_storage")

class StorageService:

    @staticmethod
    def save_upload_file(upload_file: UploadFile, subfolder: str = "reports") -> str:
        target_dir = os.path.join(STORAGE_DIR, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        
        file_ext = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(target_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return file_path