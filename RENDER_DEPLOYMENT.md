# Render Deployment Guide: AIShield Platform

This repository is pre-configured for seamless, unified 1-service deployment on [Render.com](https://render.com). The Python FastAPI backend automatically builds and serves the React frontend SPA, WebSocket feeds, and pre-trained ML models on a single URL.

---

## Method 1: Instant Blueprint Deployment (Recommended — 2 Minutes)

Render Blueprints automatically configure the build commands, environment variables, health checks, and start commands from [`render.yaml`](./render.yaml).

1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** (top right) and select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/akashhhhh246/capstone`.
4. Select the branch: **`dynamic-and-threat-enhanced`**.
5. Render will automatically detect [`render.yaml`](./render.yaml).
6. Click **Apply**.
7. Render will build the React bundle, install the Python ML stack, and launch your live application at `https://aishield-workbench.onrender.com/`.

---

## Method 2: Manual Web Service Setup (Alternative)

If you prefer creating a Web Service manually via the Render UI:

1. In Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your GitHub repo.
3. Configure the settings:
   - **Name**: `aishield-workbench`
   - **Branch**: `dynamic-and-threat-enhanced`
   - **Language / Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     chmod +x build.sh && ./build.sh
     ```
     *(Or: `cd frontend && npm install && npm run build && cd .. && pip install -r backend/requirements.txt`)*
   - **Start Command**:
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free` (or `Starter` for 1GB RAM)

4. Add the following **Environment Variables** under the **Environment** tab:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.8` | Python runtime version |
   | `NODE_VERSION` | `20.12.0` | Node.js runtime for building Vite frontend |
   | `PYTHONUNBUFFERED` | `1` | Real-time console logging |
   | `ENVIRONMENT` | `production` | Production mode |
   | `GDELT_ENABLED` | `true` | Real-time public GDELT news sync |
   | `RSS_ENABLED` | `true` | Public RSS news feed sync |
   | `GDELT_POLL_INTERVAL` | `180` | Polling interval in seconds |

5. Click **Create Web Service**.

---

## Method 3: Docker Container Deployment (Fastest & Most Reliable)

If you want 100% pre-packaged PyTorch/PyG Linux libraries:

1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your repository (`dynamic-and-threat-enhanced` branch).
3. Select **Docker** as the environment.
4. Render will automatically detect the root [`Dockerfile`](./Dockerfile).
5. Click **Create Web Service**.

---

## What to Verify After Deployment

Once Render finishes deploying (Status: `Live`):

1. **Visit your live URL**: `https://<your-app-name>.onrender.com/`
   - You should see the **AIShield Operations Dashboard**.
2. **Navigate to Threat Campaign Intelligence**: `https://<your-app-name>.onrender.com/campaigns`
   - Test the **"Scan Live Feed for Threats"** action to run live semantic clustering.
   - Test **"Export Threat Dossier (PDF)"** to download an executive intelligence report.
3. **Navigate to API Docs**: `https://<your-app-name>.onrender.com/docs`
   - Interactive Swagger API interface with all 10+ REST and WebSocket endpoints.
