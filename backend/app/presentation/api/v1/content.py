import hashlib
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.database.session import get_db
from app.domain.entities.models import Content, DetectionResult
from app.application.dto.schemas import ContentCreateRequest, ContentResponse
from app.ml.detection.preprocessing import TextPreprocessor
from app.application.services.detection_service import DetectionService

router = APIRouter(prefix="/content", tags=["Content Registry"])
detection_service = DetectionService()

@router.post("", response_model=ContentResponse)
def register_content(request: ContentCreateRequest, db: Session = Depends(get_db)):
    """Register new content snippet and automatically run initial detection."""
    clean = TextPreprocessor.clean_text(request.text)
    if not clean:
        raise HTTPException(status_code=400, detail="Content text cannot be empty.")

    text_hash = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    
    # Check if already exists
    existing = db.query(Content).filter(Content.text_hash == text_hash).first()
    if existing:
        latest_det = existing.detection_results[0] if existing.detection_results else None
        return {
            "id": existing.id,
            "text_hash": existing.text_hash,
            "raw_text": existing.raw_text,
            "clean_text": existing.clean_text,
            "domain": existing.domain,
            "word_count": existing.word_count,
            "char_count": existing.char_count,
            "created_at": existing.created_at.isoformat() if existing.created_at else "",
            "latest_detection": {
                "classification": latest_det.classification,
                "confidence": latest_det.confidence,
                "ai_probability": latest_det.ai_probability
            } if latest_det else None
        }

    features = TextPreprocessor.extract_features(clean)
    new_content = Content(
        text_hash=text_hash,
        raw_text=request.text,
        clean_text=clean,
        domain=request.domain or "general",
        source_label=request.source_label or "analyst_submission",
        word_count=features["word_count"],
        char_count=features["char_count"]
    )
    db.add(new_content)
    db.flush()

    # Run detection
    det_res = detection_service.analyze_text(clean, domain=request.domain or "general")
    det_record = DetectionResult(
        content_id=new_content.id,
        classification=det_res["classification"],
        confidence=det_res["confidence"],
        ai_probability=det_res["ai_probability"],
        model_version=det_res["model_version"],
        gltr_stats=det_res["gltr_result"]["bucket_distribution"],
        watermark_status=det_res["watermark_result"]["status"],
        watermark_details=det_res["watermark_result"]["details"],
        statistical_features=det_res["statistical_features"],
        indicators=det_res["indicators"],
        is_heuristic_fallback=False
    )
    db.add(det_record)
    db.commit()
    db.refresh(new_content)

    return {
        "id": new_content.id,
        "text_hash": new_content.text_hash,
        "raw_text": new_content.raw_text,
        "clean_text": new_content.clean_text,
        "domain": new_content.domain,
        "word_count": new_content.word_count,
        "char_count": new_content.char_count,
        "created_at": new_content.created_at.isoformat() if new_content.created_at else "",
        "latest_detection": {
            "classification": det_res["classification"],
            "confidence": det_res["confidence"],
            "ai_probability": det_res["ai_probability"]
        }
    }

@router.get("/{id}", response_model=ContentResponse)
def get_content_by_id(id: str, db: Session = Depends(get_db)):
    """Retrieve content record by ID."""
    content = db.query(Content).filter(Content.id == id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")

    latest_det = content.detection_results[0] if content.detection_results else None
    return {
        "id": content.id,
        "text_hash": content.text_hash,
        "raw_text": content.raw_text,
        "clean_text": content.clean_text,
        "domain": content.domain,
        "word_count": content.word_count,
        "char_count": content.char_count,
        "created_at": content.created_at.isoformat() if content.created_at else "",
        "latest_detection": {
            "classification": latest_det.classification,
            "confidence": latest_det.confidence,
            "ai_probability": latest_det.ai_probability
        } if latest_det else None
    }

@router.get("", response_model=List[ContentResponse])
def list_contents(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """List registered content items."""
    contents = db.query(Content).order_by(Content.created_at.desc()).limit(limit).all()
    results = []
    for c in contents:
        latest_det = c.detection_results[0] if c.detection_results else None
        results.append({
            "id": c.id,
            "text_hash": c.text_hash,
            "raw_text": c.raw_text,
            "clean_text": c.clean_text,
            "domain": c.domain,
            "word_count": c.word_count,
            "char_count": c.char_count,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "latest_detection": {
                "classification": latest_det.classification,
                "confidence": latest_det.confidence,
                "ai_probability": latest_det.ai_probability
            } if latest_det else None
        })
    return results
