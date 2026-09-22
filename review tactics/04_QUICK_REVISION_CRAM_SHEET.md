# 04. Quick Revision Cram Sheet (Read 5 Mins Before Review)

> **Keep this open on your phone or printed out while waiting outside the review hall.**

---

## 1. The 10-Second Elevator Definition
**AIShield** is an AI-powered defense workbench that detects AI-generated fake news, maps how it mutates across social media into a family tree (Provenance DAG), detects coordinated bot swarms using Graph Neural Networks, and provides a real-time WebSocket attack/defense flight simulator.

---

## 2. Acronym Decoder Ring (Never Get Stumped by an Abbreviation!)

| Acronym | Stands For | What It Actually Means |
| :--- | :--- | :--- |
| **DAG** | Directed Acyclic Graph | A family tree with arrows going forward in time; no circular loops. |
| **GNN** | Graph Neural Network | An AI model that looks at who is connected to whom in a social network. |
| **GCN** | Graph Convolutional Network | The specific type of GNN layer we use in PyTorch to pass messages between neighbor nodes. |
| **GLTR** | Giant Language Model Test Room | A technique (Harvard/MIT-IBM) testing whether words are predictable (green = AI, red = human). |
| **TF-IDF** | Term Frequency - Inverse Document Frequency | A classic statistical formula scoring how unique and distinctive words are in a document. |
| **GDELT** | Global Database of Events, Language, and Tone | A massive global database monitoring real news worldwide in 100+ languages. |
| **RSS** | Really Simple Syndication | Standard web feed protocol used by news outlets like BBC and Reuters. |
| **WAL** | Write-Ahead Logging | A database setting in SQLite that prevents "database is locked" errors during simultaneous read/write. |
| **WS** | WebSocket | A live, two-way connection between server and browser for zero-delay event streaming. |

---

## 3. Numbers & Parameters to Know by Heart

- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (Produces **384-dimensional** semantic vectors).
- **Provenance Link Threshold:** **0.75 (75%) Cosine Similarity** (If two posts are $\ge 75\%$ similar, they are linked in the DAG).
- **Overall Model Accuracy:** **$\sim 92\%$ cross-validated accuracy** on benchmark synthetic detection datasets.
- **Port Number:** Running locally on port **`9207`** (`http://localhost:9207`).
- **Simulated Event Split in Threat Campaigns:**
  - $60\%$ Adversarial Bot Leaks ($74\% - 98\%$ risk)
  - $25\%$ Fact-Check Debunks ($5\% - 16\%$ risk, emerald green)
  - $15\%$ Official Regulatory Notices ($10\% - 25\%$ risk, cyan)

---

## 4. The 5 Golden Rules for Acing Your Review

1. **Rule 1: Always speak in terms of "Layers of Defense".**
   - If asked how you solve a problem, say: *"We don't rely on one method; we use a multi-layer defense: linguistic text detection, provenance lineage, and network topology."*
2. **Rule 2: Never claim 100% accuracy.**
   - If asked about accuracy: *"We achieve ~92% accuracy, and we intentionally designed the platform with Human-in-the-Loop decision support so human analysts have explainable evidence before making conclusions."*
3. **Rule 3: If you don't know a theoretical answer, bridge back to your code.**
   - Say: *"While I would need to check the exact mathematical equation for that specific variation, in our implementation in `propagation_service.py`, we handle it by..."* Examiners love seeing code familiarity!
4. **Rule 4: Emphasize the Fact-Checking & Good News in Simulation.**
   - Evaluators love balance: *"Our simulator doesn't just show scary attacks; it realistically models defense counter-measures like community notes, fact-checkers, and verified science broadcasts."*
5. **Rule 5: Keep your screen clean and zoomed in.**
   - Use `Ctrl + Plus` if projected on a wall or TV so professors in the back row can easily read the crisp typography and dark theme.

---

## 5. Folder Index in `review tactics/`
- [01_PROJECT_STORY_AND_CONCEPTS.md](file:///c:/Users/Akash/Desktop/capstone%20phase%202/review%20tactics/01_PROJECT_STORY_AND_CONCEPTS.md) - The complete story, analogies, and concepts explained simply.
- [02_HOW_TO_DEMO_AND_PRESENT.md](file:///c:/Users/Akash/Desktop/capstone%20phase%202/review%20tactics/02_HOW_TO_DEMO_AND_PRESENT.md) - Exact step-by-step click guide and verbal script.
- [03_VIVA_QUESTIONS_AND_PERFECT_ANSWERS.md](file:///c:/Users/Akash/Desktop/capstone%20phase%202/review%20tactics/03_VIVA_QUESTIONS_AND_PERFECT_ANSWERS.md) - 25 probable viva questions with model answers.
- [04_QUICK_REVISION_CRAM_SHEET.md](file:///c:/Users/Akash/Desktop/capstone%20phase%202/review%20tactics/04_QUICK_REVISION_CRAM_SHEET.md) - This 5-minute pre-viva sheet.
