from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json, pathlib, datetime, collections, re, random, unicodedata
import feedparser
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from fastapi import Depends

models.Base.metadata.create_all(bind=engine)


# =========================
# CONFIGURAÇÃO BÁSICA
# =========================

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

# =========================
# MODELOS E UTILITÁRIOS
# =========================

class Answer(BaseModel):
    user: Optional[str] = "anonymous"
    q1: Optional[str] = None
    q2: Optional[int] = None
    q3: Optional[str] = None
    q4: Optional[str] = None
    timestamp: Optional[str] = None


def read_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# TRATAMENTO DE TEXTO
# =========================

STOPWORDS = {
    "a", "o", "e", "de", "do", "da", "que", "em", "para", "com", "como",
    "no", "na", "os", "as", "um", "uma", "meu", "minha", "seu", "sua",
    "nos", "nós", "eles", "elas", "você", "vocês", "tudo", "todo",
    "todos", "ia", "inteligência", "artificial", "mais", "muito", "pouco",
    "desde", "entre", "sobre", "cada", "mesmo", "faz", "porque", "isso",
    "essa", "esse", "essa", "também", "já", "ainda", "tem", "pra", "pro"
}

POSITIVE_WORDS = {
    "ajuda", "rápido", "eficiente", "melhor", "ótimo", "positivo",
    "criativo", "facilita", "inteligente", "incrível", "útil",
    "agilidade", "automatiza", "bom", "excelente", "produtivo"
}

NEGATIVE_WORDS = {
    "difícil", "lento", "confuso", "atrapalha", "ruim", "negativo",
    "cansativo", "demorado", "complicado", "fraco"
}


def normalize_word(word: str) -> str:
    nfkd = unicodedata.normalize("NFKD", word)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()


def process_text(texts: List[str]) -> List[str]:
    full_text = " ".join(texts).lower()
    words = re.findall(r"\b[a-zà-ú]+\b", full_text)
    normalized = [normalize_word(w) for w in words]
    return [w for w in normalized if w not in STOPWORDS and len(w) > 2]


def analyze_sentiment(words: List[str]) -> str:
    positives = sum(w in POSITIVE_WORDS for w in words)
    negatives = sum(w in NEGATIVE_WORDS for w in words)
    if positives > negatives:
        return "positivo"
    elif negatives > positives:
        return "negativo"
    return "neutro"


# =========================
# LÓGICA DE INSIGHTS
# =========================

def simple_insight_from_answers(answers):
    texts, scores, frequency = [], [], []

    for ans in answers:
        if ans.get("q3"):
            texts.append(ans["q3"].lower())
        if ans.get("q2"):
            scores.append(ans["q2"])
        if ans.get("q1"):
            frequency.append(str(ans["q1"]).lower())

    all_text = " ".join(texts)
    words = re.findall(r"\b[a-zà-úÀ-ÚçÇ]+\b", all_text)
    simplified = [w.lower() for w in words]

    CUSTOM_STOPWORDS = {
        "a", "o", "e", "de", "da", "do", "em", "no", "na", "que", "para",
        "por", "com", "um", "uma", "as", "os", "é", "ser", "se", "me",
        "muito", "mais", "menos", "nas", "nos", "ao", "aos", "à", "às"
    }

    CONTEXT_STOPWORDS = {
        "ia", "inteligencia", "artificial", "codigo", "codigos", "testes", "teste", 
        "desenvolvimento", "elaboracao", "tarefa", "tarefas", "trabalho", "processo",
        "solucao", "solucoes", "pensar", "automatizar", "utilizar", "ajuda", "ajudar",
        "uso", "usando", "utilizo", "utiliza", "utilizando"
    }

    HIGHLIGHT_TOPICS = [
        "produtividade", "eficiência", "agilidade", "aprendizado", "criatividade",
        "rapidez", "facilidade", "erro", "bugs", "tempo", "automatização",
        "precisão", "clareza", "confiança", "inovação"
    ]

    filtered = [w for w in simplified if w not in CUSTOM_STOPWORDS and w not in CONTEXT_STOPWORDS]
    count = collections.Counter(filtered)
    raw_top = [w for w, _ in count.most_common(15)]

    highlighted = [w for w in HIGHLIGHT_TOPICS if w in filtered]
    top_words = list(dict.fromkeys(highlighted + raw_top))[:8]

    avg_score = sum(scores) / len(scores) if scores else 0
    freq = collections.Counter(frequency).most_common(1)
    freq_label = freq[0][0] if freq else "desconhecida"

    freq_map = {
        "daily": "uso diário",
        "diariamente": "uso diário",
        "weekly": "uso semanal",
        "semanalmente": "uso semanal",
        "monthly": "uso mensal",
        "mensalmente": "uso mensal",
        "raramente": "uso raro",
        "nunca": "sem uso"
    }

    freq_text = freq_map.get(freq_label, "uso esporádico")
    mood = "positiva" if avg_score >= 7 else "neutra" if avg_score >= 4 else "negativa"

    insight_templates = [
        f"As respostas indicam um {freq_text} das ferramentas de IA, com uma percepção {mood} e utilidade média de {avg_score:.1f}/10.",
        f"Observa-se um {freq_text}, acompanhado de uma avaliação {mood} e nota média de {avg_score:.1f}/10 sobre o impacto da IA.",
        f"Os participantes relataram {freq_text}, refletindo uma experiência {mood} e satisfação em torno de {avg_score:.1f}/10.",
        f"Há um padrão de {freq_text} e avaliação {mood}, sugerindo um impacto geral de {avg_score:.1f}/10 na rotina com IA."
    ]

    insight = random.choice(insight_templates)
    if top_words:
        insight += f" Termos como **{', '.join(top_words[:5])}** refletem os temas mais mencionados."

    return {"insight": insight, "words": [{"word": w, "sentiment": "neutral"} for w in top_words]}


# =========================
# ENDPOINTS
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/curiosity")
def get_curiosity():
    """
    Retorna uma curiosidade real sobre Inteligência Artificial
    (via Google News RSS). Se falhar, usa dados locais (mock).
    """
    try:
        feed = feedparser.parse(
            "https://news.google.com/rss/search?q=inteligencia+artificial&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        if feed.entries:
            entry = random.choice(feed.entries[:5])  # escolhe uma entre as 5 primeiras
            curiosity_text = f"{entry.title}. Leia mais: {entry.link}"
            return {"text": curiosity_text}
    except Exception as e:
        print(f"[Curiosity RSS Error] {e}")

    # fallback para mock local
    data = read_data()
    curiosities = data.get("curiosities", [])
    if not curiosities:
        raise HTTPException(status_code=404, detail="Nenhuma curiosidade disponível.")
    return random.choice(curiosities)

    data = read_data()
    if not data.get("curiosities"):
        raise HTTPException(status_code=404, detail="No curiosities available")
    return random.choice(data["curiosities"])


@app.get("/questions")
def get_questions():
    data = read_data()
    return {"questions": data.get("questions", [])}


# ===========================================
# ENDPOINT COM VALIDAÇÃO DE ENTRADAS
# ===========================================
@app.post("/answers")
def post_answers(answer: Answer, db: Session = Depends(get_db)):
    if not any([answer.q1, answer.q2, answer.q3, answer.q4]):
        raise HTTPException(status_code=400, detail="Resposta inválida ou incompleta.")

    db_answer = models.Answer(
        user=answer.user or "anonymous",
        q1=answer.q1,
        q2=answer.q2,
        q3=answer.q3,
        q4=answer.q4
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)

    return {"ok": True, "saved": {
        "user": db_answer.user,
        "q1": db_answer.q1,
        "q2": db_answer.q2,
        "q3": db_answer.q3,
        "q4": db_answer.q4,
        "timestamp": str(db_answer.timestamp)
    }}
    data = read_data()
    if "answers" not in data:
        data["answers"] = []

    payload = answer.dict()

    if not any([payload.get("q1"), payload.get("q2"), payload.get("q3"), payload.get("q4")]):
        raise HTTPException(status_code=400, detail="Resposta inválida ou incompleta.")

    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"

    data["answers"].append(payload)
    write_data(data)
    return {"ok": True, "saved": payload}


@app.get("/insight")
def get_insight(db: Session = Depends(get_db)):
    answers = db.query(models.Answer).all()
    formatted = [
        {"q1": a.q1, "q2": a.q2, "q3": a.q3, "q4": a.q4, "user": a.user}
        for a in answers
    ]
    result = simple_insight_from_answers(formatted)
    return result


@app.get("/insight-ai")
def get_insight_ai():
    return {"note": "Endpoint placeholder - integrate with OpenAI or another LLM to generate richer insights."}


# ===========================================
# NOVO ENDPOINT: LIMPAR TODAS AS RESPOSTAS
# ===========================================
@app.delete("/reset")
def reset_answers():
    data = read_data()
    data["answers"] = []
    write_data(data)
    return {"ok": True, "message": "Todas as respostas foram removidas com sucesso."}
