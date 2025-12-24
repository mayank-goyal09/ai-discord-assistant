import os
import httpx
import discord
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

# Load .env from current directory
load_dotenv(dotenv_path=".env")

# Debug: print what we got
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

print(f"DEBUG: DISCORD_TOKEN = {DISCORD_TOKEN}")
print(f"DEBUG: BACKEND_URL = {BACKEND_URL}")

if not DISCORD_TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found in .env!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message: discord.Message):
    print(f"📨 Message from {message.author}: {message.content}")
    
    if message.author.bot:
        print("  → Ignoring bot message")
        return

    content = (message.content or "").strip()
    if not content.lower().startswith("ai:"):
        print("  → Doesn't start with 'ai:'")
        return

    prompt = content[3:].strip()
    if not prompt:
        await message.channel.send("Send like: ai: explain transformers in 2 lines")
        return

    print(f"  → Calling backend with prompt: {prompt}")
    async with httpx.AsyncClient(timeout=60) as http:
        r = await http.post(f"{BACKEND_URL}/generate/text", json={"prompt": prompt})
        r.raise_for_status()
        data = r.json()

    print(f"  → Backend replied: {data}")
    await message.channel.send(data["response"])

client.run(DISCORD_TOKEN)
