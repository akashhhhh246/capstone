from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto.schemas import AnalyzeTextRequest, DetectionResultResponse
from app.application.services.detection_service import DetectionService

router = APIRouter(prefix="/detection", tags=["Content Detection"])
detection_service = DetectionService()

@router.post("/analyze", response_model=DetectionResultResponse)
def analyze_content(request: AnalyzeTextRequest, db: Session = Depends(get_db)):
    """
    Execute Part 1 Detection Pipeline:
    - TF-IDF + Logistic Regression classification (HUMAN vs AI_GENERATED)
    - GLTR-style statistical token probability ranking
    - Kirchenbauer / Cryptographic watermark verification
    - Stylometric text statistics (burstiness, entropy, lexical diversity)
    - Optional content registration in provenance database
    """
    try:
        result = detection_service.analyze_text(
            text=request.text,
            domain=request.domain or "general",
            db=db,
            register_content=request.register_content or False
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection pipeline error: {str(e)}")
