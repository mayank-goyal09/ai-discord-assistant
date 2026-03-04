import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from faster_whisper import WhisperModel
import torch
from diffusers import StableDiffusionPipeline

app = FastAPI()

print("Loading Whisper Model... (this might take a few seconds on first run to download)")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading Text-to-Image Model on {device}... (This will download ~4GB of weights on the first run, please be patient!)")
if device == "cuda":
    image_pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
else:
    # CPU takes longer to run, so we load full precision but it works.
    image_pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
image_pipe = image_pipe.to(device)

class TextRequest(BaseModel):
    prompt: str

class ChatMessage(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None

class ChatRequest(BaseModel):
    model: str = "mistral"
    messages: List[ChatMessage]

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

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Call Ollama's chat API with memory and optional image support"""
    messages_payload = []
    for m in req.messages:
        d = {"role": m.role, "content": m.content}
        if m.images:
            d["images"] = m.images
        messages_payload.append(d)
        
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "http://127.0.0.1:11434/api/chat",
            json={
                "model": req.model,
                "messages": messages_payload,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()
    
    # returns {"message": {"role": "assistant", "content": "..."}}
    return data

@app.post("/transcribe/audio")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an audio file using Faster Whisper"""
    # Save the file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Transcribe audio using the Whisper model
        segments, info = whisper_model.transcribe(temp_file_path, beam_size=5)
        text = "".join([segment.text for segment in segments])
        
        return {"text": text.strip()}
    finally:
        # Clean up the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/generate/image")
async def generate_image(req: TextRequest):
    """Generate an image using Stable Diffusion and return the file."""
    # We use fewer inference steps to speed it up (20 instead of the default 50).
    # If running on CPU, this might still take a couple of minutes per image.
    image = image_pipe(req.prompt, num_inference_steps=20).images[0]
    
    filename = f"temp_image_{uuid.uuid4().hex}.png"
    image.save(filename)
    
    # We return the file directly to the client (Discord bot).
    # FastAPI's FileResponse manages reading the file and setting the right headers.
    return FileResponse(filename, media_type="image/png")
