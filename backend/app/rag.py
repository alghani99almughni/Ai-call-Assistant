"""Local embeddings + tenant-filtered retrieval helpers."""
from sentence_transformers import SentenceTransformer
import httpx
from .config import settings

# multilingual-e5-small produces 384-dimensional vectors.
_model = None
def embed(text: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer("intfloat/multilingual-e5-small")
    return _model.encode("passage: " + text, normalize_embeddings=True).tolist()

def embed_query(text: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer("intfloat/multilingual-e5-small")
    return _model.encode("query: " + text, normalize_embeddings=True).tolist()

async def ollama_chat(messages: list[dict], temperature: float = 0.2) -> str:
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(f"{settings.ollama_url}/api/chat", json={
            "model": settings.ollama_model, "messages": messages, "stream": False,
            "options": {"temperature": temperature}
        })
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

def build_context(chunks: list[str], max_chars: int = 6000) -> str:
    return "\n\n".join(chunks)[:max_chars]
