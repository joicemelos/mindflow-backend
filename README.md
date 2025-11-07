# MindFlow Backend (FastAPI + Poetry)

Um backend simples e modular desenvolvido para o protótipo MindFlow, que coleta respostas, gera pequenos insights e armazena dados simulados via JSON mock.

## Visão geral
O backend do MindFlow utiliza FastAPI e Poetry para oferecer uma API simples, organizada e ideal para prototipagem rápida.
Ele simula persistência local e geração de insights automáticos, servindo como base para o front-end desenvolvido em React.

## Estrutura do Projeto
mindflow-backend/
│
├── app/
│   ├── main.py              # Aplicação principal FastAPI
│   └── data/
│       └── mock_data.json   # Armazena curiosidades, perguntas e respostas mockadas
│
├── pyproject.toml           # Configuração do Poetry
├── Dockerfile               # Containerização simples
├── run.sh                   # Script rápido de inicialização
└── README.md                # Este arquivo

## Configuração Rápida
* Opção 1 — Usando Poetry (recomendado)
```bash
    poetry install
    poetry run uvicorn app.main:app --reload --port 8000
```

* Opção 2 — Sem Poetry (usando pip)
```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install fastapi uvicorn
    uvicorn app.main:app --reload --port 8000
```

A API estará disponível em: 
    ```http://localhost:8000/```


## Endpoints Disponíveis
|  Método  | Rota         | Descrição                                             |
| :------: | :----------- | :---------------------------------------------------- |
|  **GET** | `/curiosity` | Retorna uma curiosidade aleatória do mock             |
|  **GET** | `/questions` | Lista as perguntas do questionário                    |
| **POST** | `/answers`   | Recebe respostas em JSON e salva no mock              |
|  **GET** | `/insight`   | Gera um insight simples com base nas respostas salvas |
|  **GET** | `/health`    | Health check (verifica se a API está ativa)           |
| **POST** | `/reset`     | Limpa as respostas do mock (para testes)              |


## Notas
As respostas enviadas via /answers são armazenadas no mock_data.json.
O endpoint /insight realiza uma análise simples (palavras-chave + média de pontuação) e retorna uma frase automática.
Esse comportamento pode ser substituído futuramente por um modelo de IA real.

## Próximos passos
- Substituir mock JSON por banco de dados real (ex: PostgreSQL).
- Integrar com serviços de IA para insights mais profundos.
 - Adicionar autenticação e controle de usuários.
- Criar testes automatizados (pytest).