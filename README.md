<!-- Header Banner -->
<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=250&section=header&text=AI%20Discord%20Assistant&fontSize=50&animation=fadeIn&fontAlignY=38&desc=Multimodal%20Intelligence%20in%20Your%20Server&descAlignY=55&descAlign=50" alt="Header" />
</div>

<!-- Technology Badges -->
<div align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  </a>
  <a href="https://discordpy.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py"/>
  </a>
  <a href="https://ollama.com/">
    <img src="https://img.shields.io/badge/Ollama-FFFFFF?style=for-the-badge&logo=Ollama&logoColor=black" alt="Ollama"/>
  </a>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/HuggingFace-F9AB00?style=for-the-badge&logo=huggingface&logoColor=white" alt="HuggingFace"/>
</div>

<br/>

<!-- Introduction -->
<div align="center">
  <i>A fully autonomous, self-hosted Discord bot powered by state-of-the-art open-source machine learning models. Chat contextually, generate stunning images, analyze visual data, and transcribe voice messages—all running exactly where you want it.</i>
</div>

<br/>

<details open>
  <summary><b>📖 Table of Contents</b></summary>
  <ol>
    <li><a href="#-the-problem">The Problem</a></li>
    <li><a href="#-the-logic">The Logic</a></li>
    <li><a href="#-the-result">The Result</a></li>
    <li><a href="#-see-it-in-action">See It In Action</a></li>
    <li><a href="#-core-capabilities--models">Core Capabilities & Models</a></li>
    <li><a href="#-system-architecture">System Architecture</a></li>
    <li><a href="#-project-structure">Project Structure</a></li>
    <li><a href="#-prerequisites--system-requirements">Requirements</a></li>
    <li><a href="#-step-by-step-installation">Installation</a></li>
    <li><a href="#-command-reference">Command Reference</a></li>
    <li><a href="#-troubleshooting-guide">Troubleshooting</a></li>
  </ol>
</details>

---

## 🌟 The Problem
**Users juggle separate tools for text, image, and voice AI — creating a fragmented, inefficient, and frustrating experience.** Context is lost jumping between Midjourney, ChatGPT, and speech-to-text tools. Privacy is compromised by sending data to multiple third-party APIs.

## 🧠 The Logic
**A custom FastAPI backend orchestrates three distinct AI models — contextual chat (Mistral), diffusion-based imaging (Stable Diffusion), and real-time audio transcription (Faster-Whisper) — via unified API endpoints.** By decoupling the heavy ML operations from the Discord client interface, the system achieves maximum scalability without blocking event loops.

## 🚀 The Result
**A production-ready Discord assistant handling multimodal AI requests in real-time, eliminating external tools through seamless RESTful integration.** Everything runs locally, guaranteeing data privacy and zero subscription costs for external APIs.

---

<div align="center">
  <h2>🎥 See It In Action</h2>
  <p><i>Watch the bot generate images, transcribe audio, and chat seamlessly!</i></p>
  
  <!-- Add your YouTube link here -->
  <a href="URL_TO_YOUR_YOUTUBE_VIDEO">
    <img src="https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg" width="800" alt="Watch the Demo">
  </a>
</div>

---

## 🤖 Core Capabilities & Models

<table align="center" width="100%">
  <tr>
    <td align="center" width="25%">
      <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Camera%20with%20Flash.png" alt="Vision" width="80" />
      <br />
      <b>Computer Vision</b>
    </td>
    <td width="75%">
      Utilizes the <b>LLaVA (Large Language-and-Vision Assistant)</b> model running via Ollama. When a user attaches an image, the bot seamlessly transitions to a vision state, analyzing the pixels and describing the scene, answering questions about the image's content.
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Studio%20Microphone.png" alt="Voice" width="80" />
      <br />
      <b>Audio Transcription</b>
    </td>
    <td width="75%">
      Powered by <b>Faster-Whisper (Int8 Compute)</b>. Captures raw `.ogg`, `.mp3`, or `.wav` voicenotes directly from Discord, processing the raw audiobytes and decoding them into highly accurate text using the base Whisper model architecture, feeding it directly into the LLM context.
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Milky%20Way.png" alt="Generation" width="80" />
      <br />
      <b>AI Art Generation</b>
    </td>
    <td width="75%">
      Harnesses the power of <b>Stable Diffusion v1-5 (RunwayML)</b> via HuggingFace `diffusers`. Generates complex visual concepts in ~20 inference steps natively on the host's GPU/CPU. Includes an interactive UI inside Discord to regenerate or delete generation outputs dynamically.
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Robot.png" alt="Chat" width="80" />
      <br />
      <b>Contextual LLM</b>
    </td>
    <td width="75%">
      Powered by <b>Mistral 7B</b>. The core logic brain. Maintains an active running memory (up to 10 conversational turns per unique Discord User ID), maintaining distinct system prompts governing its "Nexus" personality.
    </td>
  </tr>
</table>

---
