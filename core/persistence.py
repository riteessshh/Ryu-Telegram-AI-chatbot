import os
import json
from core.config import MODEL_PREFS_FILE

def load_model_prefs():
    if os.path.exists(MODEL_PREFS_FILE):
        with open(MODEL_PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_model_prefs(prefs):
    with open(MODEL_PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)
