import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure backend root in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.infrastructure.database.session import SessionLocal, init_db
from app.application.services.detection_service import DetectionService
from app.application.services.provenance_service import ProvenanceService
from app.application.services.propagation_service import PropagationService
from app.application.services.campaign_service import CampaignService

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def detection_service():
    return DetectionService()

@pytest.fixture
def provenance_service():
    return ProvenanceService()

@pytest.fixture
def propagation_service():
    return PropagationService()

@pytest.fixture
def campaign_service():
    return CampaignService()
