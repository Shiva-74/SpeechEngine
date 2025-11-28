import time
import os
from faster_whisper import WhisperModel

class FastWhisperEngine:
    def __init__(self, model_size="base.en"):
        print(f"[INIT] Loading Whisper '{model_size}'...")
        os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=4)
        print("[INIT] Whisper Ready.")

    def transcribe(self, audio_data):
        start = time.time()
        try:
            segments, _ = self.model.transcribe(
                audio_data,
                beam_size=1,
                language="en",
                condition_on_previous_text=False,
                vad_filter=False 
            )
            text = " ".join([s.text for s in segments]).strip()
            return text, (time.time() - start) * 1000
        except:
            return "", 0