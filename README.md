# CredSaathi — Transparent Credit & Scheme Discovery Platform

CredSaathi is a fintech platform designed for micro-entrepreneurs and applicants across India to discover relevant government and bank loan schemes, understand eligibility criteria, manage structured document vaults, simulate financial scenarios, and track credit application status transparently.

---

## Architecture Overview

```text
React Frontend (Vercel)
       ↓ (HTTP REST / API V1)
FastAPI Backend (Render Web Service)
       ↓ (Internal HTTP Client + Bearer Key)
Stateless AI Service (Render Web Service)
       ↓
Managed PostgreSQL (Render Database)
```

- **`frontend/`**: React 18 + TypeScript + Vite UI (Stitch UX design tokens).
- **`backend/`**: FastAPI + SQLAlchemy + Alembic core platform (Auth, DB, Financial Calculation Engine, Applications, Documents).
- **`ai/`**: FastAPI AI microservice layer (Saakshi RAG Assistant, Document Extraction, Semantic Scheme Matching).

---

## Local Multi-Service Development Setup (Windows PowerShell)

### Step 1: Start PostgreSQL Dependency Container

```powershell
# Run from repository root
docker compose up -d postgres

# Verify container status and health
docker compose ps
```

---

### Step 2: Configure Environment Files

Create `.env` files in each service directory using the provided templates:

#### Backend (`backend/.env`):
```powershell
Copy-Item backend/.env.example backend/.env
```
Ensure `DATABASE_URL` matches your local database:
```env
DATABASE_URL=postgresql+psycopg://credsaathi_user:credsaathi_password@localhost:5432/credsaathi
AI_SERVICE_URL=http://localhost:8001/api/v1/ai
AI_API_KEY=credsaathi_secret_api_key_v1
```

#### AI Microservice (`ai/.env`):
```powershell
Copy-Item ai/.env.example ai/.env
```

#### Frontend (`frontend/.env`):
```powershell
Copy-Item frontend/.env.example frontend/.env
```
Ensure real backend integration is active:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEMO_MODE=false
```

---

### Step 3: Initialize Database & Run Migrations

```powershell
# Create and activate virtual environment in backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r ..\requirements.txt

# Run Alembic migrations to create tables
python -m alembic upgrade head
cd ..
```

---

### Step 4: Launch Backend & AI Services (Separate Terminals)

#### Terminal 1 — AI Microservice (Port 8001):
```powershell
cd ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
python -m uvicorn ai.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2 — FastAPI Backend (Port 8000):
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 5: Launch Frontend & Verify Endpoints

#### Terminal 3 — Vite Frontend (Port 5173):
```powershell
cd frontend
npm install
npm run dev
```

#### Health Check Verification Commands:
```powershell
# Verify Backend Health Endpoint (Port 8000)
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Verify AI Service Health Endpoint (Port 8001)
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ai/health"
```

---

## Production Deployment Blueprint

### Provider Stack
- **Frontend**: Vercel (Root: `frontend/`, Framework Preset: Vite)
- **Backend & AI Services**: Render (Blueprinted via `render.yaml`)
- **Database**: Render Managed PostgreSQL (`credsaathi-db`)

### Deployment Manifests Created
- `render.yaml`: Provisions `credsaathi-ai`, `credsaathi-backend`, and `credsaathi-db`.
- `vercel.json`: Configures Vite SPA routing for production deployments.

---

## Production Provider Configuration & Manual Setup Checklist

### 1. Render Environment Setup (Backend & AI)
1. **AI Microservice (`credsaathi-ai`)**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn ai.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/api/v1/ai/health`
   - Set `AI_API_KEYS` to a strong randomly generated string.
   - Configure live LLM Provider credentials if switching off mock provider: `AI_DEFAULT_PROVIDER=openai`, `AI_LLM_API_KEY=sk-...`.

2. **Backend Service (`credsaathi-backend`)**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`
   - Set `SECRET_KEY` to a 64-character hex string.
   - Set `AI_SERVICE_URL=https://credsaathi-ai.onrender.com/api/v1/ai`.
   - Set `AI_API_KEY` matching `credsaathi-ai`'s `AI_API_KEYS`.
   - Set `DATABASE_URL` matching the Render PostgreSQL internal connection string (`postgresql+psycopg://...`).
   - Persistent Disk: Attach a Render Persistent Disk at `/app/uploads` to persist uploaded documents across service restarts.

3. **Database Migration Execution**:
   - Run Alembic migration as a pre-deploy step on Render Backend service: `python -m alembic upgrade head`.

### 2. Vercel Environment Setup (Frontend)
1. Set Root Directory to `frontend/`.
2. Add Environment Variables:
   - `VITE_API_BASE_URL=https://credsaathi-backend-1voa.onrender.com/api/v1`
   - `VITE_DEMO_MODE=false`

---

## Post-Deployment Smoke Test Protocol

Execute these steps after deployment to confirm live readiness:

1. **Health Verification**:
   - `GET https://credsaathi-backend-1voa.onrender.com/health` -> HTTP 200 `{"status": "healthy"}`
   - `GET https://credsaathi-ai.onrender.com/api/v1/ai/health` -> HTTP 200 `{"status": "healthy"}`
2. **Auth Verification**:
   - Register a new user at `https://credsaathi.vercel.app/register` and confirm successful JWT generation.
3. **Financial & Scheme Discovery Verification**:
   - Fill in Loan Requirement form -> Confirm hard eligibility filtering + AI scheme matching.
4. **Document AI Verification**:
   - Upload sample PDF/PNG document -> Confirm storage and extraction response.
5. **Saakshi AI Verification**:
   - Ask Saakshi a question -> Confirm grounded answer with disclaimers.

---

## Automated Test Verification

```powershell
# Run backend and AI test suite (124 tests)
python -m pytest backend/tests/ ai/tests/

# Run frontend tests and build check
cd frontend
npm test -- --run
npm run build
```
