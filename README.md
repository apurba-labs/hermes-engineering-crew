# Hermes Engineering Crew

Hermes Engineering Crew is a multi-agent AI engineering assistant that analyzes GitHub repositories using collaborative AI agents powered by local Gemma models through Ollama.

Built with FastAPI, Next.js, and Hermes-style orchestration workflows.

---

# Features

- GitHub repository ingestion
- AI-powered security analysis
- Architecture review agent
- Engineering roadmap generation
- Multi-agent orchestration workflow
- Local AI inference using Gemma + Ollama
- Modern Next.js dashboard
- Structured engineering reports

---

# Orchestration Philosophy

Hermes Engineering Crew follows a Hermes-inspired orchestration model where specialized AI agents collaborate through a central orchestrator to analyze repositories, synthesize findings, and generate engineering recommendations.

---

# Architecture

```text
GitHub Repository
        ↓
GitHub Loader Service
        ↓
Hermes Orchestrator
        ↓
Security Agent
Architecture Agent
Planning Agent
        ↓
Final Engineering Report
```

---

# Orchestration Philosophy

Hermes Engineering Crew follows a Hermes-inspired orchestration model where specialized AI agents collaborate through a central orchestrator to analyze repositories, synthesize findings, and generate engineering recommendations.

Each agent is responsible for a focused engineering domain:

- Security Analysis
- Architecture Review
- Engineering Planning

The Hermes Orchestrator coordinates agent execution and aggregates structured reports into a unified engineering analysis workflow.

---

# Tech Stack

## Backend
- FastAPI
- Python
- AsyncIO
- Ollama
- Gemma 3
- Hermes-inspired orchestration architecture

## Frontend
- Next.js
- TypeScript
- TailwindCSS

---

# Current MVP Workflow

1. Enter a GitHub repository URL
2. Hermes Orchestrator loads repository structure
3. AI agents analyze repository
4. Security risks are identified
5. Architecture review is generated
6. Planning Agent creates engineering roadmap
7. Dashboard displays structured reports

---

# AI Agents

## Security Analyst Node
Analyzes:
- hardcoded secrets
- insecure configurations
- authentication risks
- dangerous patterns

## Architecture Agent
Reviews:
- repository structure
- modularity
- engineering organization

## Planning Agent
Generates:
- engineering roadmap
- technical priorities
- next-step recommendations

---

# Local AI Inference

Hermes Engineering Crew uses:

- Ollama
- Gemma 3 (1B)

for lightweight local inference and privacy-focused AI orchestration.

---

# Run Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

# Run Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

# Environment Variables

Create:

```text
backend/.env
```

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
OLLAMA_TIMEOUT=300

MAX_REPO_FILES=8
MAX_FILE_CONTENT_LENGTH=800
```

---

# Screenshots

## Swagger API Response

- Multi-agent engineering reports
- AI-powered security analysis
- Architecture review workflow

## Dashboard UI

- Repository input interface
- Agent orchestration visualization
- Structured AI report cards

---

# Project Status

Current Phase:
- GitHub Loader ✅
- AI Security Agent ✅
- Architecture Agent ✅
- Planning Agent ✅
- Hermes Orchestrator ✅
- Next.js Dashboard ✅
- Local Gemma Inference ✅

---

# Vision

Hermes Engineering Crew explores collaborative AI engineering workflows where specialized AI agents work together to analyze, review, and improve software repositories.

---

# License

MIT