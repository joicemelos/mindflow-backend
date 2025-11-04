#!/usr/bin/env bash
# Quick run without poetry
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn
uvicorn app.main:app --reload --port 8000
