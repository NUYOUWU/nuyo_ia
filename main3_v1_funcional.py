import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

OLLAMA_URL = "http://localhost:11434/api/chat"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


AGENTS = {
    "linux_doctor": {
        "provider": "ollama",
        "model": "llama3.2:latest",
        "system": "Eres un experto en Arch Linux, terminal, systemd, redes locales y diagnóstico. Responde en español claro. Explica riesgos antes de sugerir comandos peligrosos."
    },
    "code_helper": {
        "provider": "ollama",
        "model": "llama3.2:latest",
        "system": "Eres un asistente de programación. Ayuda con Python, Bash, APIs, FastAPI, errores y refactorización. Explica paso a paso."
    },
    "kimi_architect": {
        "provider": "kimi",
        "model": "moonshotai/kimi-k2.6",
        "system": "Eres un arquitecto de software. Diseña sistemas simples, modulares, seguros y escalables. Responde en español claro."
    }
}


class ChatRequest(BaseModel):
    agent: str = "linux_doctor"
    prompt: str


def ask_ollama(model: str, system: str, prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if response.status_code != 200:
        return f"Error de Ollama {response.status_code}: {response.text}"

    data = response.json()
    return data["message"]["content"]


def ask_kimi(model: str, system: str, prompt: str) -> str:
    if not NVIDIA_API_KEY:
        return "Error: falta NVIDIA_API_KEY. Configúrala con export NVIDIA_API_KEY='tu_key'."

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
        "top_p": 0.9,
        "stream": False,
    }

    response = requests.post(NVIDIA_URL, headers=headers, json=payload, timeout=180)

    if response.status_code != 200:
        return f"Error de Kimi {response.status_code}: {response.text}"

    data = response.json()
    return data["choices"][0]["message"]["content"]


@app.get("/")
def root():
    return {
        "message": "Nuyo IA Server esta funcionando",
        "rutas": ["/health", "/agents", "/docs", "/chat"]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/agents")
def list_agents():
    return AGENTS


@app.post("/chat")
def chat(req: ChatRequest):
    if req.agent not in AGENTS:
        return {
            "error": f"Agente no existe: {req.agent}",
            "agentes_disponibles": list(AGENTS.keys())
        }

    agent = AGENTS[req.agent]
    provider = agent["provider"]
    model = agent["model"]
    system = agent["system"]

    if provider == "ollama":
        answer = ask_ollama(model, system, req.prompt)
    elif provider == "kimi":
        answer = ask_kimi(model, system, req.prompt)
    else:
        return {
            "error": f"Provider inválido: {provider}"
        }

    return {
        "agent": req.agent,
        "provider": provider,
        "model": model,
        "answer": answer
    }
