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

import base64

class ImageControlView(discord.ui.View):
    def __init__(self, prompt: str):
        super().__init__(timeout=None) # The buttons will persist
        self.prompt = prompt

    @discord.ui.button(label="Regenerate", style=discord.ButtonStyle.primary, emoji="🔄")
    async def regenerate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"🎨 Regenerating: `{self.prompt}`...", ephemeral=True)
        # Send the API request again
        async with httpx.AsyncClient(timeout=300) as http:
            try:
                r = await http.post(f"{BACKEND_URL}/generate/image", json={"prompt": self.prompt})
                r.raise_for_status()
                import io
                image_bytes = r.content
                file = discord.File(fp=io.BytesIO(image_bytes), filename="regenerated_image.png")
                # Send the new image as a completely new message with the same buttons!
                await interaction.followup.send(f"Here is another version for: **{self.prompt}**", file=file, view=ImageControlView(self.prompt))
            except Exception as e:
                print(f"Error regenerating image: {e}")
                await interaction.followup.send("Failed to regenerate the image.", ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # We delete the message that the buttons are attached to (the bot's message)
        await interaction.message.delete()

client = discord.Client(intents=intents)

user_memory = {}
MAX_MEMORY = 10

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
    
    # ---------------- TEXT-TO-IMAGE ----------------
    if content.lower().startswith("image:"):
        prompt = content[6:].strip()
        if not prompt:
            await message.channel.send("Provide a prompt, e.g. `image: a futuristic cyber city`")
            return
            
        await message.channel.send(f"🎨 Painting `{prompt}`... This will take a moment, especially if this is the first time running!")
        
        async with httpx.AsyncClient(timeout=300) as http:
            try:
                r = await http.post(f"{BACKEND_URL}/generate/image", json={"prompt": prompt})
                r.raise_for_status()
                
                # The backend returns the raw image file bytes
                import io
                image_bytes = r.content
                file = discord.File(fp=io.BytesIO(image_bytes), filename="generated_image.png")
                # We attach the view (the buttons) to the message!
                view = ImageControlView(prompt=prompt)
                await message.channel.send(f"Here is your image for: **{prompt}**", file=file, view=view)
            except Exception as e:
                print(f"Error generating image: {e}")
                await message.channel.send("Sorry, something went wrong while generating the image.")
        return

    # ---------------- CLEAR MEMORY ----------------
    if content.lower() == "ai: clear":
        user_memory[message.author.id] = []
        await message.channel.send("🧹 Memory cleared! I have forgotten our previous conversation.")
        return

    # Check for attachments (Audio or Image)
    is_audio = False
    is_image = False
    audio_bytes = None
    image_bytes = None
    
    if message.attachments:
        attachment = message.attachments[0]
        mime = attachment.content_type or ""
        
        if mime.startswith("audio") or attachment.filename.lower().endswith((".ogg", ".wav", ".mp3", ".m4a")):
            is_audio = True
            audio_bytes = await attachment.read()
        elif mime.startswith("image") or attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            is_image = True
            image_bytes = await attachment.read()

    # Extract user text
    user_text = ""
    if content.lower().startswith("ai:"):
        user_text = content[3:].strip()
        
    # Ignore standalone messages that aren't addressed to bot, unless they sent audio/image
    if not user_text and not is_audio and not is_image:
        return

    # Initialize memory for user
    user_id = message.author.id
    if user_id not in user_memory:
        # Give the AI a Name and Personality using a "system" prompt!
        user_memory[user_id] = [
            {"role": "system", "content": "You are a highly intelligent, friendly Discord AI assistant named Nexus. You have multimodal capabilities: you can understand text, read images (Vision), transcribe voice messages, and generate images. Always be helpful and concise."}
        ]

    # 1. Handle Audio -> Text
    if is_audio:
        await message.channel.send("🎙️ Listening to your voice message...")
        async with httpx.AsyncClient(timeout=120) as http:
            files = {'file': (message.attachments[0].filename, audio_bytes, mime or 'audio/ogg')}
            r = await http.post(f"{BACKEND_URL}/transcribe/audio", files=files)
            r.raise_for_status()
            user_text = r.json().get("text", "")
            
        if not user_text:
            await message.channel.send("I couldn't hear any words in that audio.")
            return

    # Build the memory entry
    if not user_text:
        user_text = "What is in this image?"

    mem_entry = {"role": "user", "content": user_text}
    model_to_use = "mistral"

    # 2. Handle Image -> base64
    if is_image:
        base64_img = base64.b64encode(image_bytes).decode('utf-8')
        mem_entry["images"] = [base64_img]
        model_to_use = "llava" # Must switch to LLaVA for vision!

    # Append to memory
    user_memory[user_id].append(mem_entry)

    # Keep memory in limits (last 10 messages)
    if len(user_memory[user_id]) > MAX_MEMORY:
        user_memory[user_id] = user_memory[user_id][-MAX_MEMORY:]

    # 3. Call Chat API
    print(f"  → Calling backend /chat with model: {model_to_use}")
    async with httpx.AsyncClient(timeout=120) as http:
        payload = {
            "model": model_to_use,
            "messages": user_memory[user_id]
        }
        r = await http.post(f"{BACKEND_URL}/chat", json=payload)
        r.raise_for_status()
        data = r.json()

    ai_reply = data["message"]["content"]
    
    # 4. Append Bot reply to memory
    user_memory[user_id].append({"role": "assistant", "content": ai_reply})

    # Format the final reply
    reply_msg = ""
    if is_audio:
        reply_msg += f"**You said:** {user_text}\n\n"
    reply_msg += f"{ai_reply}"

    # Send in chunks if it exceeds Discord's 2000 character limit
    if len(reply_msg) > 2000:
        for i in range(0, len(reply_msg), 2000):
            await message.channel.send(reply_msg[i:i+2000])
    else:
        await message.channel.send(reply_msg)

client.run(DISCORD_TOKEN)
