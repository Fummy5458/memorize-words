# -*- coding: utf-8 -*-
import json
import os

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")

def save_progress(word_file, remaining_words, current_total, current_correct):
    data = {
        "last_word_file": word_file,
        "remaining_words": remaining_words,
        "current_total": current_total,
        "current_correct": current_correct
    }
    if len(remaining_words) == 0:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        return
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def has_valid_progress():
    data = load_progress()
    if not data:
        return False
    remaining = data.get("remaining_words", [])
    return len(remaining) > 0

def clear_current_progress(word_file):
    data = load_progress()
    if data and data.get("last_word_file") == word_file:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)

def clear_all_progress():
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)