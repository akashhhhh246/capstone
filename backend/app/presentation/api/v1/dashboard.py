from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.domain.entities.models import Content, DetectionResult, Campaign, Platform, SimulationRun
from app.application.dto.schemas import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["Analyst Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Aggregate high-level KPIs, alert feeds, and telemetry distributions for the main dashboard."""
    total_contents = db.query(Content).count()
    human_count = db.query(DetectionResult).filter(DetectionResult.classification == "HUMAN").count()
    ai_count = db.query(DetectionResult).filter(DetectionResult.classification == "AI_GENERATED").count()
    
    # Suspicious count: AI probability >= 0.70
    suspicious_count = db.query(DetectionResult).filter(DetectionResult.ai_probability >= 0.70).count()
    
    active_campaigns = db.query(Campaign).filter(Campaign.status == "ACTIVE").count()
    high_risk_campaigns = db.query(Campaign).filter(Campaign.risk_score >= 0.60).count()
    active_sims = db.query(SimulationRun).filter(SimulationRun.status == "RUNNING").count()
    platforms_count = db.query(Platform).count()

    # Risk distribution across campaigns
    crit = db.query(Campaign).filter(Campaign.risk_score >= 0.80).count()
    high = db.query(Campaign).filter(Campaign.risk_score >= 0.60, Campaign.risk_score < 0.80).count()
    med = db.query(Campaign).filter(Campaign.risk_score >= 0.40, Campaign.risk_score < 0.60).count()
    low = db.query(Campaign).filter(Campaign.risk_score < 0.40).count()

    # Platform breakdown
    platforms = db.query(Platform).all()
    platform_data = []
    for pl in platforms:
        platform_data.append({
            "name": pl.name,
            "type": pl.platform_type,
            "posts_count": len(pl.posts) if pl.posts else 0,
            "accounts_count": len(pl.accounts) if pl.accounts else 0
        })

    # Recent Alerts
    campaigns = db.query(Campaign).order_by(Campaign.risk_score.desc()).limit(5).all()
    alerts = []
    for c in campaigns:
        sev = "CRITICAL" if c.risk_score >= 0.8 else ("HIGH" if c.risk_score >= 0.6 else "MEDIUM")
        alerts.append({
            "id": f"alert-{c.id[:8]}",
            "campaign_id": c.id,
            "campaign_name": c.name,
            "severity": sev,
            "risk_score": round(c.risk_score, 2),
            "message": f"Suspicious propagation surge detected across {c.total_platforms} platforms.",
            "timestamp": c.updated_at.isoformat() if c.updated_at else ""
        })

    # Recent Analyses
    recent_contents = db.query(Content).order_by(Content.created_at.desc()).limit(6).all()
    recent_analyses = []
    for rc in recent_contents:
        det = rc.detection_results[0] if rc.detection_results else None
        recent_analyses.append({
            "id": rc.id,
            "text_snippet": rc.raw_text[:110] + "..." if len(rc.raw_text) > 110 else rc.raw_text,
            "domain": rc.domain,
            "classification": det.classification if det else "UNKNOWN",
            "ai_probability": det.ai_probability if det else 0.0,
            "confidence": det.confidence if det else 0.0,
            "created_at": rc.created_at.isoformat() if rc.created_at else ""
        })

    return {
        "total_analyzed_content": total_contents,
        "human_content_count": human_count,
        "ai_content_count": ai_count,
        "suspicious_content_count": suspicious_count,
        "active_campaigns_count": active_campaigns,
        "high_risk_campaigns_count": high_risk_campaigns,
        "active_simulations_count": active_sims,
        "platforms_count": max(4, platforms_count),
        "recent_alerts": alerts,
        "risk_distribution": {"CRITICAL": crit, "HIGH": high, "MEDIUM": med, "LOW": low},
        "platform_breakdown": platform_data,
        "recent_analyses": recent_analyses
    }
