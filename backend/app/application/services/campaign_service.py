from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.domain.entities.models import Campaign, Post, Platform, SyntheticAccount, DetectionResult
from app.ml.risk.risk_scoring_service import RiskScoringService
from app.application.services.propagation_service import PropagationService

class CampaignService:
    """
    Application Service for Campaign Intelligence & Risk Analytics.
    Aggregates multi-platform campaign telemetry and computes explainable risk scores.
    """

    def __init__(self, propagation_service: Optional[PropagationService] = None):
        self.propagation_service = propagation_service or PropagationService()

    def get_all_campaigns(self, db: Session) -> List[Dict[str, Any]]:
        campaigns = db.query(Campaign).order_by(Campaign.risk_score.desc()).all()
        results = []
        for c in campaigns:
            severity = "CRITICAL" if c.risk_score >= 0.8 else ("HIGH" if c.risk_score >= 0.6 else ("MEDIUM" if c.risk_score >= 0.4 else "LOW"))
            results.append({
                "id": c.id,
                "name": c.name,
                "objective": c.objective,
                "target_narrative": c.target_narrative,
                "status": c.status,
                "risk_score": round(c.risk_score, 2),
                "gnn_risk_score": round(c.gnn_risk_score, 2),
                "severity": severity,
                "explainability_reasons": c.explainability_reasons or [],
                "total_events": c.total_events,
                "total_reach": c.total_reach,
                "total_platforms": c.total_platforms,
                "velocity_events_per_hour": c.velocity_events_per_hour,
                "branching_factor": c.branching_factor,
                "created_at": c.created_at.isoformat() if c.created_at else ""
            })
        return results

    def get_campaign_detail(self, campaign_id: str, db: Session) -> Optional[Dict[str, Any]]:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None

        # Fetch propagation analysis
        prop_data = self.propagation_service.analyze_campaign_propagation(campaign_id, db)

        # Fetch posts
        posts = db.query(Post).filter(Post.campaign_id == campaign_id).all()
        posts_data = []
        for p in posts:
            posts_data.append({
                "id": p.id,
                "platform": p.platform.name if p.platform else "Unknown",
                "account": p.account.pseudonym_handle if p.account else "@anon",
                "content_snippet": p.content.raw_text[:100] + "..." if p.content else "",
                "post_type": p.post_type,
                "likes": p.likes,
                "reshares": p.reshares,
                "published_at": p.published_at.isoformat() if p.published_at else ""
            })

        # Calculate live explainable risk score
        ai_prob = 0.85 if campaign.risk_score > 0.6 else 0.45
        risk_eval = RiskScoringService.calculate_risk_score(
            ai_probability=ai_prob,
            propagation_velocity=campaign.velocity_events_per_hour,
            platform_count=campaign.total_platforms,
            branching_factor=campaign.branching_factor,
            derived_variant_count=len(posts_data),
            gnn_score=campaign.gnn_risk_score
        )

        # Update campaign model with fresh explainability reasons
        campaign.explainability_reasons = risk_eval["reasons"]
        campaign.risk_score = risk_eval["risk_score"]
        db.commit()

        severity = risk_eval["severity"]

        return {
            "id": campaign.id,
            "name": campaign.name,
            "objective": campaign.objective,
            "target_narrative": campaign.target_narrative,
            "status": campaign.status,
            "risk_score": risk_eval["risk_score"],
            "gnn_risk_score": campaign.gnn_risk_score,
            "severity": severity,
            "explainability_reasons": risk_eval["reasons"],
            "total_events": campaign.total_events,
            "total_reach": campaign.total_reach,
            "total_platforms": campaign.total_platforms,
            "velocity_events_per_hour": campaign.velocity_events_per_hour,
            "branching_factor": campaign.branching_factor,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
            "posts": posts_data,
            "platforms": [
                {"name": pl.name, "type": pl.platform_type, "risk_weight": pl.risk_weight}
                for pl in db.query(Platform).all()
            ],
            "accounts": [
                {"handle": a.pseudonym_handle, "bot_probability": a.bot_probability, "platform": a.platform.name if a.platform else ""}
                for a in db.query(SyntheticAccount).limit(10).all()
            ],
            "graph_metrics": prop_data
        }
