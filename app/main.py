from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import json, pathlib, datetime, collections, re

BASE = pathlib.Path(__file__).parent / "data"
DATA_FILE = BASE / "mock_data.json"

app = FastAPI(title="MindFlow - Mock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Answer(BaseModel):
    user: Optional[str] = "anonymous"
    q1: Optional[str] = None
    q2: Optional[int] = None
    q3: Optional[str] = None
    timestamp: Optional[str] = None

def read_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.get('/health')
def health():
    return {"status": "ok"}

@app.get('/curiosity')
def get_curiosity():
    data = read_data()
    if not data.get("curiosities"):
        raise HTTPException(status_code=404, detail="No curiosities available")
    # return the first curiosity (or random if you want)
    return data["curiosities"][0]

@app.get('/questions')
def get_questions():
    data = read_data()
    return data.get("questions", [])

@app.post('/answers')
def post_answers(answer: Answer):
    data = read_data()
    if "answers" not in data:
        data["answers"] = []
    payload = answer.dict()
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    data["answers"].append(payload)
    write_data(data)
    return {"ok": True, "saved": payload}

def simple_insight_from_answers(answers: List[dict]) -> str:
    # Aggregate q1 (most common tool), q2 average, top words from q3
    if not answers:
        return "Ainda não há respostas suficientes para gerar um insight. Seja o primeiro!"
    tools = [a.get("q1") for a in answers if a.get("q1")]
    ratings = [a.get("q2") for a in answers if isinstance(a.get("q2"), (int, float))]
    texts = " ".join([a.get("q3","") or "" for a in answers])
    most_common_tool = None
    if tools:
        most_common_tool = collections.Counter(tools).most_common(1)[0][0]
    avg_rating = round(sum(ratings)/len(ratings), 1) if ratings else None
    # top words:
    words = re.findall(r"\w{3,}", texts.lower())
    stop = set(['com','para','que','e','a','o','de','no','na','do','da','em','se','o','a','as','os'])
    filtered = [w for w in words if w not in stop]
    top_words = [w for w,_ in collections.Counter(filtered).most_common(6)]
    parts = []
    if most_common_tool:
        parts.append(f"Ferramenta mais citada: {most_common_tool}.")
    if avg_rating is not None:
        parts.append(f"Nota média de utilidade: {avg_rating}/10.")
    if top_words:
        parts.append("Termos frequentes: " + ", ".join(top_words) + ".")
    return " ".join(parts)

@app.get('/insight')
def get_insight():
    data = read_data()
    insight = simple_insight_from_answers(data.get("answers", []))
    return {"insight": insight, "count_answers": len(data.get("answers", []))}

# Placeholder for future OpenAI integration
@app.get('/insight-ai')
def get_insight_ai():
    return {
        "note": "Endpoint placeholder - integrate with OpenAI or another LLM to generate richer insights."
    }
