from fastapi import APIRouter, HTTPException
from app.unused.ingest_pipelines import ingest_json_file
from app.schemas.chat import ChatRequest, ChatResponse
from pathlib import Path
from app.rag.knowledge_loader import KnowledgeLoader

router = APIRouter(tags=["Ingest"])

@router.post("/ingest-default-json")
def ingest_default_json():
    """
    Ingest the default JSON located in the parent of 'app' folder.
    """
    TRUCK_SPEC_JSON_PATH = Path("app/rag/data/truck_spec.json")
    try:
        KnowledgeLoader().ingest(file_path=TRUCK_SPEC_JSON_PATH, source_type="json")
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    return {"status": "success", "message": "Default JSON ingested successfully"}
