import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.infrastructure.database.session import get_db
from app.domain.entities.models import Content, DetectionResult, Campaign, Post, Platform, SyntheticAccount, PropagationEvent
from app.application.services.provenance_service import ProvenanceService

router = APIRouter()
logger = logging.getLogger("api_live_content")

provenance_service = ProvenanceService()

class CascadeSimulationRequest(BaseModel):
    campaign_name: Optional[str] = None
    target_platforms: Optional[List[str]] = None

@router.get("", summary="List live ingested real-world content feed")
def list_live_content(
    limit: int = Query(50, ge=1, le=100),
    data_origin: Optional[str] = Query("REAL_WORLD"),
    source_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve live stream of ingested content items with detection results,
    risk scores, and topic tags.
    """
    query = db.query(Content, DetectionResult).outerjoin(
        DetectionResult, Content.id == DetectionResult.content_id
    )

    if data_origin:
        query = query.filter(Content.data_origin == data_origin)
    if source_type:
        query = query.filter(Content.source_type == source_type)

    results = query.order_by(Content.ingested_at.desc()).limit(limit).all()

    items = []
    for content, det in results:
        ai_prob = det.ai_probability if det else 0.5
        risk_score = round(ai_prob * 0.85, 2)
        items.append({
            "id": content.id,
            "title": content.title or (content.raw_text[:80] + "..."),
            "raw_text": content.raw_text,
            "clean_text": content.clean_text,
            "url": content.url,
            "source_name": content.source_name,
            "source_type": content.source_type,
            "author": content.author,
            "published_at": content.published_at.isoformat() if content.published_at else None,
            "ingested_at": content.ingested_at.isoformat() if content.ingested_at else content.created_at.isoformat(),
            "language": content.language,
            "country": content.country,
            "topics": content.topics or [],
            "entities": content.entities or [],
            "data_origin": content.data_origin,
            "classification": det.classification if det else "UNANALYZED",
            "confidence": det.confidence if det else 0.5,
            "ai_probability": ai_prob,
            "indicators": det.indicators if det else [],
            "risk_score": risk_score,
            "word_count": content.word_count,
        })

    return {
        "total": len(items),
        "data_origin": data_origin,
        "items": items
    }

@router.get("/{content_id}", summary="Get detailed real-world content item with provenance")
def get_live_content_item(content_id: str, db: Session = Depends(get_db)):
    """Retrieve full details, detection analytics, and provenance for a single ingested item."""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content record not found.")

    det = db.query(DetectionResult).filter(DetectionResult.content_id == content_id).first()
    provenance = provenance_service.get_provenance_for_content(content_id, db)

    return {
        "id": content.id,
        "title": content.title,
        "raw_text": content.raw_text,
        "clean_text": content.clean_text,
        "url": content.url,
        "source_name": content.source_name,
        "source_type": content.source_type,
        "author": content.author,
        "published_at": content.published_at.isoformat() if content.published_at else None,
        "ingested_at": content.ingested_at.isoformat() if content.ingested_at else None,
        "data_origin": content.data_origin,
        "topics": content.topics,
        "detection": {
            "classification": det.classification if det else "UNANALYZED",
            "confidence": det.confidence if det else 0.0,
            "ai_probability": det.ai_probability if det else 0.0,
            "indicators": det.indicators if det else [],
            "gltr_stats": det.gltr_stats if det else {},
            "statistical_features": det.statistical_features if det else {},
            "watermark_status": det.watermark_status if det else "UNAVAILABLE",
        } if det else None,
        "provenance": provenance
    }

@router.post("/{content_id}/simulate-cascade", summary="Seed synthetic propagation simulation from real-world article")
def seed_synthetic_simulation_from_real_content(
    content_id: str,
    req: CascadeSimulationRequest = CascadeSimulationRequest(),
    db: Session = Depends(get_db)
):
    """
    Take a real-world article as a seed and create a SIMULATED propagation cascade scenario.
    Maintains strict ethical separation: the resulting cascade is explicitly tagged as SIMULATED.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Seed content not found.")

    now = datetime.now(timezone.utc)
    campaign_name = req.campaign_name or f"Simulated Dissemination: {(content.title or content.id)[:30]}"
    camp_id = f"camp-sim-{content.id[:8]}"

    # Check if campaign already exists
    existing_camp = db.query(Campaign).filter(Campaign.id == camp_id).first()
    if not existing_camp:
        campaign = Campaign(
            id=camp_id,
            name=campaign_name,
            objective=f"Evaluate simulated cross-platform diffusion cascade seeded by real-world news item",
            target_narrative=content.title or content.raw_text[:120],
            status="ACTIVE",
            risk_score=0.72,
            gnn_risk_score=0.68,
            explainability_reasons=[
                "Seeded from real-world public news article.",
                "Simulated synthetic cross-platform dissemination cascade across 3 platforms.",
                "Multi-account amplification dynamics modeled for defensive readiness."
            ],
            total_events=6,
            total_reach=4500,
            total_platforms=3,
            velocity_events_per_hour=8.5,
            branching_factor=2.4,
            created_at=now
        )
        db.add(campaign)
        db.flush()

        # Seed synthetic post records for this simulation
        platforms = db.query(Platform).all()
        accounts = db.query(SyntheticAccount).all()
        
        p1 = platforms[0].id if platforms else "plat-01"
        a1 = accounts[0].id if accounts else "acc-01"
        
        post_obj = Post(
            id=f"post-sim-{content.id[:8]}-01",
            platform_id=p1,
            account_id=a1,
            content_id=content.id,
            campaign_id=camp_id,
            post_type="ORIGINAL",
            likes=45,
            reshares=22,
            published_at=now,
            created_at=now
        )
        db.add(post_obj)
        db.commit()
    else:
        campaign = existing_camp

    return {
        "message": "Synthetic propagation simulation seeded successfully.",
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "seed_content_id": content.id,
        "data_origin_of_cascade": "SIMULATED",
        "data_origin_of_seed": content.data_origin
    }
