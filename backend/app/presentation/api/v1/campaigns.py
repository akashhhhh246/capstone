from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.infrastructure.database.session import get_db
from app.application.dto.schemas import CampaignResponse, CampaignDetailResponse
from app.application.services.campaign_service import CampaignService
from app.application.services.campaign_discovery_service import CampaignDiscoveryService

router = APIRouter(prefix="/campaigns", tags=["Campaign Intelligence"])
campaign_service = CampaignService()
discovery_service = CampaignDiscoveryService()

@router.get("", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    """List all tracked information operation campaigns with risk scores and severity classifications."""
    return campaign_service.get_all_campaigns(db)

@router.post("/discover", summary="Execute dynamic ML campaign discovery scan on live corpus")
def trigger_dynamic_discovery(db: Session = Depends(get_db)):
    """
    Run dynamic semantic clustering across all active content items,
    execute GNN inference, and register emergent live threat campaigns.
    """
    discovered = discovery_service.discover_and_update_campaigns(db)
    return {
        "status": "COMPLETED",
        "discovered_campaigns_count": len(discovered),
        "campaigns": discovered,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/{id}", response_model=CampaignDetailResponse)
def get_campaign_detail(id: str, db: Session = Depends(get_db)):
    """Retrieve in-depth campaign telemetry, network topology, posts, and itemized explainability reasons."""
    campaign = campaign_service.get_campaign_detail(campaign_id=id, db=db)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign

@router.get("/{id}/report", summary="Generate formatted forensic threat intelligence brief")
def get_campaign_report(id: str, db: Session = Depends(get_db)):
    """Generate a structured, professional Markdown intelligence report for threat briefing."""
    campaign = campaign_service.get_campaign_detail(campaign_id=id, db=db)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Generate structured markdown dossier
    reasons_list = "\n".join([f"- {r}" for r in campaign.get("explainability_reasons", [])])
    
    markdown_report = f"""# THREAT INTELLIGENCE DOSSIER: {campaign.get('name').upper()}
**Generated:** {now_str}
**Campaign ID:** `{campaign.get('id')}`
**Status:** `{campaign.get('status')}`
**Composite Risk Score:** `{int(campaign.get('risk_score', 0) * 100)}%` (GNN Topological Risk: `{int(campaign.get('gnn_risk_score', 0) * 100)}%`)
**Severity Level:** `{campaign.get('severity')}`

---

## 1. Executive Summary & Objective
- **Target Narrative:** {campaign.get('target_narrative')}
- **Objective:** {campaign.get('objective')}
- **Total Cross-Platform Reach:** {campaign.get('total_reach', 0):,} users
- **Diffusion Velocity:** {campaign.get('velocity_events_per_hour', 0):.1f} events/hour
- **Branching Amplification Factor:** {campaign.get('branching_factor', 0):.2f}

---

## 2. Evidentiary Forensic Risk Factors
{reasons_list if reasons_list else "- Automated multi-account synchronized dissemination detected."}

---

## 3. Dissemination Vectors & Accounts
- **Total Platforms:** {campaign.get('total_platforms', 0)}
- **Discovered Posts / Variants:** {len(campaign.get('posts', []))}
- **High-Risk Bot Accounts Involved:** {len(campaign.get('accounts', []))}

---

## 4. Defensive Containment Recommendations
1. Deploy provenance-authenticated debunking labels across affected mirror clusters.
2. Invalidate upstream bot coordination nodes identified via high betweenness centrality.
3. Establish continuous GDELT DOC API and public stream monitoring for mutation tracking.
"""
    return PlainTextResponse(markdown_report, media_type="text/markdown")
