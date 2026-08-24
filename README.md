# Mitigating National Security Risks Posed by Large Language Models (LLMs) in AI-Driven Malign Information Operations

An enterprise-grade, defensive cybersecurity and information integrity research prototype designed to detect AI-generated disinformation, trace content provenance across multi-platform simulated networks, evaluate cascade diffusion using Graph Neural Networks (GNNs) and NetworkX, calculate explainable risk scores, and stream real-time synthetic simulation events to an interactive analyst workbench.

---

## 1. Project Overview

Advanced Large Language Models (LLMs) enable the automated generation of realistic, persuasive, and stylistically varied fake content at unprecedented scale. When leveraged in coordinated information operations, these models facilitate hyper-targeted disinformation campaigns, panic-inducing narratives, and cross-platform narrative mutation that evade traditional signature-based detection.

This research prototype provides an integrated, modular defensive platform capable of:
- Analyzing ingested text for statistical AI generation signatures and token probability anomalies.
- Reconstructing Directed Acyclic Graph (DAG) provenance chains showing where content originated, how it mutated, and who amplified it.
- Analyzing multi-platform propagation graphs with structural metrics and Graph Neural Networks (PyG GraphSAGE).
- Generating human-interpretable, multi-factor explainable threat risk scores.
- Simulating dynamic social media cascades in real-time over WebSockets.

---

## 2. Problem Statement

Modern AI-driven influence campaigns operate across multiple communication channels (microblogs, encrypted messaging channels, community forums, and news syndicates) using paraphrasing and LLM-assisted mutations to evade lexical duplicate detection. Security analysts lack unified tools to:
1. Distinguish between human writing and LLM outputs with transparent confidence and token-level likelihood distributions.
2. Track how an initial seed narrative evolves into paraphrased derivatives across multiple platforms over time.
3. Quantify the velocity, reach, and coordinated inauthentic behavior (CIB) patterns of multi-hop cascades.
4. Obtain transparent, explainable reasons for risk scores rather than uninterpretable black-box numbers.

---

## 3. Objectives

1. **AI Content Detection**: Implement real baseline classifiers (TF-IDF + Logistic Regression), GLTR-style statistical token probability visualizers, and pluggable watermark detectors.
2. **Provenance Reconstruction**: Build an automated DAG provenance engine using dense semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and TF-IDF cosine similarity.
3. **Graph & GNN Analysis**: Construct multi-relational NetworkX graphs and execute PyTorch Geometric GraphSAGE GNN inference for cascade risk scoring.
4. **Explainable Risk Attribution**: Synthesize linguistic, kinematic, topological, and GNN signals into an itemized, factor-by-factor risk breakdown.
5. **Real-Time Simulation**: Deliver an asynchronous social media cascade simulator broadcasting live events (`POST`, `RESHARE`, `REPLY`, `QUOTE`, `CROSS_PLATFORM_SHARE`, `CONTENT_VARIANT`) over WebSockets.
6. **Analyst Dashboard**: Provide 7 fully realized analyst pages using React, TypeScript, Material UI, React Flow, and Recharts.
7. **Privacy & Civil Liberties**: Adhere strictly to synthetic and public benchmark data, preserving individual privacy and civil liberties.

---

## 4. System Architecture

```mermaid
flowchart TD
    subgraph Frontend["Frontend Analyst Workbench (React + TypeScript + MUI + React Flow)"]
        UI_Dash["Dashboard (/)]"]
        UI_Detect["Content Analysis (/analysis)"]
        UI_Prov["Provenance Explorer (/provenance)"]
        UI_Prop["Propagation Analysis (/propagation)"]
        UI_Camp["Campaign Intelligence (/campaigns)"]
        UI_Sim["Live Simulation (/simulation)"]
        UI_Gov["Model Governance (/models)"]
    end

    subgraph Backend["Modular Monolith Backend (FastAPI + Python 3.12+)"]
        API["REST API (/api/v1) & WebSocket Gateway"]

        subgraph Application["Application Layer"]
            DetSvc["DetectionService"]
            ProvSvc["ProvenanceService"]
            PropSvc["PropagationService"]
            CampSvc["CampaignService"]
            SimEng["SimulationEngine (Async)"]
        end

        subgraph ML["Machine Learning Layer"]
            TFIDF["TF-IDF + Logistic Regression"]
            GLTR["GLTR Statistical Token Analyzer"]
            WM["Kirchenbauer Watermark Verifier"]
            STEmbed["SentenceTransformers (all-MiniLM-L6-v2)"]
            NetX["NetworkX Graph Metric Engine"]
            PyGGNN["PyG GraphSAGE GNN Model"]
            RiskScorer["Explainable Risk Scoring Engine"]
        end

        subgraph Storage["Persistence Layer"]
            ORM["SQLAlchemy ORM + Alembic Migrations"]
            DB[(PostgreSQL / SQLite)]
        end
    end

    UI_Detect -->|Submit Text| API
    API --> DetSvc
    DetSvc --> TFIDF & GLTR & WM
    DetSvc --> ORM
    ORM --> ProvSvc
    ProvSvc --> STEmbed
    ProvSvc --> PropSvc
    PropSvc --> NetX & PyGGNN
    PropSvc --> RiskScorer
    RiskScorer --> DB
    SimEng -->|Stream Events| API
    API -->|WebSocket| UI_Sim & UI_Dash
```

---

## 5. Technology Stack

### Backend
- **Language & Runtime**: Python 3.12+
- **API Framework**: FastAPI, Uvicorn, WebSockets
- **Data Validation & Settings**: Pydantic v2, Pydantic-Settings
- **Database & ORM**: SQLAlchemy 2.0, Alembic, PostgreSQL (with SQLite zero-friction local fallback)
- **Machine Learning & NLP**:
  - `scikit-learn`: TF-IDF Vectorizer, Logistic Regression, pairwise metrics
  - `sentence-transformers`: Pretrained dense semantic embeddings (`all-MiniLM-L6-v2`)
  - `networkx`: Multi-platform graph construction and structural centrality metrics
  - `torch` & `torch-geometric`: PyTorch Geometric 2-layer GraphSAGE GNN
  - `numpy`, `pandas`: Statistical analysis and feature processing
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`

### Frontend
- **Framework & Tooling**: React 18, TypeScript, Vite
- **UI & Component Library**: Material UI (MUI v5), Emotion
- **Graph & Network Visualizations**: `@xyflow/react` (React Flow)
- **Charts & Telemetry**: Recharts
- **Icons**: Lucide React, MUI Icons
- **HTTP & Networking**: Axios, native WebSocket client manager with auto-reconnect

---

## 6. Folder Structure

```
.
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   │   └── entities/models.py          # SQLAlchemy domain models & value enums
│   │   ├── application/
│   │   │   ├── dto/schemas.py              # Pydantic request/response schemas
│   │   │   └── services/                   # Application services
│   │   │       ├── detection_service.py
│   │   │       ├── provenance_service.py
│   │   │       ├── propagation_service.py
│   │   │       ├── campaign_service.py
│   │   │       └── simulation_service.py
│   │   ├── infrastructure/
│   │   │   ├── configuration/config.py     # Configuration management (.env)
│   │   │   └── database/session.py         # SQLAlchemy engine & session factory
│   │   ├── ml/
│   │   │   ├── detection/                  # TF-IDF, GLTR, Watermark, Preprocessing
│   │   │   ├── embeddings/                 # SentenceTransformers dense provider
│   │   │   ├── similarity/                 # TF-IDF, Dense & Hybrid similarity
│   │   │   ├── provenance/                 # Lineage DAG builder
│   │   │   ├── graph/                      # NetworkX builder & PyG GraphSAGE GNN
│   │   │   └── risk/                       # Multi-factor explainable risk scorer
│   │   ├── presentation/
│   │   │   ├── api/v1/                     # REST API route controllers
│   │   │   └── websocket/simulation_ws.py  # WebSocket gateway
│   │   └── main.py                         # FastAPI initialization & SPA hosting
│   ├── data/
│   │   ├── sample_dataset.json             # Benchmark samples (Human, LLM, Disinfo)
│   │   └── sample_dataset.csv
│   ├── models/                             # Serialized joblib and PyTorch weights
│   ├── alembic/                            # Alembic migration scripts
│   ├── tests/                              # Pytest test suite (19 tests)
│   ├── train_models.py                     # Standalone model training CLI
│   ├── seed_db.py                          # Database seeder
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/                     # MetricCard, GLTRViewer, Graphs, Badges
│   │   ├── layouts/MainLayout.tsx          # Top navigation and sidebar shell
│   │   ├── pages/                          # 7 Dedicated Analyst Pages
│   │   ├── services/                       # Axios api.ts and websocket.ts
│   │   ├── theme/theme.ts                  # Cyber-defense dark theme
│   │   ├── types/index.ts                  # TypeScript definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── README.md
└── .gitignore
```

---

## 7. Part 1 Methodology — AI Content Detection

Part 1 implements a multi-model evaluation pipeline:
1. **Preprocessing & Stylometry**: Normalizes text, computes word/character counts, Shannon character entropy, sentence length variance (**burstiness**), lexical diversity (Type-Token Ratio / TTR), stopword ratios, and punctuation distributions.
2. **TF-IDF + Logistic Regression Classifier**: Trained on authentic human articles (journalism, science, academic abstracts) and LLM-generated texts (GPT-3.5, GPT-4, Llama). Employs sublinear TF-IDF word & character n-grams $(1, 2)$ with L2 regularization to output calibrated probabilities $(p_{\text{human}}, p_{\text{ai}})$.
3. **GLTR Statistical Token Distribution**: Partitions vocabulary into 4 probability tiers:
   - **Green (Top 10)**: Extremely predictable / greedy LLM sampling tokens.
   - **Yellow (Top 100)**: Medium-high likelihood tokens.
   - **Red (Top 1000)**: Lower likelihood tokens.
   - **Purple (Tail > 1000)**: Unpredictable tokens, human stylistic nuances, or domain jargon.
   Also computes empirical perplexity and mean cross-entropy.
4. **Watermark Detection**: Statistical green-list token hypothesis test (Kirchenbauer et al. method) computing one-tailed $z$-scores to test for keyed pseudo-random token partition watermarks. Returns explicit status (`DETECTED`, `NOT_DETECTED`, `NOT_SUPPORTED`, `UNAVAILABLE`).
5. **Unified Detection Service**: Combines individual model verdicts and stylometric indicators into a unified response with an explicit human-in-the-loop advisory.

---

## 8. Part 2 Methodology — Content Provenance

Part 2 models how content mutates and propagates across platforms:
1. **Entities**: Tracks `Content`, `Post`, `SyntheticAccount`, `Platform`, `Campaign`, and `PropagationEvent`.
2. **Hybrid Similarity Matching**:
   - **Lexical TF-IDF Cosine Similarity**: Captures near-verbatim reposts and direct quotes.
   - **Dense Embedding Cosine Similarity**: Employs `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense projections) to detect semantic paraphrases and modified narrative mutations.
   - **Hybrid Weighted Similarity**: $S_{\text{hybrid}} = 0.4 \cdot S_{\text{tfidf}} + 0.6 \cdot S_{\text{embedding}}$.
3. **Lineage Relationship Classification**:
   - $\ge 0.98$: `EXACT_COPY` / `CROSS_PLATFORM_COPY`
   - $0.85 \le S < 0.98$: `NEAR_DUPLICATE`
   - $0.65 \le S < 0.85$: `PARAPHRASED_DERIVATIVE`
   - $0.50 \le S < 0.65$: `RELATED_NARRATIVE`
4. **Provenance DAG Construction**: Reconstructs chronological Directed Acyclic Graphs tracing root origins through initial publication, cross-platform reposts, and derivative variants.

---

## 9. Machine Learning Pipeline

```
Raw Analyst Text / Social Post
          │
          ▼
Text Cleaning & Stylometry Extraction
(Entropy, Burstiness, TTR, Char Count)
          │
          ├───► TF-IDF + Logistic Regression ──► Predicted Class & Calibrated Proba
          │
          ├───► GLTR Statistical Ranking ──────► Token Buckets (Green/Yellow/Red/Purple) & Perplexity
          │
          ├───► Watermark Detector ────────────► Green-List Z-Score & Status
          │
          ▼
Combined Detection Result & Content Registry
          │
          ▼
Dense Semantic Embedding (SentenceTransformers 384-dim)
          │
          ▼
Provenance DAG & Propagation Graph (NetworkX + PyG GNN)
          │
          ▼
Multi-Factor Explainable Risk Scoring Engine
```

---

## 10. Provenance Pipeline

1. **Ingestion**: When text is submitted, a SHA-256 hash is computed. If new, it is registered in `contents`.
2. **Historical Comparison**: The text is embedded and compared against all registered repository items.
3. **Threshold Categorization**: Matches exceeding $0.50$ similarity are linked as potential ancestors or derivatives.
4. **Chronological DAG Construction**: Nodes are ordered by publication timestamps to prevent cyclic references.
5. **Graph Visualization**: Exported to React Flow JSON nodes and edges for visual exploration.

---

## 11. GNN Methodology

- **Framework**: PyTorch Geometric (PyG)
- **Architecture**: 2-Layer `GraphSAGE` with Mean-Pooling Neighborhood Aggregation:
  $$h_v^{(k)} = \sigma \left( W_{\text{self}} h_v^{(k-1)} + W_{\text{neigh}} \cdot \text{MEAN}_{u \in \mathcal{N}(v)} h_u^{(k-1)} \right)$$
- **Node Features (16 Dimensions)**: Bot probability, in-degree, out-degree, coordination flag, platform one-hot encoding, and velocity.
- **Dual Heads**:
  1. **Node Classifier**: Binary prediction of coordinated bot accounts vs benign nodes.
  2. **Global Mean-Pooling Risk Head**: Graph-level sigmoid risk score $(0.0 - 1.0)$.
- **Status Transparency**: Clearly flags model status (`TRAINED`, `PRETRAINED`, `DEMONSTRATION`, `HEURISTIC_FALLBACK`).

---

## 12. Real-Time Simulation Architecture

The simulation engine provides realistic testing without generating real-world harm:
- **Asynchronous Loop**: Runs background tasks in FastAPI.
- **Event Types**: `POST`, `RESHARE`, `REPLY`, `QUOTE`, `CROSS_PLATFORM_SHARE`, `CONTENT_VARIANT`.
- **WebSocket Hub**: `ConnectionManager` broadcasts events to frontend clients in real time.
- **Dynamic Updates**: Frontend feeds update live without full-page reloads.

---

## 13. Database Schema

```mermaid
erDiagram
    contents ||--o{ detection_results : "has"
    contents ||--o{ posts : "published in"
    platforms ||--o{ synthetic_accounts : "hosts"
    platforms ||--o{ posts : "hosts"
    synthetic_accounts ||--o{ posts : "creates"
    campaigns ||--o{ posts : "contains"
    campaigns ||--o{ simulation_runs : "generates"
    posts ||--o{ posts : "parent-child"
    simulation_runs ||--o{ propagation_events : "emits"

    contents {
        string id PK
        string text_hash
        text raw_text
        text clean_text
        string domain
        int word_count
        datetime created_at
    }

    detection_results {
        string id PK
        string content_id FK
        string classification
        float confidence
        float ai_probability
        json gltr_stats
        string watermark_status
        json statistical_features
        json indicators
    }

    platforms {
        string id PK
        string name
        string platform_type
        float risk_weight
    }

    synthetic_accounts {
        string id PK
        string platform_id FK
        string pseudonym_handle
        float bot_probability
        boolean is_coordinated_actor
    }

    campaigns {
        string id PK
        string name
        string objective
        text target_narrative
        string status
        float risk_score
        float gnn_risk_score
        json explainability_reasons
        int total_events
        int total_reach
    }

    posts {
        string id PK
        string platform_id FK
        string account_id FK
        string content_id FK
        string parent_post_id FK
        string campaign_id FK
        string post_type
        int likes
        int reshares
    }

    simulation_runs {
        string id PK
        string campaign_id FK
        string status
        float event_rate_per_sec
        int total_events_emitted
        datetime started_at
    }

    propagation_events {
        string id PK
        string simulation_id FK
        string campaign_id FK
        string event_type
        string source_post_id
        string target_post_id
        string account_id
        string platform_id
        datetime timestamp
    }
```

---

## 14. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/detection/analyze` | Execute Part 1 multi-model AI detection pipeline |
| `POST` | `/api/v1/content` | Register new text in content repository |
| `GET` | `/api/v1/content/{id}` | Retrieve content details and latest detection |
| `GET` | `/api/v1/content` | List registered content items |
| `GET` | `/api/v1/provenance/{contentId}` | Reconstruct Provenance Lineage DAG |
| `GET` | `/api/v1/propagation/{contentId}` | Calculate NetworkX velocity & GNN risk |
| `GET` | `/api/v1/campaigns` | List all tracked campaigns with risk scores |
| `GET` | `/api/v1/campaigns/{id}` | Retrieve campaign telemetry & explainable reasons |
| `POST` | `/api/v1/simulation/start` | Start real-time propagation simulation |
| `POST` | `/api/v1/simulation/{id}/pause` | Pause active simulation |
| `POST` | `/api/v1/simulation/{id}/stop` | Stop active simulation |
| `GET` | `/api/v1/simulation/{id}` | Get simulation status and emitted counts |
| `GET` | `/api/v1/models` | List ML model cards, metrics, and limitations |
| `GET` | `/api/v1/dashboard/stats` | Retrieve aggregate KPIs, charts, and alerts |
| `WS` | `/api/v1/ws/simulation/{id}` | WebSocket stream for simulation events |
| `WS` | `/api/v1/ws/live` | Global WebSocket live alert and event stream |

Interactive Swagger documentation available at: `http://localhost:9207/docs`

---

## 15. Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- Git

---

## 16. Environment Variables

Create `backend/.env` (or copy `backend/.env.example`):

```env
DATABASE_URL=sqlite:///./provenance_defense.db
# PostgreSQL example: postgresql://postgres:postgres@localhost:5432/provenance_defense_db

API_BASE_URL=http://localhost:9207
HOST=0.0.0.0
PORT=9207
LOG_LEVEL=INFO
DEBUG=True

MODEL_DIR=./models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TFIDF_MODEL_PATH=./models/tfidf_classifier.joblib
GNN_MODEL_PATH=./models/gnn_propagation_model.pt

CORS_ORIGINS=http://localhost:9207,http://127.0.0.1:9207,http://localhost:5173
```

---

## 17. Database Setup

```powershell
cd backend
alembic upgrade head
python seed_db.py
```

---

## 18. Running the Backend & Unified Application

The application can be started directly as a unified full-stack server on port **9207**:

```powershell
cd backend
python train_models.py
python seed_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 9207
```

Access the application in your browser at:
`http://localhost:9207`

---

## 19. Running Frontend in Development Mode

If you wish to run the Vite dev server separately:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

---

## 20. Running Tests

Run the full automated pytest suite (19 test cases covering preprocessing, classifiers, GLTR, watermarks, similarity, provenance, graph features, GNN, risk scoring, REST APIs, and end-to-end integration):

```powershell
python -m pytest backend/tests -v
```

---

## 21. Sample Dataset

The included benchmark dataset (`backend/data/sample_dataset.json` and `sample_dataset.csv`) contains:
- **Human Writing**: Peer-reviewed scientific summaries (ESA/Astrophysics), municipal civic reports, academic ML abstracts, culinary articles, and financial earnings reports.
- **LLM Generated**: Boilerplate prose, synthetic technical summaries, and characteristic transition patterns.
- **Synthetic Disinformation Narratives**: Synthetic emergency infrastructure alerts, unverified public health contamination rumors, and artificial banking collapse panics.

---

## 22. Limitations

1. **Stylistic Evasion**: Highly creative human authors or non-native English speakers can produce statistical false positives in n-gram and token-rank distributions.
2. **Short Text Sensitivity**: Snippets under 25 words lack sufficient token volume for statistically significant perplexity or watermark hypothesis testing.
3. **Paraphrase Perturbations**: Heavy adversarial paraphrasing can degrade lexical matching; dense embeddings mitigate this but require threshold tuning.
4. **Watermarking Key Dependence**: Watermark verification assumes key agreement; non-watermarked proprietary LLMs cannot be watermarked retroactively.

---

## 23. Privacy and Civil Liberties Considerations

- **Strict Non-Surveillance**: The platform is explicitly prohibited from scraping private user accounts, monitoring personal communications, or deanonymizing individuals.
- **100% Synthetic Entities**: All accounts, platforms, and campaigns in the demonstration use pseudonymized IDs (`@synth_relay_alpha`, `SimuTwitter`, `SimuTelegram`).
- **Decision Support, Not Automated Censorship**: AI detector scores are probabilistic estimates. All alerts and risk scores require human analyst validation.

---

## 24. Future Improvements

1. **Transformer Discriminators**: Integration of fine-tuned DeBERTa-v3/RoBERTa classifiers alongside the TF-IDF baseline.
2. **Dynamic Graph Attention (GAT)**: Upgrading GraphSAGE layers to GATv2 for edge-weighted attention on multi-platform reposts.
3. **Multimodal Ingestion**: Extending provenance tracking to synthetic images (diffusion model fingerprints) and synthetic audio.
4. **Cross-Lingual Provenance**: Leveraging multilingual dense embeddings (`paraphrase-multilingual-mpnet-base-v2`) for global narrative tracking.
