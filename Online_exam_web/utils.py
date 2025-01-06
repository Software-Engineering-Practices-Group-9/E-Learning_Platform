import json

CHAP_1_FILE = "question_bank/chap_1.json"

def load_questions(chapter):
    """根據章節載入題目"""
    if chapter == "chap1":
        try:
            with open(CHAP_1_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    return []
