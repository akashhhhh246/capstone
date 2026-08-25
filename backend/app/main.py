import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging

# Ensure backend root in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.configuration.config import settings
from app.infrastructure.database.session import init_db, SessionLocal
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

background_ingestion_task = None

async def periodic_ingestion_worker():
    """Background worker periodically polling GDELT and RSS feeds."""
    ingestion_service = IngestionService()
    logger.info("Started periodic real-time public data ingestion background worker.")
    
    # Wait 10 seconds after server boot before first sync
    await asyncio.sleep(10)
    
    while True:
        try:
            db = SessionLocal()
            try:
                if settings.GDELT_ENABLED:
                    logger.info("Executing automated periodic GDELT news sync...")
                    ingestion_service.ingest_from_source("gdelt", db, limit=settings.GDELT_MAX_RESULTS)
                if settings.RSS_ENABLED:
                    logger.info("Executing automated periodic RSS feed sync...")
                    ingestion_service.ingest_from_source("rss", db, limit=15)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in periodic ingestion worker: {e}")

        # Sleep for configured polling interval
        poll_seconds = max(settings.GDELT_POLL_INTERVAL, 60)
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
async def health_check():
    """Health check endpoint for Render, Docker, and Kubernetes probes."""
    return JSONResponse(status_code=200, content={"status": "UP", "service": "aegis-defense-workbench", "version": "1.0.0"})

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
