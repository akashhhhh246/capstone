# 02. How to Demo & Present Like a Pro (Step-by-Step Click Guide)

> **Goal:** This document gives you an exact script for your presentation. When you stand in front of your professors or examiners, follow this exact sequence. You won't have to guess what to click or stumble on your words.

---

## 0. Pre-Demo Checklist (Do This 5 Minutes Before Review)

1. Open your browser and go to: **`http://localhost:9207`**
2. Press `F11` (or maximize the browser) so it fills the screen like a real military/cyber defense command center.
3. Make sure the dark dashboard has loaded with all sidebar navigation links visible:
   - **Dashboard**
   - **Live Data Ingestion**
   - **Content Analysis**
   - **Provenance Explorer**
   - **Propagation Analysis**
   - **Campaign Analysis**
   - **Real-Time Simulation**
   - **Model Governance**

---

## 1. The Opening Hook (1 Minute Intro)

**What you show on screen:** The main **Dashboard** (`/`).

**What you say:**
> *"Good morning respected evaluators. Today we are presenting **AIShield: An AI-Driven Information Operations & Disinformation Defense Workbench**. 
> 
> With modern LLMs like ChatGPT, anyone can generate thousands of convincing fake news articles in seconds and use automated bot swarms to amplify them. Our platform is built for cyber-intelligence analysts to detect AI-generated text, trace how it mutates, and pinpoint the coordinated bot rings behind it. 
> 
> Let us walk you through the system from real-world data ingestion to deep AI detection, network graph forensics, and live simulation."*

---

## 2. Step 1: Show Real-World News Ingestion (`/ingestion`)

**Where to click:** Click on **Live Data Ingestion** in the sidebar.

**What you see on screen:** 
- Three connector status cards: **GDELT Global News Connector**, **RSS Feeds (BBC/Reuters)**, and **Bluesky AT-Protocol**.
- The "Ingest Public Telemetry" button.
- A table of real, live news articles continuously ingested from the internet.

**What you say:**
> *"Before we analyze content, we need data. AIShield isn't a static dummy project — it features continuous live data connectors. 
> 
> Here on our Ingestion Deck, our background worker connects to:
> 1. **The GDELT Project** (Global Database of Events, Language, and Tone), which monitors world news in over 100 languages.
> 2. **Trusted RSS Feeds** such as BBC World News and Reuters.
> 3. **Bluesky Social** for real-time social posts.
> 
> As you can see, real news articles are continuously ingested, deduplicated using cryptographic hashes, and saved into our database."*

---

## 3. Step 2: Content Analysis & Multi-Layer AI Detection (`/detection`)

**Where to click:** Click on **Content Analysis** in the sidebar.

**What you do:**
- There is a text box. You can either type or paste sample text, or use the pre-loaded examples.
- Click **Analyze Content**.

**What you see on screen:**
- **Overall AI Probability Gauge** (e.g., 88% Synthetic vs 12% Human).
- **Linguistic Metrics Breakdown**:
  - Entropy (Word predictability).
  - Burstiness (Sentence length variation).
  - Top-K Token Rank Distribution (Green, Yellow, Red tokens).
- **Watermark & Steganography indicator**.

**What you point out and say:**
> *"Now we move to our first line of defense: AI Content Detection. 
> 
> Rather than relying on a single black-box score, AIShield uses an **Explainable Hybrid Ensemble**:
> - First, our **TF-IDF Statistical Classifier** analyzes stylistic word choices.
> - Second, we use the **GLTR (Giant Language Model Test Room)** algorithm. You can see the entropy and token distribution here. AI models produce text where almost every word is mathematically predictable (green tokens). Humans naturally write with higher burstiness and surprise words.
> - Third, we run a **Watermark Detector** to check for synthetic token biasing.
> 
> Combining these signals gives the analyst an explainable confidence score, not just a blind guess."*

---

## 4. Step 3: Provenance Explorer & Family Tree DAG (`/provenance`)

**Where to click:** Click on **Provenance Explorer** in the sidebar.

**What you do:**
- Click on any campaign or select a root seed (e.g., the *Operation GridPulse* seed or an ingested news article).
- The interactive React Flow canvas appears with nodes and arrows.
- Click on any node; drag nodes around to show interactivity.

**What you point out and say:**
> *"Once a piece of text is flagged, the analyst asks: 'Where did this story come from, and who changed it?' That is **Content Provenance**.
> 
> Here on our interactive Directed Acyclic Graph (DAG) canvas:
> - The **Root Node (red/blue)** at the top is the original post ('Patient Zero').
> - Each **Child Node** connected by an arrow represents a mutated version of that story that was shared later on social media.
> 
> We compute this using **SentenceTransformer semantic embeddings**. If a new post has a semantic cosine similarity greater than 0.75 to an existing post, our engine automatically links it in the tree and highlights the semantic mutation. An investigator can instantly see how a minor rumor was twisted into an alarming headline as it spread across platforms."*

---

## 5. Step 4: Propagation Analysis & Bot Network GNN (`/propagation`)

**Where to click:** Click on **Propagation Analysis** in the sidebar.

**What you do:**
- Select a campaign from the dropdown.
- Point to the network graph and the metrics panel (Cascade Velocity, Coordinated Bot Ratio, GNN Risk Score).

**What you point out and say:**
> *"Detecting text is only half the battle. Malicious actors use bot swarms to amplify false claims.
> 
> Here in Propagation Analysis, we look at the social graph:
> - The circular nodes represent user accounts, and the connecting lines represent retweets, mentions, and quotes.
> - We trained a **Graph Convolutional Network (GNN)** using PyTorch. 
> - Unlike traditional models that only look at a single user profile, our GNN analyzes **topological neighborhood patterns**. It identifies bot clusters that exhibit synchronized posting, unnatural amplification velocity, and synthetic follower-following ratios.
> - The system flags the coordinated accounts in red with their bot probability."*

---

## 6. Step 5: Campaign Analysis (`/campaigns`)

**Where to click:** Click on **Campaign Analysis** in the sidebar.

**What you point out and say:**
> *"In the real world, bad actors don't just launch one post; they orchestrate full-scale **Information Operations**.
> 
> On this page, our clustering algorithms automatically aggregate hundreds of individual posts and cross-platform signals into named campaigns.
> - For example, **Operation GridPulse** is tracked here with its composite threat score (88%), number of active synthetic accounts, target narrative, and geographical impact.
> - We also track high-integrity, verified campaigns like **NASA JWST Cosmic Outreach** (8% threat) to benchmark normal public discourse against malicious attacks."*

---

## 7. Step 6: Real-Time Simulation Deck (`/simulation`)

**Where to click:** Click on **Real-Time Simulation** in the sidebar.

**This is the most impressive, dynamic part of your demo!**

**What you do:**
1. Show the **Scenario Category Quick-Filter Chips**:
   - `All Scenarios`
   - `🚨 Disinfo Threats`
   - `🛡️ Verified Science / Good News`
2. First, click **`🛡️ Verified Science / Good News`**.
   - Notice the dropdown switches to **NASA JWST Cosmic Outreach**.
   - Click the green **`Start Simulation`** button.
   - Watch the live telemetry stream:
     - Events come in with emerald green badges: `POST`, `RESHARE`, `QUOTE`.
     - The **Real-Time Threat Score** card turns **Emerald Green (8% - 15%)** labeled *"Verified / Low Threat"*.
   - Click **`Stop Simulation`** to show full control.
3. Next, click **`🚨 Disinfo Threats`**.
   - The dropdown switches to **Operation GridPulse**.
   - Click **`Start Simulation`**.
   - Watch the live events:
     - You see adversarial bot leaks with red badges (85% - 95% risk).
     - **Crucial highlight:** Point out the emerald green **`FACT_CHECK_DEBUNK`** events (`@official_factcheck_desk`, `@reuters_verify`) and cyan **`OFFICIAL_NOTICE`** events streaming in at 5% - 15% risk.
   - Click **`Stop Simulation`**.

**What you say:**
> *"Finally, we built a **Real-Time WebSocket Simulation Deck**. This allows defense analysts and decision-makers to stress-test their response protocols against live social media dynamics.
> 
> Notice two key capabilities:
> 1. When we simulate a verified campaign like **NASA JWST Outreach**, the system streams legitimate public communication with green, low-risk scores (under 20%).
> 2. When we simulate an adversarial campaign like **Operation GridPulse**, the platform doesn't just show bot attacks; it realistically models **ecosystem defense**. You can see independent fact-checkers (`FACT_CHECK_DEBUNK`) and regulatory advisories (`OFFICIAL_NOTICE`) dynamically intervening in real time to neutralize the disinformation.
> 
> All of this streams over asynchronous WebSockets at customizable event rates."*

---

## 8. Step 7: Model Governance & Enterprise Health (`/governance`)

**Where to click:** Click on **Model Governance** in the sidebar.

**What you point out and say:**
> *"To ensure our platform is enterprise-ready, we implemented a dedicated **Model Governance & MLOps Deck**:
> - We maintain an audit trail for all models in production: our TF-IDF Classifier, our SentenceTransformer embedder, and our PyTorch GNN.
> - We monitor versioning, inference latency, drift metrics, and ethical compliance to prevent algorithmic bias.
> - Our system is hardened with SQLite Write-Ahead Logging (WAL) for high concurrency, OWASP security headers, and automated health telemetry."*

---

## 9. The Closing Statement (30 Seconds)

**What you say:**
> *"In conclusion, AIShield provides a comprehensive, multi-layer defense against AI-generated disinformation. By uniting **Content Detection**, **Provenance Lineage**, **Graph Social Forensics**, and **Real-Time Simulation** into a single cohesive workbench, we transform what used to take days of manual investigation into seconds of automated intelligence. 
> 
> Thank you, and we are now eager to answer any questions!"*
