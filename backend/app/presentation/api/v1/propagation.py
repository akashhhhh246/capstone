from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto.schemas import PropagationMetricsResponse
from app.application.services.propagation_service import PropagationService

router = APIRouter(prefix="/propagation", tags=["Propagation Analysis"])
propagation_service = PropagationService()

@router.get("/{contentId}", response_model=PropagationMetricsResponse)
def get_propagation_metrics(contentId: str, db: Session = Depends(get_db)):
    """
    Compute NetworkX graph propagation metrics and GNN risk scores:
    - Propagation Velocity (events/hour)
    - Estimated Audience Reach
    - Reshare Depth & Branching Factor
    - Betweenness Centrality & Hub Identification
    - Coordinated Inauthentic Behavior (CIB) Indicators
    """
    try:
        result = propagation_service.analyze_propagation_for_content(content_id=contentId, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Propagation analysis error: {str(e)}")
