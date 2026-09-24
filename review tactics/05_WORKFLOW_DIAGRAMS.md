# 05. System Workflow & Architecture Diagrams (Mermaid)

> **Summary:** This document provides clear, visual Mermaid workflow diagrams for **AIShield**. You can render these in any Markdown viewer (GitHub, VS Code, Obsidian) or copy the Mermaid code directly into presentations.

---

## 1. Complete End-to-End System Workflow

This diagram illustrates how raw information flows from external sources through our multi-layer detection and forensic engines to the analyst dashboard.

```mermaid
flowchart TD
    %% ================= DATA INGESTION =================
    subgraph S1["1. Data Ingestion & Signal Capture"]
        direction TB
        IN_GDELT["GDELT Global News Feed<br/>(100+ Languages)"]
        IN_RSS["Trusted RSS News Feeds<br/>(BBC News, Reuters)"]
        IN_BSKY["Bluesky Social Stream<br/>(AT-Protocol Firehose)"]
        IN_SIM["Real-Time Simulation Engine<br/>(Adversarial Attacks + Debunks)"]
    end

    %% ================= NORMALIZATION =================
    subgraph S2["2. Ingestion Gateway & Preprocessing"]
        direction TB
        GATEWAY["FastAPI Ingestion Service"]
        DEDUP["SHA-256 Deduplication & Content Registry"]
        CLEAN["Text Normalization & Tokenizer<br/>(Sentence Splitting, Punctuation)"]
    end

    IN_GDELT --> GATEWAY
    IN_RSS --> GATEWAY
    IN_BSKY --> GATEWAY
    IN_SIM --> GATEWAY

    GATEWAY --> DEDUP
    DEDUP --> CLEAN

    %% ================= CORE DEFENSE PIPELINE =================
    subgraph S3["3. Multi-Layer Intelligence & Defense Pipeline"]
        direction TB

        %% LAYER 1
        subgraph L1["Layer 1: AI Content Detection (Linguistic Forensic)"]
            TFIDF["TF-IDF + ML Classifier<br/>(N-gram Stylistic Probability)"]
            GLTR["GLTR Test Room<br/>(Entropy & Burstiness Predictability)"]
            WM["Watermark Detector<br/>(Statistical Green/Red Token Biasing)"]
            L1_OUT["Ensemble AI Probability Score<br/>(0% Human - 100% Synthetic)"]
            TFIDF --> L1_OUT
            GLTR --> L1_OUT
            WM --> L1_OUT
        end

        %% LAYER 2
        subgraph L2["Layer 2: Provenance Engine (Mutation Lineage)"]
            EMBED["SentenceTransformer MiniLM-L6-v2<br/>(384-Dimensional Semantic Vectors)"]
            COS["Cosine Similarity Engine<br/>(Threshold >= 0.75)"]
            DAG["Directed Acyclic Graph Builder<br/>(Parent-Child Lineage & Word Diffs)"]
            EMBED --> COS --> DAG
        end

        %% LAYER 3
        subgraph L3["Layer 3: Network Forensics (Bot Swarms)"]
            GRAPH["Multi-Platform Social Graph<br/>(Nodes: Users, Posts | Edges: Shares)"]
            TOPOL["Topological Centrality Extraction<br/>(PageRank, Betweenness, Velocity)"]
            GNN["PyTorch Graph Neural Network<br/>(2-Layer Graph Convolutional Network)"]
            GRAPH --> TOPOL --> GNN
        end

        %% LAYER 4
        subgraph L4["Layer 4: Campaign Clustering"]
            CLUSTER["HDBSCAN & Agglomerative Clustering<br/>(Cross-Platform Campaign Aggregation)"]
        end
    end

    CLEAN --> TFIDF
    CLEAN --> GLTR
    CLEAN --> WM
    CLEAN --> EMBED
    CLEAN --> GRAPH
    DAG --> CLUSTER
    GNN --> CLUSTER

    %% ================= RISK ENGINE & DATABASE =================
    subgraph S4["4. Risk Synthesis & Storage"]
        RISK["Composite Explainable Risk Engine<br/>(Linguistic + Provenance + Network + Campaign)"]
        DB[("SQLite WAL Database<br/>(Write-Ahead Logging / High Concurrency)")]
    end

    L1_OUT --> RISK
    DAG --> RISK
    GNN --> RISK
    CLUSTER --> RISK
    RISK --> DB

    %% ================= PRESENTATION & TELEMETRY =================
    subgraph S5["5. Analyst Workbench & Real-Time Telemetry"]
        WS["WebSocket Telemetry Gateway<br/>(ws:// - Low-Latency Event Push)"]
        UI["React 18 + TypeScript Dashboard<br/>(Material-UI Cyber Defense Operations Console)"]
        V1["Content Analysis Gauges"]
        V2["Interactive Provenance DAG Canvas<br/>(React Flow Draggable Tree)"]
        V3["Spacious Propagation Swimlanes<br/>(Platform Columns & Bot Nodes)"]
        V4["Live Telemetry Event Log<br/>(Attacks, Fact-Checks & Official Notices)"]
    end

    RISK --> WS
    DB --> UI
    WS --> UI
    UI --> V1
    UI --> V2
    UI --> V3
    UI --> V4
```

---

## 2. Request Lifecycle Sequence (Step-by-Step Flow)

This sequence diagram illustrates exactly what happens when an analyst submits a post or when an article is ingested from the live web.

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Intelligence Analyst / Live Feed
    participant API as FastAPI Backend (/api/v1)
    participant Detect as Detection Engine (TF-IDF + GLTR)
    participant Prov as Provenance Engine (SentenceTransformers)
    participant GNN as Propagation Engine (PyG GCN)
    participant DB as SQLite WAL Database
    participant WS as WebSocket Broadcaster
    participant UI as React Frontend Console

    Analyst->>API: Submit Text or Ingest RSS/GDELT Article
    API->>DB: Check SHA-256 Hash (Deduplication)
    
    par Parallel Analysis
        API->>Detect: Evaluate Linguistic Predictability (Entropy, Burstiness, TF-IDF)
        Detect-->>API: AI Probability (e.g., 91% Synthetic)
    and
        API->>Prov: Compute 384-d Embedding & Query Cosine Similarities
        Prov-->>API: Match to Root Seed -> Build DAG Node
    and
        API->>GNN: Extract Subgraph Features & Pass Message Neighbors
        GNN-->>API: Bot Coordination Probability & Graph Risk
    end

    API->>API: Calculate Composite Risk Score (Weighted Fusion)
    API->>DB: Commit Entities (Content, Detection, Posts, Events)
    API->>WS: Broadcast Event to Active Analysts
    WS-->>UI: Live Event Push (Type: POST / DEBUNK / VARIANT)
    API-->>Analyst: Return JSON Forensics Dossier (HTTP 200 OK)
    UI->>UI: Update Telemetry Gauges, React Flow Canvas & Event Stream
```

---

## 3. Propagation & Defense Dynamics (Simulation Workflow)

This diagram shows how our simulator generates a realistic mixed ecosystem containing both adversarial attacks and defensive counter-measures.

```mermaid
stateDiagram-v2
    [*] --> Idle: Simulator Standby

    state "Scenario Selection" as Select {
        DisinfoThreat: "🚨 Disinfo Threat (Operation GridPulse)"
        VerifiedScience: "🛡️ Verified Science (NASA JWST Outreach)"
    }

    Idle --> Select: Analyst Chooses Scenario

    state "Live Simulation Stream (WebSockets)" as SimStream {
        state DisinfoThreat {
            direction TB
            BotLeak: "60% Adversarial Bot Propagation (Risk: 74% - 98%)"
            FactCheck: "25% Fact-Check Debunks (Risk: 5% - 16%, Emerald Green)"
            OfficialNotice: "15% Institutional Notices (Risk: 10% - 25%, Cyan)"
        }

        state VerifiedScience {
            direction TB
            SciencePost: "85% Verified Scientific Outreach (Risk: 4% - 22%)"
            PublicDiscussion: "15% Organic Citizen Inquiries (Risk: 8% - 28%)"
        }
    }

    Select --> SimStream: Start Simulation

    state "Workbench Metrics Update" as Metrics {
        ExposureGauge: Update Dynamic Reach
        ThreatScore: Update Composite Score (Green <=35%, Amber <=70%, Red >70%)
        EventStream: Render Live Telemetry Chips
    }

    SimStream --> Metrics: Stream Telemetry Events
    Metrics --> Idle: Stop Simulation
```

---

## 4. How to Explain This Diagram in Your Viva

When the evaluators ask: *"Walk me through the architecture / workflow of your project"*, point to Section 1 and say:

> *"Our workflow operates in 5 clean stages:
> 
> 1. **Ingestion:** We pull live, uncurated data continuously from GDELT, RSS feeds, and social platforms, deduplicating via cryptographic hashes.
> 2. **Content Analysis:** Text is normalized and evaluated by our hybrid ensemble (TF-IDF for stylistics, GLTR for entropy/burstiness, and watermark detection).
> 3. **Provenance & Graph Forensics:** Simultaneously, our SentenceTransformer maps semantic mutations into a Directed Acyclic Graph (DAG) to find the origin, while our PyTorch Graph Neural Network analyzes the social network to catch bot clusters.
> 4. **Risk Synthesis:** All four signals are combined into an explainable composite threat score stored in high-concurrency SQLite WAL mode.
> 5. **Analyst Presentation:** Results are broadcast instantly via WebSockets to our React operations dashboard with interactive visual canvases."*
