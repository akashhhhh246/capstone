# Backend Modular Monolith — LLM Malign Information Operations Defense

Defensive Cybersecurity and Information Integrity Research Prototype Backend.

## Architecture
- **Framework**: FastAPI (Python 3.12+)
- **Database Layer**: SQLAlchemy 2.0 ORM + Alembic migrations (PostgreSQL with automatic SQLite zero-friction local fallback)
- **Machine Learning Layer**:
  - **Part 1 Content Detection**: Scikit-Learn TF-IDF + Logistic Regression binary classifier (`HUMAN` vs `AI_GENERATED`), GLTR-style statistical token probability visualizer, and Kirchenbauer green-list watermark detector.
  - **Part 2 Content Provenance & Graph Analysis**: Dense `sentence-transformers` (`all-MiniLM-L6-v2`) semantic embeddings, NetworkX multi-platform propagation graph builder, PyTorch Geometric GraphSAGE GNN cascade risk model.
  - **Explainable Risk Scoring**: Deterministic multi-factor risk scoring engine providing itemized explainability reasons.
  - **Real-Time Simulation Hub**: Asynchronous event generator streaming multi-platform social media cascade events over WebSockets (`POST`, `RESHARE`, `REPLY`, `QUOTE`, `CROSS_PLATFORM_SHARE`, `CONTENT_VARIANT`).

## Folder Structure
```
backend/
├── app/
│   ├── domain/entities/models.py       # SQLAlchemy ORM models & enums
│   ├── application/
│   │   ├── services/                   # Detection, Provenance, Propagation, Campaign, Simulation
│   │   └── dto/schemas.py              # Pydantic request/response DTOs
│   ├── infrastructure/
│   │   ├── configuration/config.py     # Pydantic settings (.env)
│   │   └── database/session.py         # SQLAlchemy engine & session factory
│   ├── ml/
│   │   ├── detection/                  # Preprocessing, TF-IDF Classifier, GLTR, Watermark
│   │   ├── embeddings/                 # SentenceTransformers dense provider
│   │   ├── similarity/                 # TF-IDF, Dense & Hybrid similarity services
│   │   ├── provenance/                 # Lineage DAG reconstruction engine
│   │   ├── graph/                      # NetworkX builder & PyG GraphSAGE GNN
│   │   └── risk/                       # Explainable multi-factor risk scorer
│   ├── presentation/
│   │   ├── api/v1/                     # Versioned REST endpoints
│   │   └── websocket/                  # WebSocket connection manager
│   └── main.py                         # FastAPI initialization & lifecycle
├── data/                               # Curated benchmark datasets (JSON & CSV)
├── models/                             # Trained model weights & joblib artifacts
├── alembic/                            # Database migration scripts
├── tests/                              # Comprehensive test suite (19 test cases)
├── train_models.py                     # Standalone model training CLI
├── seed_db.py                          # Database seeder
└── requirements.txt
```

## Quick Start
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train baseline models
python train_models.py

# 3. Seed database
python seed_db.py

# 4. Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger UI available at: `http://localhost:8000/docs`

## Running Tests
```powershell
python -m pytest tests -v
```
