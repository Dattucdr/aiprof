# AIProf Healthcare Platform

![AIProf Healthcare Platform Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20AI%20%7C%20FastAPI%20%7C%20React-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19.0-cyan?logo=react)
![LangChain](https://img.shields.io/badge/AI-LangGraph%20%2F%20LangChain-orange)

An enterprise-grade, multi-agent AI clinical outreach, voice/text intake, risk triage, and escalation safety platform designed for modern healthcare organizations.

---

## 🌟 Key Features

- 🤖 **Dual-Assessor Multi-Agent Consensus**: Uses two independent AI agents (*Assessor A* & *Assessor B*) to analyze clinical intake and synthesize conservative risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and recommended actions (`NO_ACTION`, `FOLLOW_UP`, `CLINICAL_REVIEW`, `URGENT_CLINICAL_REVIEW`).
- 🛡️ **Deterministic Red-Flag Safety Backstop**: Hardcoded clinical rule checks that immediately force high-risk escalation upon detecting critical symptoms (e.g., chest pain, dyspnea, stroke indicators, suicide risk), acting as a fail-safe against AI hallucinations or under-triage.
- 📞 **Voice & Text Clinical Intake**: Intelligent extraction of patient symptoms, duration, severity, and context from call transcripts and messages into structured SOAP notes and EHR updates.
- 🏢 **Multi-Tenant Architecture**: Built-in tenant isolation supporting multiple hospital networks, clinics, and medical centers with role-based access control (RBAC).
- 🔄 **Outreach & Queue Management**: Celery-powered asynchronous workers for orchestrating bulk outreach campaigns, call retries, and EHR sync.
- 📊 **Clinical & Safety Analytics**: Interactive dashboards for monitoring real-time patient queues, escalations, risk metrics, and automated safety evaluation benchmarks.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React 19 + TypeScript + Vite)"]
        UI[Clinical Dashboard & Queue]
        CampUI[Campaign & Outreach Manager]
        SafetyUI[Safety & Audit Benchmark UI]
    end

    subgraph Backend ["Backend API (FastAPI)"]
        API[FastAPI Router & RBAC]
        DB[(PostgreSQL / SQLite)]
    end

    subgraph AI Engine ["Multi-Agent AI Decision Engine"]
        Intake[Voice & Text Intake Extractor]
        AssessorA[Assessor A - Agent]
        AssessorB[Assessor B - Agent]
        Consensus[Consensus Engine]
        RedFlag[Deterministic Red-Flag Safety Backstop]
        Context[Patient EHR Context Agent]
        Doc[SOAP / Clinical Note Synthesizer]
    end

    subgraph Workers ["Asynchronous Task Queue (Celery + Redis)"]
        CallWorker[Call Processing Worker]
        OutreachWorker[Outreach Worker]
        EHRWorker[EHR Sync Worker]
    end

    UI -->|REST / JSON| API
    CampUI -->|REST / JSON| API
    SafetyUI -->|REST / JSON| API

    API --> DB
    API -->|Invoke Graphs| AI Engine
    API -->|Queue Tasks| Workers

    AssessorA --> Consensus
    AssessorB --> Consensus
    Consensus --> RedFlag
    RedFlag -->|Final Risk & Action| API
    Workers --> DB
```

---

## 🛠️ Tech Stack

### **Backend & AI**
- **Framework**: Python 3.11+, FastAPI, Uvicorn
- **AI / LLM Orchestration**: LangChain, LangGraph, Google Gemini (`langchain-google-genai`)
- **Database & ORM**: PostgreSQL / SQLite, SQLAlchemy, Pydantic v2
- **Task Queue & Caching**: Celery, Redis

### **Frontend**
- **Framework**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS v4, Lucide React Icons
- **Routing & HTTP**: React Router v7, Axios

---

## 📂 Directory Structure

```
aiprof-healthcare-platform/
├── ai/                      # Multi-agent AI logic & LangGraph workflows
│   ├── graph/               # Consensus, red-flag rules, triage, voice intake, context
│   ├── schemas/             # Pydantic data schemas for AI inputs/outputs
│   └── tools/               # EHR, protocol, escalation, and validator tools
├── backend/                 # FastAPI REST application
│   ├── api/                 # API endpoint routers (patients, calls, campaigns, escalations, etc.)
│   ├── auth/                # JWT authentication, dependencies, and RBAC roles
│   ├── core/                # Configuration settings and multi-tenant security
│   ├── database/            # Database initialization, models, and seed scripts
│   ├── models/              # SQLAlchemy database models
│   ├── services/            # Business logic and service layers
│   └── main.py              # FastAPI entry point
├── workers/                 # Celery asynchronous workers (calls, outreach, EHR sync, retries)
├── frontend/                # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── api/             # Frontend API client modules
│   │   ├── components/      # UI components & protected route guards
│   │   ├── pages/           # Dashboard, Calls, Campaigns, Escalations, Analytics, Audit pages
│   │   └── App.tsx          # Main React router application
├── demo/                    # Synthetic demo dataset (300 patients)
├── tests/                   # Test suite & safety benchmark evaluation scripts
├── docker-compose.yml       # Docker environment (PostgreSQL & Redis)
├── requirements.txt         # Python dependencies
└── pytest.ini               # Test configuration
```

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.10+
- **Node.js** 18+ and **npm**
- **Docker & Docker Compose** (Optional, for running PostgreSQL and Redis)

---

### 1. Environment Setup

Copy `.env.example` (or set up `.env`) in the root directory:

```env
DATABASE_URL=sqlite:///./aiprof_healthcare.db
# For PostgreSQL: postgresql://postgres:postgres@localhost:5432/aiprof_healthcare
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_jwt_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

### 2. Backend Setup & Run

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize DB & Seed 300 Demo Patients**:
   ```bash
   python backend/seed_300_patients.py
   ```

4. **Start the FastAPI Backend Server**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *Access API Interactive Documentation at `http://localhost:8000/docs`.*

---

### 3. Celery Workers Setup (Optional / Outreach Queue)

Start Redis (via Docker or local instance):
```bash
docker-compose up -d redis
```

Run the Celery worker:
```bash
celery -A workers.celery_app worker --loglevel=info
```

---

### 4. Frontend Setup & Run

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install npm packages**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   *Access the web interface at `http://localhost:5173`.*

---

## 🛡️ AI Safety & Evaluation Framework

Safety and reliability are top priorities for healthcare AI:
- **Red-Flag Safety Backstop**: Located at `ai/graph/red_flag_rules.py`, this module scans for high-risk symptoms and overrides any lenient AI assessment.
- **Safety Benchmark Evaluation**: Located in `tests/run_safety_evaluation.py`, this suite runs automated tests across synthetic patient safety cases (`tests/safety_dataset.py`) to verify zero under-triage for critical conditions.

Run safety benchmarks:
```bash
pytest tests/
# Or run safety evaluation directly:
python tests/run_safety_evaluation.py
```

---

## 🔐 Default Seed Credentials

Upon initial database seed, default system users are created:
- **Campaign**: `Campaign@apollo-demo.com` / `Campaign@12345`

## 📄 License

This project is released under the **MIT License**.
