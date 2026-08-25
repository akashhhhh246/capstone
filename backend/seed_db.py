import os
import sys
import json
import hashlib
from datetime import datetime, timezone, timedelta

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from app.infrastructure.database.session import SessionLocal, init_db, engine
from app.domain.entities.models import (
    Base, Platform, SyntheticAccount, Content, DetectionResult, Campaign, Post, PropagationEvent
)
from app.ml.detection.preprocessing import TextPreprocessor
from app.application.services.detection_service import DetectionService

def seed_database(force_reseed: bool = False):
    print("==================================================")
    print("Seeding Research Prototype Database (Clustered)...")
    print("==================================================")
    
    if force_reseed:
        print("Re-creating database tables for clean cluster seeding...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        init_db()

    db = SessionLocal()
    detection_service = DetectionService()

    try:
        if not force_reseed and db.query(Platform).count() > 0:
            print("Database already contains seeded entities. Skipping re-seed.")
            return

        now = datetime.now(timezone.utc)

        # 1. Seed Platforms
        platforms = [
            Platform(id="plat-01", name="SimuTwitter", platform_type="microblogging", risk_weight=1.2, description="Simulated fast-turnaround microblogging service", icon_name="twitter"),
            Platform(id="plat-02", name="SimuTelegram", platform_type="messaging_channel", risk_weight=1.4, description="Simulated broadcast messaging channels with low moderation", icon_name="send"),
            Platform(id="plat-03", name="SimuReddit", platform_type="community_forum", risk_weight=0.9, description="Simulated threaded community forum with upvoting mechanics", icon_name="message-square"),
            Platform(id="plat-04", name="SimuNewsWire", platform_type="syndicated_news", risk_weight=1.5, description="Simulated open-publishing pseudo-journalism aggregator", icon_name="globe"),
        ]
        db.add_all(platforms)
        db.flush()
        print(f"  -> Added {len(platforms)} simulated platforms.")

        # 2. Seed Synthetic Accounts (Pseudonymized)
        accounts = [
            SyntheticAccount(id="acc-01", platform_id="plat-01", pseudonym_handle="@synth_relay_alpha", account_age_days=12, bot_probability=0.94, follower_count=1200, following_count=45, is_coordinated_actor=True),
            SyntheticAccount(id="acc-02", platform_id="plat-01", pseudonym_handle="@pulse_mesh_node", account_age_days=8, bot_probability=0.89, follower_count=850, following_count=30, is_coordinated_actor=True),
            SyntheticAccount(id="acc-03", platform_id="plat-02", pseudonym_handle="@shadow_wire_channel", account_age_days=45, bot_probability=0.92, follower_count=5400, following_count=10, is_coordinated_actor=True),
            SyntheticAccount(id="acc-04", platform_id="plat-02", pseudonym_handle="@intel_echo_vault", account_age_days=60, bot_probability=0.85, follower_count=3200, following_count=12, is_coordinated_actor=True),
            SyntheticAccount(id="acc-05", platform_id="plat-03", pseudonym_handle="@u_curious_truth_seeker", account_age_days=180, bot_probability=0.72, follower_count=140, following_count=89, is_coordinated_actor=True),
            SyntheticAccount(id="acc-06", platform_id="plat-04", pseudonym_handle="@wire_syndicate_bot", account_age_days=300, bot_probability=0.98, follower_count=12000, following_count=0, is_coordinated_actor=True),
            SyntheticAccount(id="acc-07", platform_id="plat-01", pseudonym_handle="@verified_science_daily", account_age_days=1200, bot_probability=0.04, follower_count=45000, following_count=350, is_coordinated_actor=False),
            SyntheticAccount(id="acc-08", platform_id="plat-03", pseudonym_handle="@u_academic_observer", account_age_days=800, bot_probability=0.08, follower_count=420, following_count=110, is_coordinated_actor=False),
        ]
        db.add_all(accounts)
        db.flush()
        print(f"  -> Added {len(accounts)} synthetic pseudonymized accounts.")

        # 3. Load Rich Sample Dataset & Register Contents with Detections
        dataset_path = os.path.join(backend_dir, "data", "sample_dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            sample_data = json.load(f)

        content_map = {}

        for i, item in enumerate(sample_data):
            c_id = item["id"]
            text = item["text"]
            clean = TextPreprocessor.clean_text(text)
            features = TextPreprocessor.extract_features(clean)
            text_hash = hashlib.sha256(clean.encode("utf-8")).hexdigest()
            created_time = now - timedelta(hours=(len(sample_data) - i))

            content_obj = Content(
                id=c_id,
                text_hash=text_hash,
                raw_text=text,
                clean_text=clean,
                source_label=item.get("source_type", "benchmark_dataset"),
                domain=item.get("domain", "general"),
                word_count=features["word_count"],
                char_count=features["char_count"],
                created_at=created_time
            )
            db.add(content_obj)
            db.flush()
            content_map[c_id] = c_id

            # Run detection
            det_res = detection_service.analyze_text(clean, domain=item.get("domain", "general"))
            det_record = DetectionResult(
                id=f"det-{i+1:03d}",
                content_id=c_id,
                classification=item.get("label", det_res["classification"]),
                confidence=det_res["confidence"],
                ai_probability=0.92 if item.get("label") == "AI_GENERATED" else 0.08,
                model_version=det_res["model_version"],
                gltr_stats=det_res["gltr_result"]["bucket_distribution"],
                watermark_status="DETECTED" if item.get("source_type") == "synthetic_seed" else det_res["watermark_result"]["status"],
                watermark_details=det_res["watermark_result"]["details"],
                statistical_features=det_res["statistical_features"],
                indicators=det_res["indicators"],
                is_heuristic_fallback=False,
                created_at=created_time
            )
            db.add(det_record)

        print(f"  -> Added {len(sample_data)} rich benchmark content items and detection results.")

        # 4. Seed Tracked Campaigns
        campaigns = [
            Campaign(
                id="camp-01",
                name="Operation GridPulse",
                objective="Fabricate nationwide emergency electrical blackout directives to induce civil panic",
                target_narrative="Confidential government whistleblowers claim coordinated power grid shutdown at midnight",
                status="ACTIVE",
                risk_score=0.88,
                gnn_risk_score=0.84,
                explainability_reasons=[
                    "[NARRATIVE HARM] Fabricates nationwide critical infrastructure shutdown with explicit call-to-action urging emergency bank fund withdrawals to trigger financial ATM panic.",
                    "[COORDINATED NETWORK] GraphSAGE GNN identified synchronized inauthentic burst topology across low-age (<15 days) pseudonymized relay accounts with 85%+ bot probability.",
                    "[EVASION TACTIC] Coordinated multi-platform astroturfing across Telegram, microblogs, and forums deploying 6 paraphrased mutation variants to evade exact-match moderation filters.",
                    "[AI SYNTHESIS] Stylometric n-gram classifier confirms synthetic text generation (85% probability) used to mass-produce mutations at high diffusion velocity (18.4 events/hr)."
                ],
                total_events=42,
                total_reach=18500,
                total_platforms=4,
                velocity_events_per_hour=18.4,
                branching_factor=3.8,
                created_at=now - timedelta(hours=8)
            ),
            Campaign(
                id="camp-02",
                name="DeepWater Alert",
                objective="Spread unverified public health panic regarding municipal tap water contamination",
                target_narrative="Leaked defense ministry documents prove metropolitan water filtration laced with chemicals",
                status="ACTIVE",
                risk_score=0.82,
                gnn_risk_score=0.79,
                explainability_reasons=[
                    "[NARRATIVE HARM] Deceptive public health crisis claims alleging metropolitan chemical poisoning with alarmist directives to avoid municipal tap water.",
                    "[COORDINATED NETWORK] High concentration of automated syndication bots (75%) executing synchronized cross-platform broadcast relays across 3 channels.",
                    "[EVASION TACTIC] Employs synthetic lexical rephrasing and hashtag injection (#WaterGateAlert) to manufacture organic viral momentum.",
                    "[AI SYNTHESIS] High linguistic model confidence (82%) identifying template-based prompt generation with characteristic low-burstiness sentence cadence."
                ],
                total_events=31,
                total_reach=12400,
                total_platforms=3,
                velocity_events_per_hour=12.6,
                branching_factor=2.9,
                created_at=now - timedelta(hours=14)
            ),
            Campaign(
                id="camp-05",
                name="LithoPulse Supply Cascade",
                objective="Coordinated rumor propagation regarding critical semiconductor equipment export bans",
                target_narrative="Unverified leaks allege covert supply chain halt on High-NA EUV lithography systems",
                status="ACTIVE",
                risk_score=0.68,
                gnn_risk_score=0.64,
                explainability_reasons=[
                    "[NARRATIVE HARM] Market-destabilizing speculation targeting international semiconductor supply chain tools to distort technology equities.",
                    "[COORDINATED NETWORK] Rapid automated cross-posting on Telegram channels and pseudo-news aggregators with elevated betweenness centrality.",
                    "[EVASION TACTIC] Paraphrases legitimate financial wire excerpts with sensationalist exaggerations to mimic authoritative reporting.",
                    "[AI SYNTHESIS] Moderate AI probability (68%) indicating machine-assisted journalistic paraphrasing with uniform syntactic structure."
                ],
                total_events=22,
                total_reach=9800,
                total_platforms=3,
                velocity_events_per_hour=8.4,
                branching_factor=2.4,
                created_at=now - timedelta(hours=18)
            ),
            Campaign(
                id="camp-06",
                name="Solid-State Energy Speculation",
                objective="Viral exaggeration of laboratory-stage solid-state battery commercial readiness",
                target_narrative="Speculative claims of immediate consumer solid-state battery integration in domestic EV fleets",
                status="ACTIVE",
                risk_score=0.44,
                gnn_risk_score=0.38,
                explainability_reasons=[
                    "[NARRATIVE HARM] Commercial technology hype cycle overstating lab readiness without severe civil or infrastructure panic intent.",
                    "[COORDINATED NETWORK] Predominantly organic enthusiast discussion mixed with minor automated news-relay accounts (25% bot density).",
                    "[EVASION TACTIC] Low evasion behavior; standard cross-forum sharing without coordinated astroturfing signatures.",
                    "[AI SYNTHESIS] Mild synthetic indicators (44%) consistent with automated PR aggregation tools and press summary generators."
                ],
                total_events=14,
                total_reach=5200,
                total_platforms=2,
                velocity_events_per_hour=4.6,
                branching_factor=1.7,
                created_at=now - timedelta(hours=20)
            ),
            Campaign(
                id="camp-03",
                name="JWST Cosmic Outreach",
                objective="Authentic scientific discovery syndication across research and news platforms",
                target_narrative="NASA's James Webb Space Telescope captures deepest infrared image of galaxy cluster SMACS 0723",
                status="CONTAINED",
                risk_score=0.08,
                gnn_risk_score=0.06,
                explainability_reasons=[
                    "[NARRATIVE HARM] Zero harm vector; legitimate scientific educational dissemination regarding deep-field galaxy astrophysics.",
                    "[COORDINATED NETWORK] 100% organic human propagation verified through peer institutions, official science channels, and academic observers.",
                    "[EVASION TACTIC] Zero evasion indicators; transparent attribution with verbatim wire syndication and educational summaries.",
                    "[AI SYNTHESIS] Benign AI assistance (32%) limited to auxiliary news brief formatting without deceptive or malicious intent."
                ],
                total_events=12,
                total_reach=64000,
                total_platforms=3,
                velocity_events_per_hour=3.2,
                branching_factor=1.4,
                created_at=now - timedelta(hours=22)
            ),
            Campaign(
                id="camp-04",
                name="AI Governance Briefing",
                objective="Policy discussions regarding EU AI Act compliance standards and foundation model audits",
                target_narrative="European Parliament and Council reach political agreement on landmark AI Act",
                status="CONTAINED",
                risk_score=0.15,
                gnn_risk_score=0.12,
                explainability_reasons=[
                    "[NARRATIVE HARM] Constructive civic policy analysis covering legislative compliance standards for foundation models.",
                    "[COORDINATED NETWORK] Natural multi-community discourse across technology forums and legal policy analysts with 0% bot coordination.",
                    "[EVASION TACTIC] Transparent public citations and verified links to official European Parliament communiques.",
                    "[AI SYNTHESIS] Low-risk baseline synthesis (28%) representing standard automated policy brief translation."
                ],
                total_events=16,
                total_reach=28000,
                total_platforms=3,
                velocity_events_per_hour=4.1,
                branching_factor=1.6,
                created_at=now - timedelta(hours=26)
            )
        ]
        db.add_all(campaigns)
        db.flush()
        print(f"  -> Added {len(campaigns)} tracked research campaigns.")

        # 5. Seed Multi-Platform Posts linking Clustered Contents
        posts = [
            # JWST Cluster Posts (Science Wire -> Microblog -> Forum)
            Post(id="post-jwst-01", platform_id="plat-04", account_id="acc-07", content_id="jwst-001", campaign_id="camp-03", post_type="ORIGINAL", likes=1420, reshares=890, published_at=now - timedelta(hours=21)),
            Post(id="post-jwst-02", platform_id="plat-01", account_id="acc-07", content_id="jwst-002", parent_post_id="post-jwst-01", campaign_id="camp-03", post_type="REPOST", likes=950, reshares=430, published_at=now - timedelta(hours=20)),
            Post(id="post-jwst-03", platform_id="plat-03", account_id="acc-08", content_id="jwst-003", parent_post_id="post-jwst-02", campaign_id="camp-03", post_type="QUOTE", likes=310, reshares=85, published_at=now - timedelta(hours=18)),

            # AI Governance Cluster Posts (Policy wire -> Twitter -> Reddit)
            Post(id="post-aigov-01", platform_id="plat-04", account_id="acc-07", content_id="ai-reg-001", campaign_id="camp-04", post_type="ORIGINAL", likes=820, reshares=340, published_at=now - timedelta(hours=25)),
            Post(id="post-aigov-02", platform_id="plat-01", account_id="acc-07", content_id="ai-reg-002", parent_post_id="post-aigov-01", campaign_id="camp-04", post_type="CROSS_PLATFORM", likes=540, reshares=210, published_at=now - timedelta(hours=24)),
            Post(id="post-aigov-03", platform_id="plat-03", account_id="acc-08", content_id="ai-reg-003", parent_post_id="post-aigov-02", campaign_id="camp-04", post_type="REPLY", likes=190, reshares=45, published_at=now - timedelta(hours=22)),

            # Operation GridPulse Posts (Origin -> SimuTwitter -> SimuTelegram -> SimuReddit -> SimuNewsWire)
            Post(id="post-grid-01", platform_id="plat-01", account_id="acc-01", content_id="grid-001", campaign_id="camp-01", post_type="ORIGINAL", likes=340, reshares=180, published_at=now - timedelta(hours=7)),
            Post(id="post-grid-02", platform_id="plat-01", account_id="acc-02", content_id="grid-002", parent_post_id="post-grid-01", campaign_id="camp-01", post_type="REPOST", likes=120, reshares=95, published_at=now - timedelta(hours=6, minutes=30)),
            Post(id="post-grid-03", platform_id="plat-02", account_id="acc-03", content_id="grid-002", parent_post_id="post-grid-01", campaign_id="camp-01", post_type="CROSS_PLATFORM", likes=890, reshares=410, published_at=now - timedelta(hours=6)),
            Post(id="post-grid-04", platform_id="plat-02", account_id="acc-04", content_id="grid-003", parent_post_id="post-grid-03", campaign_id="camp-01", post_type="REPLY", likes=210, reshares=140, published_at=now - timedelta(hours=5)),
            Post(id="post-grid-05", platform_id="plat-03", account_id="acc-05", content_id="grid-003", parent_post_id="post-grid-04", campaign_id="camp-01", post_type="QUOTE", likes=450, reshares=220, published_at=now - timedelta(hours=4)),
            Post(id="post-grid-06", platform_id="plat-04", account_id="acc-06", content_id="grid-004", parent_post_id="post-grid-05", campaign_id="camp-01", post_type="CROSS_PLATFORM", likes=1500, reshares=600, published_at=now - timedelta(hours=3)),

            # DeepWater Alert Posts
            Post(id="post-water-01", platform_id="plat-02", account_id="acc-03", content_id="water-001", campaign_id="camp-02", post_type="ORIGINAL", likes=560, reshares=290, published_at=now - timedelta(hours=13)),
            Post(id="post-water-02", platform_id="plat-01", account_id="acc-01", content_id="water-002", parent_post_id="post-water-01", campaign_id="camp-02", post_type="CROSS_PLATFORM", likes=420, reshares=190, published_at=now - timedelta(hours=11)),
            Post(id="post-water-03", platform_id="plat-03", account_id="acc-05", content_id="water-002", parent_post_id="post-water-02", campaign_id="camp-02", post_type="REPOST", likes=180, reshares=75, published_at=now - timedelta(hours=10)),
        ]
        db.add_all(posts)
        db.flush()
        print(f"  -> Added {len(posts)} multi-platform provenance posts.")

        # 6. Seed Propagation Events
        events = [
            PropagationEvent(id="ev-01", campaign_id="camp-01", event_type="POST", source_post_id=None, target_post_id="post-grid-01", account_id="acc-01", platform_id="plat-01", content_id="grid-001", timestamp=now - timedelta(hours=7)),
            PropagationEvent(id="ev-02", campaign_id="camp-01", event_type="RESHARE", source_post_id="post-grid-01", target_post_id="post-grid-02", account_id="acc-02", platform_id="plat-01", content_id="grid-002", timestamp=now - timedelta(hours=6, minutes=30)),
            PropagationEvent(id="ev-03", campaign_id="camp-01", event_type="CROSS_PLATFORM_SHARE", source_post_id="post-grid-01", target_post_id="post-grid-03", account_id="acc-03", platform_id="plat-02", content_id="grid-002", timestamp=now - timedelta(hours=6)),
            PropagationEvent(id="ev-04", campaign_id="camp-01", event_type="CONTENT_VARIANT", source_post_id="post-grid-03", target_post_id="post-grid-04", account_id="acc-04", platform_id="plat-02", content_id="grid-003", timestamp=now - timedelta(hours=5)),
            PropagationEvent(id="ev-05", campaign_id="camp-01", event_type="QUOTE", source_post_id="post-grid-04", target_post_id="post-grid-05", account_id="acc-05", platform_id="plat-03", content_id="grid-003", timestamp=now - timedelta(hours=4)),
            PropagationEvent(id="ev-06", campaign_id="camp-01", event_type="CROSS_PLATFORM_SHARE", source_post_id="post-grid-05", target_post_id="post-grid-06", account_id="acc-06", platform_id="plat-04", content_id="grid-004", timestamp=now - timedelta(hours=3)),
        ]
        db.add_all(events)
        db.commit()
        print(f"  -> Added {len(events)} propagation event records.")

        print("==================================================")
        print("Clustered Database Seeding Completed Successfully!")
        print("==================================================")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(force_reseed=True)
