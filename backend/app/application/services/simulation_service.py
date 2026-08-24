import asyncio
import uuid
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.domain.entities.models import SimulationRun, Campaign, Post, Platform, SyntheticAccount, PropagationEvent, Content
from app.infrastructure.database.session import SessionLocal
from app.presentation.websocket.simulation_ws import ws_manager

class SimulationEngine:
    """
    Asynchronous Simulation Engine.
    Generates synthetic multi-platform social media propagation events in real time.
    Emits events over WebSockets to update frontend graphs, telemetry gauges, and alerts.
    """

    _active_tasks: Dict[str, asyncio.Task] = {}
    _running_states: Dict[str, str] = {}  # RUNNING, PAUSED, STOPPED

    EVENT_TYPES = ["POST", "RESHARE", "REPLY", "QUOTE", "CROSS_PLATFORM_SHARE", "CONTENT_VARIANT"]

    @classmethod
    async def start_simulation(
        cls,
        campaign_id: str,
        event_rate: float = 1.5,
        duration_seconds: int = 120,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        sim_id = str(uuid.uuid4())
        
        # Register in DB
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        try:
            sim_run = SimulationRun(
                id=sim_id,
                campaign_id=campaign_id,
                status="RUNNING",
                event_rate_per_sec=event_rate,
                duration_seconds=duration_seconds,
                started_at=datetime.now(timezone.utc)
            )
            db.add(sim_run)
            db.commit()
        finally:
            if own_db:
                db.close()

        cls._running_states[sim_id] = "RUNNING"
        # Spawn async generator task
        task = asyncio.create_task(cls._simulation_loop(sim_id, campaign_id, event_rate, duration_seconds))
        cls._active_tasks[sim_id] = task

        return {
            "id": sim_id,
            "campaign_id": campaign_id,
            "status": "RUNNING",
            "event_rate_per_sec": event_rate,
            "duration_seconds": duration_seconds,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    async def pause_simulation(cls, simulation_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        cls._running_states[simulation_id] = "PAUSED"
        
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        try:
            sim_run = db.query(SimulationRun).filter(SimulationRun.id == simulation_id).first()
            if sim_run:
                sim_run.status = "PAUSED"
                sim_run.paused_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            if own_db:
                db.close()

        return {"id": simulation_id, "status": "PAUSED"}

    @classmethod
    async def stop_simulation(cls, simulation_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        cls._running_states[simulation_id] = "STOPPED"
        if simulation_id in cls._active_tasks:
            task = cls._active_tasks.pop(simulation_id)
            task.cancel()

        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        try:
            sim_run = db.query(SimulationRun).filter(SimulationRun.id == simulation_id).first()
            if sim_run:
                sim_run.status = "STOPPED"
                sim_run.stopped_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            if own_db:
                db.close()

        return {"id": simulation_id, "status": "STOPPED"}

    @classmethod
    def get_simulation_status(cls, simulation_id: str, db: Session) -> Optional[Dict[str, Any]]:
        sim_run = db.query(SimulationRun).filter(SimulationRun.id == simulation_id).first()
        if not sim_run:
            return None
        return {
            "id": sim_run.id,
            "campaign_id": sim_run.campaign_id,
            "status": cls._running_states.get(simulation_id, sim_run.status),
            "event_rate_per_sec": sim_run.event_rate_per_sec,
            "total_events_emitted": sim_run.total_events_emitted,
            "duration_seconds": sim_run.duration_seconds,
            "started_at": sim_run.started_at.isoformat() if sim_run.started_at else None,
            "paused_at": sim_run.paused_at.isoformat() if sim_run.paused_at else None,
            "stopped_at": sim_run.stopped_at.isoformat() if sim_run.stopped_at else None
        }

    @classmethod
    async def _simulation_loop(cls, sim_id: str, campaign_id: str, event_rate: float, duration_seconds: int):
        """Async loop emitting synthetic propagation events."""
        interval = 1.0 / max(0.2, event_rate)
        elapsed = 0.0
        events_emitted = 0

        while elapsed < duration_seconds and cls._running_states.get(sim_id) != "STOPPED":
            if cls._running_states.get(sim_id) == "PAUSED":
                await asyncio.sleep(0.5)
                continue

            # Generate synthetic event
            event_payload = cls._generate_random_event(sim_id, campaign_id, events_emitted)
            
            # Broadcast over WebSocket
            await ws_manager.broadcast_event(
                {
                    "type": "SIMULATION_PROPAGATION_EVENT",
                    "data": event_payload
                },
                simulation_id=sim_id
            )

            # Persist event in DB asynchronously
            cls._persist_event(sim_id, campaign_id, event_payload)

            events_emitted += 1
            elapsed += interval
            await asyncio.sleep(interval)

        cls._running_states[sim_id] = "COMPLETED"
        await ws_manager.broadcast_event(
            {
                "type": "SIMULATION_COMPLETED",
                "simulation_id": sim_id,
                "total_events": events_emitted
            },
            simulation_id=sim_id
        )

    @classmethod
    def _generate_random_event(cls, sim_id: str, campaign_id: str, event_seq: int) -> Dict[str, Any]:
        platforms = [
            ("plat-sim-01", "SimuTwitter"),
            ("plat-sim-02", "SimuTelegram"),
            ("plat-sim-03", "SimuReddit"),
            ("plat-sim-04", "SimuNewsWire")
        ]
        chosen_plat = random.choice(platforms)
        
        accounts = [
            ("acc-synth-101", "@echo_node_01", 0.92),
            ("acc-synth-102", "@pulse_relay_beta", 0.88),
            ("acc-synth-103", "@shadow_wire_99", 0.95),
            ("acc-synth-104", "@vector_mesh_alpha", 0.74),
            ("acc-synth-105", "@observer_node_x", 0.25)
        ]
        chosen_acc = random.choice(accounts)
        
        event_type = random.choice(cls.EVENT_TYPES)
        now_str = datetime.now(timezone.utc).isoformat()

        sim_velocity = round(random.uniform(8.5, 24.0), 2)
        total_reach = int(2400 + (event_seq * random.randint(80, 160)))
        risk_score = round(min(0.99, max(0.40, 0.75 + random.uniform(-0.1, 0.15))), 2)

        snippets = [
            "ALERT: Leaked defense briefing confirms coordinated grid switching protocol...",
            "URGENT: Municipal water supplies under unverified filtration lockdown...",
            "BREAKING: Overnight liquidity halt rumored across major banking exchanges...",
            "Warning: Automated cognitive broadcast signals detected on aviation routes..."
        ]

        return {
            "event_id": str(uuid.uuid4()),
            "simulation_id": sim_id,
            "campaign_id": campaign_id,
            "event_type": event_type,
            "source_post_id": f"post-src-{random.randint(100, 199)}",
            "target_post_id": f"post-tgt-{random.randint(200, 299)}",
            "account_id": chosen_acc[0],
            "account_handle": chosen_acc[1],
            "bot_probability": chosen_acc[2],
            "platform_id": chosen_plat[0],
            "platform_name": chosen_plat[1],
            "content_id": f"content-sim-{random.randint(1, 10)}",
            "content_snippet": random.choice(snippets),
            "timestamp": now_str,
            "velocity": sim_velocity,
            "total_reach": total_reach,
            "risk_score": risk_score
        }

    @classmethod
    def _persist_event(cls, sim_id: str, campaign_id: str, event_data: Dict[str, Any]):
        db = SessionLocal()
        try:
            ev = PropagationEvent(
                id=event_data["event_id"],
                simulation_id=sim_id,
                campaign_id=campaign_id,
                event_type=event_data["event_type"],
                source_post_id=event_data.get("source_post_id"),
                target_post_id=event_data.get("target_post_id"),
                account_id=event_data["account_id"],
                platform_id=event_data["platform_id"],
                content_id=event_data["content_id"],
                metadata_json=event_data
            )
            db.add(ev)
            # Update SimulationRun total_events_emitted
            sim_run = db.query(SimulationRun).filter(SimulationRun.id == sim_id).first()
            if sim_run:
                sim_run.total_events_emitted += 1
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
