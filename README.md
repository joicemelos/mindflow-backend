# MindFlow Backend (FastAPI + Poetry)

This is a scaffold backend for the **MindFlow** prototype. It uses **FastAPI** and a small mock JSON store to simulate persistence and simple AI-driven insight generation.

## What is included
- `pyproject.toml` (Poetry config)
- `app/main.py` (FastAPI application with endpoints)
- `app/data/mock_data.json` (mock data for curiosities, questions and answers)
- `Dockerfile` (simple containerization)
- `run.sh` (quick start script)
- `README.md` (this file)

## Quick start (no Poetry)
If you don't have Poetry installed, you can run with plain pip inside a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
uvicorn app.main:app --reload --port 8000
```

## With Poetry (recommended)
```bash
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /curiosity` — returns a random curiosity (or the first, from mock)
- `GET /questions` — returns the survey questions
- `POST /answers` — accepts an answer JSON and saves it to mock_data.json
- `GET /insight` — generates a simple aggregated insight from saved answers
- `GET /health` — health check

## Notes
This scaffold uses a simple file-based mock. In production, replace with a database (Postgres) and connect to a real AI service (OpenAI) for richer insights.
