from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto.schemas import ProvenanceResponse
from app.application.services.provenance_service import ProvenanceService

router = APIRouter(prefix="/provenance", tags=["Content Provenance"])
provenance_service = ProvenanceService()

@router.get("/{contentId}", response_model=ProvenanceResponse)
def get_content_provenance(contentId: str, db: Session = Depends(get_db)):
    """
    Reconstruct Directed Acyclic Graph (DAG) of content lineage and provenance.
    Traces root origins, near-duplicate paraphrases, platform reposts, and cross-platform spread.
    """
    try:
        result = provenance_service.get_provenance_for_content(content_id=contentId, db=db)
        if "error" in result and not result.get("nodes"):
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provenance reconstruction error: {str(e)}")
