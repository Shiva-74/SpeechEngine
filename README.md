#  Neural Dictate: Intelligent Low-Latency Speech Engine
**(Ready-to-Use Output | No LLMs | <1500ms Latency)**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green) ![Model](https://img.shields.io/badge/Model-Faster--Whisper-orange) ![License](https://img.shields.io/badge/License-MIT-purple) ![Status](https://img.shields.io/badge/Status-Production--Ready-red)

A real-time, privacy-focused speech dictation engine that transforms raw voice input into structured, grammatically correct, and formatted text immediately. Built for speed and accuracy without relying on cloud APIs or Large Language Models (LLMs).

---

##  Table of Contents
- [Problem Statement](#-problem-statement)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Performance & Benchmarks](#-performance--benchmarks)
- [Installation & Setup](#-installation--setup)
- [Usage Guide (Voice Commands)](#-usage-guide-voice-commands)
- [Tech Stack](#-tech-stack)

---

##  Problem Statement
Standard speech-to-text tools output raw streams of consciousness:
> *"um hello draft email to boss saying i am late no i mean sick regards john"*

This requires manual editing, wasting time. **Neural Dictate** solves this by producing ready-to-use text instantly:
> **Subject: Sick Leave**
>
> **Hello Boss,**
>
> **I am sick.**
>
> **Regards,**
> **John**

All processing happens **locally** with strict latency constraints (**≤1500ms**).

---

##  Key Features

*   ** Ultra-Low Latency:** Optimized pipeline achieves **~800-1200ms** end-to-end latency using in-memory processing and quantized models.
*   ** Privacy-First (No LLMs):** Uses lightweight ML models (`Faster-Whisper`, `T5-Small`) running entirely on the CPU. No data leaves your device.
*   ** Smart Formatting:** Context-aware logic automatically formats **Emails**, **Bulleted Lists**, and **Checklists**.
*   ** Grammar Correction:** Filters out fillers (*um, uh, like*) and fixes sentence structure/punctuation.
*   ** Intelligent VAD:** Frontend Voice Activity Detection automatically chunks speech based on natural pauses.
*   ** Split-Screen UI:** Real-time view of Raw STT Input vs. Final Polished Output.

---

##  System Architecture

The project uses a **"Sandwich Pipeline"** architecture to ensure formatting survives the grammar correction phase.

1.  **Frontend (VAD):** JS detects silence (>1000ms), slices audio, and sends it as a Blob.
2.  **In-Memory Processing:** Python receives the blob and pipes it directly to FFmpeg/Whisper in RAM (No Disk I/O).
3.  **ASR Engine:** `Faster-Whisper` (Int8 Quantized) transcribes audio to raw text.
4.  **Logic Engine (Pre-Process):** Cleans fillers, repetitions, and repairs ASR hallucinations (e.g., "Bled" -> "Bullet").
5.  **Grammar Engine:** `T5-Base` model fixes capitalization and punctuation.
6.  **Logic Engine (Post-Process):** Applies structural formatting (Bullets, Paragraphs, Email headers).

```mermaid
graph LR
    A[User Speaks] -->|VAD Cut| B(Backend API)
    B -->|In-Memory Pipe| C[Whisper ASR]
    C --> D[Regex Cleaner]
    D --> E[T5 Grammar Model]
    E --> F[Smart Formatter]
    F --> G[Final UI Output]
```
## Performance & Benchmarks
Tested on standard hardware (Intel i5/i7, No GPU required).  
Metric	Result	Notes  
ASR Latency	~300ms	Using Faster-Whisper (Int8)  
Grammar Latency	~400ms	Using optimized T5-Base  
Logic/Formatting	~1ms	Regex-based (Instant)  
Total Pipeline	~900ms	Well within the 1500ms limit  
Memory Usage	~1.2GB	Efficient for modern laptops  
##  Installation & Setup
Prerequisites
Python 3.10+
FFmpeg: Must be installed and added to your system PATH.  
Windows:
```
winget install Gyan.FFmpeg
```
Mac: 
```
brew install ffmpeg
```
Linux: 
```
sudo apt install ffmpeg
```
### Steps
Clone the repository:
```
git clone https://github.com/yourusername/SpeechEngine.git
cd SpeechEngine
```
Create a Virtual Environment:
```
python -m venv venv
```
Windows:
```
.\venv\Scripts\activate
```
Mac/Linux:
```
source venv/bin/activate
```
Install Dependencies:
```
pip install fastapi uvicorn[standard] python-multipart faster-whisper transformers sentencepiece torch psutil
```
Run the Application:
```
python app.py
```
Access the UI:

Open your browser and go to 
```
http://127.0.0.1:7000
```
## Usage Guide (Voice Commands)
The engine listens to context. Try these commands:  
1. Email Mode
```
Trigger: "Draft email to [Name]..." or "Write an email to [Name]..."
```
Example Voice Input:
```
"Draft email to Sarah saying that good morning I will be sending the report by friday thanks"
```
Output:
```
Subject: [Auto-Detected Context if available]

Good morning Sarah,

I will be sending the report by Friday.

Thanks,
```
2.  Checklist Mode (Array Split)
```
Trigger: "Checklist of [Item] and [Item]..."
```
Example Voice Input:
```
"Make a checklist of apples and bananas and milk and bread"
```
Output:
```
Here is the checklist:
• Apples
• Bananas
• Milk
• Bread
```
3.  Standard Bullet Points
```
Trigger: "Bullet point", "Next point", "Number one".
```
Example Voice Input:
```
"The plan is bullet point start early bullet point work hard bullet point finish fast"
```
Output:
```
The plan is:
• Start early
• Work hard
• Finish fast
```
Tech Stack
Backend: FastAPI (Python)
Speech-to-Text: Faster-Whisper (CTranslate2)
Grammar Correction: Vennify/T5-Base-Grammar
Audio Processing: FFmpeg (In-Memory Piping)

##  Project Structure

A clean, modular architecture designed for maintainability.

```
neural-dictate/
│
├── app.py                 # Main Application Entry Point (FastAPI)
├── requirements.txt       # Python Dependencies
│
├── core/                  # Core Processing Logic
│   ├── __init__.py
│   ├── asr_engine.py      # Whisper Implementation (STT)
│   ├── grammar_model.py   # T5 Model Wrapper (Grammar)
│   └── text_engine.py     # Regex Logic (Cleaning & Formatting)
│
├── static/                # Static Assets (CSS/JS if separated)
└── templates/
    └── index.html         # The Frontend Interface
```
Advanced Configuration
You can tweak performance settings in services/asr_engine.py and templates/index.html.
1. Adjusting Silence Detection (Frontend)
In index.html, modify these constants to change how aggressive the auto-cutting is:
```
const SILENCE_MS = 1000;  // Time to wait before cutting (in ms)
const VOL_THRESHOLD = 2;  // Volume sensitivity (Lower = more sensitive)
```
2. Changing Model Size (Backend)
In app.py, you can swap the model for accuracy vs. speed trade-offs:
code
Python
# Options: tiny.en, base.en, small.en, medium.en
asr_engine = FastWhisperEngine(model_size="base.en")
Note: base.en is the recommended balance for CPU inference.
🐛 Troubleshooting
Q: The latency is high (>2000ms).
Fix: Ensure you are running on a machine with AVX2 support. The first run is always slower due to model loading. Subsequent requests will be fast.
Q: It's cutting me off while speaking.
Fix: Increase SILENCE_MS in index.html to 1500 or 2000.
Q: "Error parsing Opus packet" or Audio issues.
Fix: Ensure FFmpeg is correctly installed and accessible via your terminal. Run ffmpeg -version to verify.
📜 License
This project is licensed under the MIT License. You are free to use, modify, and distribute this software.
