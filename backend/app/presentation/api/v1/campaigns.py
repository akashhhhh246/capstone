from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database.session import get_db
from app.application.dto.schemas import CampaignResponse, CampaignDetailResponse
from app.application.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaign Intelligence"])
campaign_service = CampaignService()

@router.get("", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    """List all tracked malign information campaigns with risk scores and severity classifications."""
    return campaign_service.get_all_campaigns(db)

@router.get("/{id}", response_model=CampaignDetailResponse)
def get_campaign_detail(id: str, db: Session = Depends(get_db)):
    """Retrieve in-depth campaign telemetry, network topology, posts, and itemized explainability reasons."""
    campaign = campaign_service.get_campaign_detail(campaign_id=id, db=db)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign
