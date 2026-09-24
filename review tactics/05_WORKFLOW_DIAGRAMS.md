# 05. System Workflow & Architecture Diagrams (Mermaid)

> **Summary:** This file contains visual Mermaid workflow diagrams for **AIShield**, specifically optimized with a **Square-Like (2x2 Balanced Grid)** layout so that it fills **Canva / PowerPoint presentation slides** with large, clear, easily readable text.

---

## 1. Square-Like Presentation Workflow (2x2 Grid — Best for Slides & Canva)

*Optimized aspect ratio (~1.25 : 1) to fill presentation slides completely without wide empty margins or tiny text.*

```mermaid
flowchart TD
    subgraph ROW_TOP[" "]
        direction LR
        BOX1["<b>1. DATA INGESTION & GATEWAY</b><br/>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/><b>Live External Data Feeds:</b><br/>• GDELT Global News Stream (100+ Languages)<br/>• Trusted News RSS Feeds (BBC News, Reuters)<br/>• Bluesky Social Stream (AT-Protocol Firehose)<br/>• Multi-Platform Simulator (Attacks & Debunks)<br/><br/><b>Ingestion Processing:</b><br/>• FastAPI Asynchronous Ingestion Router<br/>• SHA-256 Deduplication & Content Registry<br/>• Text Normalizer & Linguistic Tokenizer"]

        BOX2["<b>2. TRIPLE-LAYER AI DEFENSE ENGINE</b><br/>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/><b>Layer 1: AI Content Detection</b><br/>• TF-IDF Stylistics + ML Classifier<br/>• GLTR Linguistic Entropy & Burstiness<br/>• Statistical Watermark / Steganography Detector<br/><br/><b>Layer 2: Content Provenance Lineage</b><br/>• SentenceTransformers (all-MiniLM-L6-v2)<br/>• Parent-Child Mutation DAG (Cosine >= 0.75)<br/><br/><b>Layer 3: Network & Bot Forensics</b><br/>• Multi-Platform Social Interaction Graph<br/>• PyTorch GNN (2-Layer Graph Convolutional Net)"]

        BOX1 -->|Preprocessed Text Stream| BOX2
    end

    subgraph ROW_BTM[" "]
        direction LR
        BOX3["<b>3. RISK SYNTHESIS & DATABASE</b><br/>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/><b>Composite Threat Scoring:</b><br/>• Explainable Multi-Signal Risk Fusion<br/>• Calibrated 0% - 100% Composite Risk Metric<br/>• Explainable Reasoning & Forensic Audit Trail<br/><br/><b>High-Concurrency Storage:</b><br/>• SQLite Database configured in WAL Mode<br/>• Non-blocking Simultaneous Read & Write<br/>• Entity Schema: Posts, Accounts, Campaigns"]

        BOX4["<b>4. ANALYST OPERATIONS WORKBENCH</b><br/>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/><b>Real-Time Telemetry:</b><br/>• Persistent WebSocket Gateway (ws://)<br/>• Low-Latency Event Push (Attacks & Debunks)<br/><br/><b>Interactive React 18 UI Console:</b><br/>• Draggable React Flow Provenance DAG Canvas<br/>• Multi-Platform Diffusion Swimlanes<br/>• Live Telemetry Log & Incident Management"]

        BOX3 -->|Committed Records & Metrics| BOX4
    end

    BOX2 -->|Linguistic + DAG + GNN Signals| BOX3
    BOX1 -.->|Live Simulation Event Push| BOX4

    style ROW_TOP fill:none,stroke:none
    style ROW_BTM fill:none,stroke:none

    style BOX1 fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC
    style BOX2 fill:#0F172A,stroke:#818CF8,stroke-width:2px,color:#F8FAFC
    style BOX3 fill:#0F172A,stroke:#F59E0B,stroke-width:2px,color:#F8FAFC
    style BOX4 fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#F8FAFC
```

---

## 2. Minimalist Square 4-Quadrant Architecture (Extra Big Font)

*If you want even larger text with zero clutter on your slide:*

```mermaid
flowchart TD
    subgraph TOP_ROW[" "]
        direction LR
        Q1["<b>1. INGESTION & GATEWAY</b><br/>• GDELT News + BBC/Reuters RSS Feeds<br/>• Bluesky Firehose + WebSocket Simulator<br/>• FastAPI Router & SHA-256 Deduplication<br/>• Text Normalization & Tokenization"]
        Q2["<b>2. AI DEFENSE & FORENSICS</b><br/>• Layer 1: TF-IDF + GLTR Entropy (0-100%)<br/>• Layer 2: SentenceTransformer Provenance DAG<br/>• Layer 3: PyTorch GNN Bot Cluster Detector<br/>• Cross-Platform Campaign Aggregation"]
        Q1 ==> Q2
    end

    subgraph BTM_ROW[" "]
        direction LR
        Q3["<b>3. RISK ENGINE & DATABASE</b><br/>• Explainable Multi-Signal Risk Fusion<br/>• Calibrated 0 - 100% Threat Score<br/>• SQLite WAL Mode (Zero-Locking Storage)<br/>• High-Throughput Concurrent Persistence"]
        Q4["<b>4. ANALYST WORKBENCH</b><br/>• React 18 Operations Center Dashboard<br/>• Draggable React Flow Provenance Canvas<br/>• Multi-Platform Network Swimlanes<br/>• Real-Time WebSockets (ws://) Live Stream"]
        Q3 ==> Q4
    end

    Q2 ==> Q3
    Q1 -.->|Live Feed| Q4

    style TOP_ROW fill:none,stroke:none
    style BTM_ROW fill:none,stroke:none

    style Q1 fill:#0B132B,stroke:#00B4D8,stroke-width:3px,color:#FFFFFF
    style Q2 fill:#0B132B,stroke:#7209B7,stroke-width:3px,color:#FFFFFF
    style Q3 fill:#0B132B,stroke:#F77F00,stroke-width:3px,color:#FFFFFF
    style Q4 fill:#0B132B,stroke:#06D6A0,stroke-width:3px,color:#FFFFFF
```

---

## 3. Request Lifecycle Sequence (Step-by-Step Flow)

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
    participant UI as React Operations Console

    Analyst->>API: Submit Text or Ingest RSS/GDELT Article
    API->>DB: Check SHA-256 Hash (Deduplication)
    
    par Parallel Analysis
        API->>Detect: Evaluate Predictability (Entropy, Burstiness, TF-IDF)
        Detect-->>API: AI Probability (e.g., 91% Synthetic)
    and
        API->>Prov: Generate 384-d Embedding & Compute Cosine Similarity
        Prov-->>API: Link to Root Seed -> Construct DAG Node
    and
        API->>GNN: Extract Graph Topology & Pass Node Messages
        GNN-->>API: Bot Coordination Probability & Graph Risk
    end

    API->>API: Compute Composite Threat Score (0 - 100%)
    API->>DB: Persist Entities (Content, Detection, Posts, Events)
    API->>WS: Broadcast Event to Connected Analysts
    WS-->>UI: Live Event Push (POST / DEBUNK / VARIANT)
    API-->>Analyst: Return Forensic Dossier (HTTP 200 OK)
    UI->>UI: Update Telemetry Gauges, React Flow Canvas & Event Log
```

---

## 4. How to Explain the 2x2 Diagram on Slide 10

When you are on **Slide 10 (Workflow)** in your Canva presentation, point to the 4 quadrants and say:

> *"Our system workflow is organized into four balanced quadrants:
> 
> 1. **Top-Left (Ingestion & Gateway):** We ingest live news from GDELT, RSS feeds, and Bluesky, normalizing and deduplicating data via FastAPI.
> 2. **Top-Right (Triple-Layer AI Defense):** We analyze content across three dimensions: linguistic predictability (TF-IDF + GLTR), mutation ancestry (SentenceTransformer DAG), and bot swarm coordination (PyTorch GNN).
> 3. **Bottom-Left (Risk & Database):** We synthesize all signals into an explainable composite threat score stored in SQLite with Write-Ahead Logging for high concurrency.
> 4. **Bottom-Right (Analyst Operations Workbench):** The intelligence is pushed live over WebSockets to our React 18 dashboard, giving human analysts interactive DAG canvases and diffusion swimlanes."*
