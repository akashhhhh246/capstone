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

    EVENT_TYPES = [
        "POST", "RESHARE", "REPLY", "QUOTE", "CROSS_PLATFORM_SHARE", "CONTENT_VARIANT",
        "FACT_CHECK_DEBUNK", "COMMUNITY_NOTE", "OFFICIAL_NOTICE"
    ]

    @classmethod
    async def start_simulation(
        cls,
        campaign_id: str,
        event_rate: float = 1.5,
        duration_seconds: int = 120,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        # Halt any existing runaway simulation before starting a new one
        await cls.stop_all_simulations(db)

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
                total_events_emitted=0,
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
            "total_events_emitted": 0,
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

        await ws_manager.broadcast_event(
            {
                "type": "SIMULATION_PAUSED",
                "simulation_id": simulation_id,
                "status": "PAUSED"
            },
            simulation_id="global"
        )
        return {"id": simulation_id, "status": "PAUSED"}

    @classmethod
    async def stop_simulation(cls, simulation_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        cls._running_states[simulation_id] = "STOPPED"
        if simulation_id in cls._active_tasks:
            task = cls._active_tasks.pop(simulation_id)
            if not task.done():
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

        # Broadcast stop event so all WebSocket clients immediately halt
        await ws_manager.broadcast_event(
            {
                "type": "SIMULATION_STOPPED",
                "simulation_id": simulation_id,
                "status": "STOPPED"
            },
            simulation_id="global"
        )
        return {"id": simulation_id, "status": "STOPPED"}

    @classmethod
    async def stop_all_simulations(cls, db: Optional[Session] = None) -> Dict[str, Any]:
        """Cancel and halt all active or paused simulations across memory and database."""
        stopped_count = 0
        for sim_id, task in list(cls._active_tasks.items()):
            cls._running_states[sim_id] = "STOPPED"
            if not task.done():
                task.cancel()
            stopped_count += 1
        cls._active_tasks.clear()

        for sim_id in list(cls._running_states.keys()):
            cls._running_states[sim_id] = "STOPPED"

        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        try:
            active_runs = db.query(SimulationRun).filter(SimulationRun.status.in_(["RUNNING", "PAUSED"])).all()
            for r in active_runs:
                r.status = "STOPPED"
                r.stopped_at = datetime.now(timezone.utc)
                stopped_count += 1
            db.commit()
        finally:
            if own_db:
                db.close()

        # Broadcast stop event globally
        await ws_manager.broadcast_event(
            {
                "type": "SIMULATION_STOPPED",
                "simulation_id": "all",
                "status": "STOPPED"
            },
            simulation_id="global"
        )
        return {"status": "STOPPED", "stopped_count": stopped_count}

    @classmethod
    def get_active_simulation(cls, db: Session) -> Optional[Dict[str, Any]]:
        """Return the current active or running simulation if one exists."""
        for sim_id, task in cls._active_tasks.items():
            if not task.done() and cls._running_states.get(sim_id) in ["RUNNING", "PAUSED"]:
                return cls.get_simulation_status(sim_id, db)

        active_run = db.query(SimulationRun).filter(
            SimulationRun.status.in_(["RUNNING", "PAUSED"])
        ).order_by(SimulationRun.started_at.desc()).first()

        if active_run:
            return {
                "id": active_run.id,
                "campaign_id": active_run.campaign_id,
                "status": cls._running_states.get(active_run.id, active_run.status),
                "event_rate_per_sec": active_run.event_rate_per_sec,
                "total_events_emitted": active_run.total_events_emitted,
                "duration_seconds": active_run.duration_seconds,
                "started_at": active_run.started_at.isoformat() if active_run.started_at else None,
                "paused_at": active_run.paused_at.isoformat() if active_run.paused_at else None,
                "stopped_at": active_run.stopped_at.isoformat() if active_run.stopped_at else None
            }
        return None

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
        if sim_id in cls._active_tasks:
            cls._active_tasks.pop(sim_id, None)

        db = SessionLocal()
        try:
            sim_run = db.query(SimulationRun).filter(SimulationRun.id == sim_id).first()
            if sim_run and sim_run.status in ["RUNNING", "PAUSED"]:
                sim_run.status = "COMPLETED"
                sim_run.stopped_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        await ws_manager.broadcast_event(
            {
                "type": "SIMULATION_COMPLETED",
                "simulation_id": sim_id,
                "total_events": events_emitted
            },
            simulation_id="global"
        )

    @classmethod
    def _generate_random_event(cls, sim_id: str, campaign_id: str, event_seq: int) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # Query actual platforms and accounts from database
            db_platforms = db.query(Platform).all()
            db_accounts = db.query(SyntheticAccount).all()
            db_posts = db.query(Post).filter(Post.campaign_id == campaign_id).all() if campaign_id else []
            camp = db.query(Campaign).filter(Campaign.id == campaign_id).first() if campaign_id else None

            if db_platforms:
                plat_obj = random.choice(db_platforms)
                chosen_plat = (plat_obj.id, plat_obj.name)
            else:
                chosen_plat = ("plat-live-01", "SimuTwitter")

            now_str = datetime.now(timezone.utc).isoformat()
            base_velocity = camp.velocity_events_per_hour if camp else 12.0
            sim_velocity = round(base_velocity + random.uniform(-1.5, 3.5), 2)
            base_reach = camp.total_reach if camp else 5000
            total_reach = int(base_reach + (event_seq * random.randint(50, 180)))

            # Distinguish threat campaigns from benign/science/low-risk initiatives
            camp_base_risk = camp.risk_score if camp else 0.75
            is_threat_campaign = (camp_base_risk >= 0.50)

            bot_accounts = [a for a in db_accounts if a.is_coordinated_actor or a.bot_probability > 0.5]
            credible_accounts = [a for a in db_accounts if not a.is_coordinated_actor and a.bot_probability <= 0.5]
            
            # Virtual verified handles if DB accounts are all bot seeds
            virtual_credible = [
                ("acc-factcheck-01", "@official_factcheck_desk", 0.02),
                ("acc-reuters-01", "@reuters_verify", 0.02),
                ("acc-comm-01", "@community_notes_live", 0.03),
                ("acc-science-01", "@verified_science_daily", 0.04),
                ("acc-academic-01", "@u_academic_observer", 0.06),
                ("acc-safety-01", "@national_safety_wire", 0.03)
            ]

            if is_threat_campaign:
                # In a threat cascade:
                # 60% = Adversarial dissemination (bots, high risk)
                # 25% = Live Fact-Check & Counter-Disinformation Debunks (verified, low risk!)
                # 15% = Institutional Official Clarification & Community context (low risk!)
                roll = random.random()
                if roll < 0.60:
                    event_category = "ADVERSARIAL"
                elif roll < 0.85:
                    event_category = "FACT_CHECK"
                else:
                    event_category = "OFFICIAL_NOTICE"
            else:
                # In a legitimate / scientific / low-risk campaign:
                # 85% = Verified discovery / legitimate broadcast (low risk: 4% - 18%)
                # 15% = Public discussion & inquiries (low risk: 10% - 25%)
                roll = random.random()
                if roll < 0.85:
                    event_category = "BENIGN_BROADCAST"
                else:
                    event_category = "ORGANIC_INQUIRY"

            if event_category == "ADVERSARIAL":
                if bot_accounts:
                    acc_obj = random.choice(bot_accounts)
                    chosen_acc = (acc_obj.id, acc_obj.pseudonym_handle, acc_obj.bot_probability)
                else:
                    chosen_acc = ("acc-synth-01", "@pulse_mesh_node", 0.91)

                event_type = random.choice(["POST", "RESHARE", "CROSS_PLATFORM_SHARE", "CONTENT_VARIANT"])
                risk_score = round(min(0.98, max(0.74, camp_base_risk + random.uniform(-0.05, 0.06))), 2)

                if db_posts:
                    chosen_post = random.choice(db_posts)
                    src_post_id = chosen_post.id
                    content_id = chosen_post.content_id
                    snippet = chosen_post.content.raw_text[:120] if chosen_post.content else (camp.target_narrative[:120] if camp else "Emergent disinformation signal circulating across nodes...")
                else:
                    src_post_id = f"post-sim-{random.randint(100, 199)}"
                    content_id = f"content-sim-{random.randint(1, 10)}"
                    snippet = camp.target_narrative if camp else "Emergent disinformation signal circulating across nodes..."

            elif event_category == "FACT_CHECK":
                if credible_accounts:
                    acc_obj = random.choice(credible_accounts)
                    chosen_acc = (acc_obj.id, acc_obj.pseudonym_handle, acc_obj.bot_probability)
                else:
                    chosen_acc = random.choice(virtual_credible)

                event_type = "FACT_CHECK_DEBUNK"
                risk_score = round(random.uniform(0.05, 0.16), 2)  # Low risk: 5% - 16%!
                src_post_id = f"post-fc-{random.randint(200, 299)}"
                content_id = f"content-fc-{random.randint(1, 10)}"

                camp_name_lower = (camp.name.lower() if camp else "") + " " + (camp.target_narrative.lower() if camp else "")
                if "grid" in camp_name_lower or "power" in camp_name_lower or "electric" in camp_name_lower:
                    debunk_templates = [
                        "FACT-CHECK DEBUNK: National electrical grid operators and telemetry confirm 100% stable frequency (60.0 Hz). Rumors of sabotage rated FALSE.",
                        "COMMUNITY NOTE: Independent energy watchdogs confirm zero cyber disruptions. Viral whistleblower claims originate from inauthentic bot cluster.",
                        "VERIFIED NOTICE: Energy Regulatory Commission statement: 'All national switching and substation nodes operating nominally with zero interference.'"
                    ]
                elif "water" in camp_name_lower:
                    debunk_templates = [
                        "FACT-CHECK DEBUNK: Municipal public health department tests confirm drinking water fully adheres to EPA purity guidelines. Contamination rumors false.",
                        "COMMUNITY NOTE: Independent laboratory assays show 0.0% abnormal chemical traces across all metropolitan reservoirs.",
                        "OFFICIAL CLARIFICATION: Defense ministry confirms leaked documents cited in viral posts are fabricated digital forgeries."
                    ]
                else:
                    debunk_templates = [
                        f"FACT-CHECK DEBUNK: Independent investigative analysts confirm viral narrative concerning '{camp.name if camp else 'threat'}' is unverified synthetic rumor.",
                        "COMMUNITY NOTE: Credible primary sources confirm operational normalcy; no verified evidence supports viral alarmist claims.",
                        "VERIFIED ALERT: Platform Trust & Safety team has flagged this propagation cluster for coordinated inauthentic amplification."
                    ]
                snippet = random.choice(debunk_templates)

            elif event_category == "OFFICIAL_NOTICE":
                if credible_accounts:
                    acc_obj = random.choice(credible_accounts)
                    chosen_acc = (acc_obj.id, acc_obj.pseudonym_handle, acc_obj.bot_probability)
                else:
                    chosen_acc = random.choice(virtual_credible)

                event_type = "OFFICIAL_NOTICE"
                risk_score = round(random.uniform(0.10, 0.25), 2)  # Low risk: 10% - 25%!
                src_post_id = f"post-off-{random.randint(300, 399)}"
                content_id = f"content-off-{random.randint(1, 10)}"
                snippet = "OFFICIAL ADVISORY: State emergency oversight committee confirms all public infrastructure operations proceeding normally. Citizen hotlines clear."

            elif event_category == "BENIGN_BROADCAST":
                if credible_accounts:
                    acc_obj = random.choice(credible_accounts)
                    chosen_acc = (acc_obj.id, acc_obj.pseudonym_handle, acc_obj.bot_probability)
                else:
                    chosen_acc = random.choice(virtual_credible)

                event_type = random.choice(["POST", "RESHARE", "QUOTE"])
                risk_score = round(min(0.22, max(0.04, camp_base_risk + random.uniform(-0.04, 0.04))), 2)  # Low risk: 4% - 22%!

                if db_posts:
                    chosen_post = random.choice(db_posts)
                    src_post_id = chosen_post.id
                    content_id = chosen_post.content_id
                    snippet = chosen_post.content.raw_text[:120] if chosen_post.content else (camp.target_narrative[:120] if camp else "Verified public outreach broadcast nominal...")
                else:
                    src_post_id = f"post-sci-{random.randint(400, 499)}"
                    content_id = f"content-sci-{random.randint(1, 10)}"
                    snippet = camp.target_narrative if camp else "Verified public research broadcast nominal..."

            else:  # ORGANIC_INQUIRY
                if credible_accounts:
                    acc_obj = random.choice(credible_accounts)
                    chosen_acc = (acc_obj.id, acc_obj.pseudonym_handle, acc_obj.bot_probability)
                else:
                    chosen_acc = random.choice(virtual_credible)

                event_type = random.choice(["REPLY", "QUOTE"])
                risk_score = round(random.uniform(0.08, 0.28), 2)
                src_post_id = f"post-org-{random.randint(500, 599)}"
                content_id = f"content-org-{random.randint(1, 10)}"
                snippet = "Community Discussion: 'Fascinating progress highlighted in the latest peer-reviewed report. Great to see transparent verification standards.'"

            return {
                "event_id": str(uuid.uuid4()),
                "simulation_id": sim_id,
                "campaign_id": campaign_id,
                "event_type": event_type,
                "source_post_id": src_post_id,
                "target_post_id": f"post-tgt-{uuid.uuid4().hex[:6]}",
                "account_id": chosen_acc[0],
                "account_handle": chosen_acc[1],
                "bot_probability": chosen_acc[2],
                "platform_id": chosen_plat[0],
                "platform_name": chosen_plat[1],
                "content_id": content_id,
                "content_snippet": snippet,
                "timestamp": now_str,
                "velocity": sim_velocity,
                "total_reach": total_reach,
                "risk_score": risk_score
            }
        finally:
            db.close()

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
