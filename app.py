import os
import time
import shutil
import subprocess
import uuid
import io

os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"
os.environ["CURL_CA_BUNDLE"] = ""

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from services.asr_engine import FastWhisperEngine
from services.grammar_model import GrammarBrain
from services.text_engine import LogicEngine

app = FastAPI(title="Dictation Pro Final")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

print("\n[SYSTEM] Loading Pipeline...")
asr_engine = FastWhisperEngine(model_size="base.en") 
grammar_engine = GrammarBrain()
logic_engine = LogicEngine()
print("[SYSTEM] Ready.\n")

def convert_and_read_memory(input_path):
    try:
        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", "-"
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        audio_data, _ = process.communicate()
        return io.BytesIO(audio_data) 
    except:
        return None

@app.post("/process")
async def process(file: UploadFile = File(...), tone: str = Form("neutral")):
    start_time = time.time()
    uid = uuid.uuid4().hex
    raw_file = f"temp_{uid}.webm"
    
    try:
        with open(raw_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        audio_memory = convert_and_read_memory(raw_file)
        if not audio_memory: return {"status": "error"}
            
        # 1. ASR
        raw_text, lat_asr = asr_engine.transcribe(audio_memory)
        if not raw_text or len(raw_text) < 2: return {"status": "empty"}

        # 2. CLEAN
        clean_text = logic_engine.pre_process(raw_text)
        
        # 3. GRAMMAR
        gram_text, lat_grammar = grammar_engine.fix(clean_text)
        
        # 4. FORMAT (Updated logic)
        final_text, lat_logic = logic_engine.post_process(gram_text, tone)
        
        total_ms = (time.time() - start_time) * 1000

        return {
            "status": "success",
            "raw": raw_text,
            "final": final_text,
            "metrics": {
                "asr": round(lat_asr, 1),
                "logic": round(lat_logic, 1),
                "grammar": round(lat_grammar, 1),
                "total": int(total_ms)
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}
    finally:
        if os.path.exists(raw_file): 
            try: os.remove(raw_file)
            except: pass

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7500)