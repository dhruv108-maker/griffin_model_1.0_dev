from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("")
def get_system_settings():
    return {
        "confidence_threshold": 0.50,
        "max_concurrent_jobs": 4,
        "vector_embedding_model": "all-MiniLM-L6-v2",
        "llm_validation_active": True
    }