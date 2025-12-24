from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

class TextRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Backend is up"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate/text")
async def generate_text(req: TextRequest):
    """Call Ollama's mistral model via HTTP"""
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": req.prompt,
                "stream": False  # Get full response at once
            }
        )
        response.raise_for_status()
        data = response.json()
    
    return {"response": data["response"]}
