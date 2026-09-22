import os
import sys
import time
import uuid
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from sqlalchemy.orm import Session

# Ensure backend root in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.configuration.config import settings
from app.infrastructure.database.session import init_db, SessionLocal, get_db
from app.domain.entities.models import Platform
from app.presentation.api.v1.detection import router as detection_router
from app.presentation.api.v1.content import router as content_router
from app.presentation.api.v1.provenance import router as provenance_router
from app.presentation.api.v1.propagation import router as propagation_router
from app.presentation.api.v1.campaigns import router as campaigns_router
from app.presentation.api.v1.simulation import router as simulation_router
from app.presentation.api.v1.models import router as models_router
from app.presentation.api.v1.dashboard import router as dashboard_router
from app.presentation.api.v1.data_sources import router as data_sources_router
from app.presentation.api.v1.live_content import router as live_content_router
from app.presentation.websocket.simulation_ws import ws_manager
from app.application.services.ingestion_service import IngestionService

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("provenance_defense_api")

def _run_background_sync(ingestion_service: IngestionService):
    """Synchronous worker executed in separate thread to avoid blocking asyncio event loop."""
    db = SessionLocal()
    try:
        if settings.GDELT_ENABLED:
            logger.info("Executing automated periodic GDELT news sync...")
            ingestion_service.ingest_from_source("gdelt", db, limit=settings.GDELT_MAX_RESULTS)
        if settings.RSS_ENABLED:
            logger.info("Executing automated periodic RSS feed sync...")
            ingestion_service.ingest_from_source("rss", db, limit=15)
    except Exception as e:
        logger.warning(f"Background data sync notice: {e}")
    finally:
        db.close()

async def periodic_ingestion_worker():
    """Background worker periodically polling GDELT and RSS feeds without blocking."""
    ingestion_service = IngestionService()
    logger.info("Started periodic real-time public data ingestion background worker.")
    
    # Wait 30 seconds after server boot to prioritize health checks and UI availability
    await asyncio.sleep(30)
    
    while True:
        try:
            await asyncio.to_thread(_run_background_sync, ingestion_service)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic ingestion worker: {e}")

        # Sleep for configured polling interval
        poll_seconds = max(settings.GDELT_POLL_INTERVAL, 180)
        await asyncio.sleep(poll_seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and auto-seed if empty
    logger.info("Initializing database schema...")
    init_db()
    
    db = SessionLocal()
    try:
        if db.query(Platform).count() == 0:
            logger.info("Seeding initial research prototype data...")
            from seed_db import seed_database
            seed_database()
    except Exception as e:
        logger.warning(f"Auto-seed check notice: {e}")
    finally:
        db.close()

    # Launch background ingestion worker
    task = asyncio.create_task(periodic_ingestion_worker())
        
    yield
    
    logger.info("Cancelling periodic ingestion background worker...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    logger.info("Shutting down API server...")

app = FastAPI(
    title="Information Integrity & AI Defense Workbench API",
    description="""
Defensive Cybersecurity and Information Integrity Research Prototype:
- AI-Generated Content Detection (TF-IDF Classifier, GLTR Statistical Token Ranking, Watermark Audit)
- Content Provenance & Lineage Reconstruction (DAG Builder, Dense Embeddings)
- Real-Time Public Data Ingestion (GDELT Project DOC 2.0 API, RSS Feeds, Bluesky Connector)
- Multi-Platform Propagation Graph Analysis (NetworkX, PyG GraphSAGE GNN)
- Explainable Threat Campaign Intelligence
- Real-Time Synthetic Social Media Propagation Simulator (WebSockets)
    """,
    version="1.0.0",
    lifespan=lifespan
)

SERVER_START_TIME = datetime.now(timezone.utc)

# Middleware: Request Correlation ID, Process Time & OWASP Security Headers
@app.middleware("http")
async def correlation_and_security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled Exception [RequestID: {request_id}] on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://errors.aishield.internal/server-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected server error occurred during request processing.",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            headers={"X-Request-ID": request_id}
        )
    
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time}ms"
    
    if getattr(settings, "SECURITY_HEADERS_ENABLED", True):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
    return response

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [str(settings.CORS_ORIGINS)]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["http://localhost:9207", "http://127.0.0.1:9207"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(detection_router, prefix=settings.API_V1_STR)
app.include_router(content_router, prefix=settings.API_V1_STR)
app.include_router(provenance_router, prefix=settings.API_V1_STR)
app.include_router(propagation_router, prefix=settings.API_V1_STR)
app.include_router(campaigns_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(data_sources_router, prefix=f"{settings.API_V1_STR}/data-sources", tags=["Data Sources"])
app.include_router(live_content_router, prefix=f"{settings.API_V1_STR}/live-content", tags=["Live Content"])

# WebSocket Endpoints
@app.websocket(f"{settings.API_V1_STR}/ws/simulation/{{simulation_id}}")
async def websocket_simulation_endpoint(websocket: WebSocket, simulation_id: str):
    await ws_manager.connect(websocket, simulation_id=simulation_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, simulation_id=simulation_id)
    except Exception:
        ws_manager.disconnect(websocket, simulation_id=simulation_id)

@app.websocket(f"{settings.API_V1_STR}/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, simulation_id="global")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, simulation_id="global")
    except Exception:
        ws_manager.disconnect(websocket, simulation_id="global")

@app.api_route("/health", methods=["GET", "HEAD"])
@app.api_route(f"{settings.API_V1_STR}/health", methods=["GET", "HEAD"])
async def enterprise_health_check(db: Session = Depends(get_db)):
    """
    Deep Enterprise Health & Telemetry Check.
    Verifies database connectivity, ML model availability, entity counts, and process uptime.
    """
    from sqlalchemy import text
    from app.domain.entities.models import Content, Campaign, SyntheticAccount
    db_status = "HEALTHY"
    db_latency_ms = 0.0
    entity_counts = {}
    
    t0 = time.time()
    try:
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - t0) * 1000, 2)
        entity_counts = {
            "contents": db.query(Content).count(),
            "campaigns": db.query(Campaign).count(),
            "platforms": db.query(Platform).count(),
            "accounts": db.query(SyntheticAccount).count()
        }
    except Exception as e:
        db_status = f"DEGRADED: {str(e)}"
        logger.error(f"Health check database failure: {e}")

    model_artifacts = {
        "tfidf_classifier": os.path.exists(settings.TFIDF_MODEL_PATH),
        "gnn_model": os.path.exists(settings.GNN_MODEL_PATH),
        "embedding_model": settings.EMBEDDING_MODEL
    }
    all_models_present = all([model_artifacts["tfidf_classifier"], model_artifacts["gnn_model"]])

    uptime_sec = int((datetime.now(timezone.utc) - SERVER_START_TIME).total_seconds())
    is_healthy = (db_status == "HEALTHY") and all_models_present
    status_code = 200 if is_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "UP" if is_healthy else "DEGRADED",
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "environment": os.environ.get("ENVIRONMENT", "production"),
            "uptime_seconds": uptime_sec,
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
                "records": entity_counts
            },
            "model_artifacts": model_artifacts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Serve built frontend dist assets if present
candidate_dist_paths = [
    os.path.abspath(os.path.join(os.path.dirname(backend_dir), "frontend", "dist")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "frontend", "dist")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend", "dist")),
    os.path.abspath("../frontend/dist"),
]

frontend_dist = next((p for p in candidate_dist_paths if os.path.exists(p)), None)

if frontend_dist and os.path.exists(frontend_dist):
    logger.info(f"Mounted production frontend bundle from: {frontend_dist}")
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    async def serve_frontend_spa(request: Request, full_path: str):
        # If API or Docs route, pass through
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"detail": "Frontend bundle not found"})
else:
    logger.warning("Frontend dist bundle not found; serving fallback API landing.")
    @app.api_route("/", methods=["GET", "HEAD"])
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs_url": "/docs",
            "status": "OPERATIONAL"
        }
