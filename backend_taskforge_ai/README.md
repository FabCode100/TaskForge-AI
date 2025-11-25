# TaskForge-AI Backend (FastAPI)

This is a minimal FastAPI scaffold for the TaskForge-AI marketplace backend.

Run locally:

```powershell
python backend_taskforge_ai/main.py
```

Or with Docker Compose:

```powershell
docker compose up --build
```

The app exposes a health endpoint at `/health` and API routers under `/api/v1/`.

OpenAI integration
- To enable AI responses for executions set environment variable `OPENAI_API_KEY` (or add it to `.env`).
- Optionally set `OPENAI_MODEL` in `.env` (default: `gpt-3.5-turbo`).

