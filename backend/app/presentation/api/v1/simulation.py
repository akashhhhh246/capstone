from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.domain.entities.models import Campaign, SimulationRun
from app.application.dto.schemas import SimulationStartRequest, SimulationResponse
from app.application.services.simulation_service import SimulationEngine

router = APIRouter(prefix="/simulation", tags=["Real-Time Simulation"])

@router.post("/start", response_model=SimulationResponse)
async def start_simulation(request: SimulationStartRequest, db: Session = Depends(get_db)):
    """Start asynchronous synthetic social media propagation simulation for a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Target campaign not found.")

    res = await SimulationEngine.start_simulation(
        campaign_id=request.campaign_id,
        event_rate=request.event_rate_per_sec or 1.5,
        duration_seconds=request.duration_seconds or 120,
        db=db
    )
    return res

@router.post("/{id}/pause", response_model=SimulationResponse)
async def pause_simulation(id: str, db: Session = Depends(get_db)):
    """Pause an active propagation simulation."""
    sim_status = SimulationEngine.get_simulation_status(id, db)
    if not sim_status:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    await SimulationEngine.pause_simulation(id, db)
    return SimulationEngine.get_simulation_status(id, db)

@router.post("/{id}/stop", response_model=SimulationResponse)
async def stop_simulation(id: str, db: Session = Depends(get_db)):
    """Stop and finalize an active propagation simulation."""
    sim_status = SimulationEngine.get_simulation_status(id, db)
    if not sim_status:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    await SimulationEngine.stop_simulation(id, db)
    return SimulationEngine.get_simulation_status(id, db)

@router.get("/{id}", response_model=SimulationResponse)
def get_simulation_status(id: str, db: Session = Depends(get_db)):
    """Get current lifecycle state and emitted event counts for a simulation run."""
    sim_status = SimulationEngine.get_simulation_status(id, db)
    if not sim_status:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return sim_status
