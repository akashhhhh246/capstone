# Frontend Application — National Security Research Analyst Workbench

Cybersecurity & Information-Integrity Analyst Dashboard built with React 18, TypeScript, Vite, Material UI (MUI), React Flow, Recharts, Axios, and WebSockets.

## Architecture
- **Language**: TypeScript (strict mode)
- **UI Framework**: Material UI (MUI v5) + Emotion
- **Graph Visualizations**: `@xyflow/react` (React Flow)
- **Charts & Telemetry**: Recharts
- **State & Networking**: Axios + WebSocket client (`wsService`) with auto-reconnect
- **Design System**: National Security / Cyber Defense Dark Mode palette (Obsidian, Slate Navy, Cobalt, Emerald, Crimson, Amber).

## Key Analyst Workbenches
1. **Dashboard (`/`)**: High-level KPIs, AI vs Human distribution, risk breakdown, active threat alerts, and recent content ingestions.
2. **Content Analysis (`/analysis`)**: Interactive workbench with presets and raw text input, AI probability bars, GLTR statistical token coloring, watermark audits, and one-click DAG lineage tracking.
3. **Provenance Explorer (`/provenance`)**: Interactive DAG graph canvas displaying root origin, paraphrased derivatives, platform reposts, and author accounts.
4. **Propagation Analysis (`/propagation`)**: Multi-platform network topology, velocity gauges, estimated reach, and GNN anomaly scores.
5. **Campaign Analysis (`/campaigns`)**: Master-detail campaign intelligence hub with itemized explainability reasons.
6. **Real-Time Simulation (`/simulation`)**: Asynchronous simulation deck with event rate slider, start/pause/stop controls, and live WebSocket streaming event log.
7. **Model Governance (`/models`)**: Model metadata transparency cards, performance metrics, limitations, and Privacy & Civil Liberties charter.

## Quick Start
```powershell
# 1. Install dependencies
npm.cmd install

# 2. Run dev server
npm.cmd run dev

# 3. Production build & typecheck
npm.cmd run build
```
Application will be live at `http://localhost:5173`.
