import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.infrastructure.database.session import get_db
from app.application.services.ingestion_service import IngestionService

router = APIRouter()
logger = logging.getLogger("api_data_sources")

ingestion_service = IngestionService()

class SyncRequest(BaseModel):
    limit: Optional[int] = 25
    query: Optional[str] = None

@router.get("", summary="List all registered data source connectors and configs")
def get_data_sources(db: Session = Depends(get_db)):
    """Retrieve all available data source connectors and their operational states."""
    return ingestion_service.get_all_statuses(db)

@router.get("/status", summary="Get data source health and monitoring status")
def get_data_sources_status(db: Session = Depends(get_db)):
    """Return health metrics (connected, records ingested, duplicates skipped, last sync) for GDELT, RSS, Bluesky."""
    return {
        "status": "OPERATIONAL",
        "sources": ingestion_service.get_all_statuses(db)
    }

@router.post("/gdelt/sync", summary="Trigger on-demand GDELT news ingestion sync")
def sync_gdelt(req: SyncRequest = SyncRequest(), db: Session = Depends(get_db)):
    """
    Fetch recent articles from GDELT Project DOC 2.0 API, normalize, deduplicate,
    execute Part 1 ML Detection pipeline, and persist to database.
    """
    result = ingestion_service.ingest_from_source("gdelt", db, limit=req.limit or 25, query=req.query)
    if "error" in result and result.get("ingested", 0) == 0 and "disabled" in result.get("error", "").lower():
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/rss/sync", summary="Trigger on-demand RSS feed ingestion sync")
def sync_rss(req: SyncRequest = SyncRequest(), db: Session = Depends(get_db)):
    """Fetch and ingest recent items from configured public RSS feeds."""
    result = ingestion_service.ingest_from_source("rss", db, limit=req.limit or 25, query=req.query)
    return result

@router.post("/poll-all", summary="Poll all enabled data sources in sequence")
def poll_all_sources(db: Session = Depends(get_db)):
    """Execute background ingestion across all enabled public data connectors."""
    return ingestion_service.poll_all_sources(db)
