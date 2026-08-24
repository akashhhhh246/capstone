import logging
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.connectors.base_connector import DataSourceConnector
from app.domain.schemas.normalized_content import NormalizedContent
from app.domain.entities.models import Content, DetectionResult, DataSourceAudit
from app.infrastructure.connectors.gdelt_connector import GDELTConnector
from app.infrastructure.connectors.rss_connector import RSSConnector
from app.infrastructure.connectors.bluesky_connector import BlueskyConnector
from app.ml.detection.preprocessing import TextPreprocessor
from app.application.services.detection_service import DetectionService
from app.presentation.websocket.simulation_ws import ws_manager

logger = logging.getLogger("ingestion_service")

class IngestionService:
    """
    Orchestrates real-time public data ingestion, normalization, deduplication,
    automatic Part 1 AI content detection, and live WebSocket telemetry publishing.
    """

    def __init__(self, detection_service: Optional[DetectionService] = None):
        self.detection_service = detection_service or DetectionService()
        self.connectors: Dict[str, DataSourceConnector] = {
            "gdelt": GDELTConnector(),
            "rss": RSSConnector(),
            "bluesky": BlueskyConnector(),
        }

    def get_connector(self, source_type: str) -> Optional[DataSourceConnector]:
        return self.connectors.get(source_type.lower())

    def get_all_statuses(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Return status telemetry for all registered connectors."""
        statuses = []
        for key, connector in self.connectors.items():
            st = connector.get_status()
            
            # Enrich with database audit records if available
            if db:
                audit = db.query(DataSourceAudit).filter(DataSourceAudit.source_name == connector.name).first()
                if audit:
                    st["total_ingested"] = audit.total_ingested
                    st["duplicates_skipped"] = audit.duplicates_skipped
                    if audit.last_sync_at:
                        st["last_sync_at"] = audit.last_sync_at.isoformat()
                    if audit.last_error:
                        st["last_error"] = audit.last_error

            statuses.append(st)
        return statuses

    def ingest_from_source(
        self,
        source_key: str,
        db: Session,
        limit: int = 25,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Poll single data source, normalize, deduplicate against DB,
        persist Content, execute Detection Pipeline, and broadcast event.
        """
        connector = self.get_connector(source_key)
        if not connector:
            return {"error": f"Unknown data source connector: '{source_key}'", "ingested": 0, "skipped": 0}

        try:
            raw_items: List[NormalizedContent] = connector.fetch_recent(limit=limit, query=query)
        except Exception as e:
            logger.error(f"Error fetching from connector {source_key}: {e}")
            connector.last_error = str(e)
            return {"error": str(e), "ingested": 0, "skipped": 0}

        ingested_count = 0
        skipped_count = 0
        now = datetime.now(timezone.utc)
        ingested_records = []

        for item in raw_items:
            # 1. Deduplication Check (by URL or text hash)
            existing = None
            if item.url:
                existing = db.query(Content).filter(Content.url == item.url).first()
            if not existing and item.content_hash:
                existing = db.query(Content).filter(Content.text_hash == item.content_hash).first()

            if existing:
                skipped_count += 1
                connector.duplicates_skipped += 1
                continue

            # 2. Text Preprocessing
            clean = TextPreprocessor.clean_text(item.content)
            features = TextPreprocessor.extract_features(clean)
            text_hash = item.content_hash or hashlib.sha256(clean.encode("utf-8")).hexdigest()

            # 3. Create Content Record
            content_obj = Content(
                id=item.id,
                text_hash=text_hash,
                title=item.title[:255] if item.title else None,
                raw_text=item.content,
                clean_text=clean,
                url=item.url[:500] if item.url else None,
                source_name=item.source_name[:100] if item.source_name else connector.name,
                source_type=item.source_type,
                author=item.author[:100] if item.author else None,
                published_at=item.published_at,
                ingested_at=now,
                source_label=f"real_world_{item.source_type}",
                domain=item.topics[0].lower() if item.topics else "general",
                language=item.language,
                country=item.country,
                topics=item.topics,
                entities=item.entities,
                data_origin="REAL_WORLD",
                word_count=features["word_count"],
                char_count=features["char_count"],
                created_at=now
            )
            db.add(content_obj)
            db.flush()

            # 4. Automatic ML Detection Pipeline (Part 1 Zero-Bypass)
            det_res = self.detection_service.analyze_text(clean, domain=content_obj.domain)
            det_record = DetectionResult(
                id=f"det-{content_obj.id}",
                content_id=content_obj.id,
                classification=det_res["classification"],
                confidence=det_res["confidence"],
                ai_probability=det_res["ai_probability"],
                model_version=det_res["model_version"],
                gltr_stats=det_res["gltr_result"]["bucket_distribution"],
                watermark_status=det_res["watermark_result"]["status"],
                watermark_details=det_res["watermark_result"]["details"],
                statistical_features=det_res["statistical_features"],
                indicators=det_res["indicators"],
                is_heuristic_fallback=det_res.get("is_heuristic_fallback", False),
                created_at=now
            )
            db.add(det_record)
            db.flush()

            ingested_count += 1
            connector.total_ingested += 1

            record_summary = {
                "id": content_obj.id,
                "title": content_obj.title,
                "url": content_obj.url,
                "source_name": content_obj.source_name,
                "source_type": content_obj.source_type,
                "published_at": content_obj.published_at.isoformat() if content_obj.published_at else None,
                "ingested_at": content_obj.ingested_at.isoformat() if content_obj.ingested_at else None,
                "topics": content_obj.topics,
                "data_origin": content_obj.data_origin,
                "classification": det_record.classification,
                "confidence": det_record.confidence,
                "ai_probability": det_record.ai_probability,
                "indicators": det_record.indicators,
                "risk_score": round(det_record.ai_probability * 0.85, 2)
            }
            ingested_records.append(record_summary)

            # 5. Broadcast to Live WebSocket clients
            try:
                import asyncio
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    pass

                if loop and loop.is_running():
                    loop.create_task(ws_manager.broadcast_to_all({
                        "event_type": "REAL_WORLD_CONTENT_INGESTED",
                        "payload": record_summary
                    }))
            except Exception as ws_err:
                logger.debug(f"WebSocket broadcast skipped: {ws_err}")

        # Update or create DataSourceAudit record
        audit = db.query(DataSourceAudit).filter(DataSourceAudit.source_name == connector.name).first()
        if not audit:
            audit = DataSourceAudit(
                source_name=connector.name,
                is_enabled=connector.is_enabled,
                status=connector.status,
                total_ingested=connector.total_ingested,
                duplicates_skipped=connector.duplicates_skipped,
                last_sync_at=now,
                last_error=connector.last_error
            )
            db.add(audit)
        else:
            audit.status = connector.status
            audit.total_ingested += ingested_count
            audit.duplicates_skipped += skipped_count
            audit.last_sync_at = now
            audit.last_error = connector.last_error

        db.commit()

        return {
            "source": connector.name,
            "source_type": source_key,
            "ingested": ingested_count,
            "skipped_duplicates": skipped_count,
            "records": ingested_records,
            "last_sync_at": now.isoformat()
        }

    def poll_all_sources(self, db: Session) -> Dict[str, Any]:
        """Poll all enabled public connectors in sequence."""
        results = {}
        for key, connector in self.connectors.items():
            if connector.is_enabled:
                logger.info(f"Running automated background ingestion for: {connector.name}")
                res = self.ingest_from_source(key, db)
                results[key] = res
            else:
                results[key] = {"status": "DISABLED", "ingested": 0, "skipped": 0}
        return results
