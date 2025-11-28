from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import torch
import os

class GrammarBrain:
    def __init__(self):
        print("[INIT] Loading Grammar Model...")
        os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"
        self.model_name = "vennify/t5-base-grammar-correction"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model = torch.quantization.quantize_dynamic(self.model, {torch.nn.Linear}, dtype=torch.qint8)
        except:
            self.model = None

    def fix(self, text):
        start = time.time()
        if not text or len(text.split()) < 3: 
            return (text[0].upper() + text[1:]) if text else "", (time.time() - start) * 1000
        try:
            input_ids = self.tokenizer(f"grammar: {text}", return_tensors="pt").input_ids
            max_len = int(len(input_ids[0]) * 1.2) + 4
            outputs = self.model.generate(input_ids, max_length=max_len, num_beams=1, early_stopping=True)
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return corrected, (time.time() - start) * 1000
        except:
            return text, (time.time() - start) * 1000