import json
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAP_1_FILE = "question_bank/chap_1.json"
USER_JSON_PATH = os.path.join(BASE_DIR, "../account_management/database/user.json")
USER_HISTORY_DIR = os.path.join(BASE_DIR, "../account_management/database/user_history")
QUESTION_BANK_PATH = "question_bank/"
def load_questions(chapter):
    """根據章節載入題目"""
    if chapter == "chap1":
        try:
            with open(CHAP_1_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    return []

def load_accounts():
    """載入所有帳號資料"""
    try:
        with open(USER_JSON_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_accounts(accounts):
    
    os.makedirs(os.path.dirname(USER_JSON_PATH), exist_ok=True)  # 確保目錄存在
    with open(USER_JSON_PATH, 'w', encoding='utf-8') as file:
        json.dump(accounts, file, ensure_ascii=False, indent=4)

def save_user_history(user_id, chapter, user_answers, status_check):
    """將使用者測驗紀錄儲存到以學號命名的 json 檔案，並分配索引編號"""
    os.makedirs(USER_HISTORY_DIR, exist_ok=True)
    user_history_path = os.path.join(USER_HISTORY_DIR, f"{user_id}.json")

    try:
        with open(user_history_path, 'r', encoding='utf-8') as file:
            history_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history_data = []

    # 新的紀錄索引基於現有紀錄數量
    record_index = len(history_data)
    new_record = {
        "record_index": record_index,
        "user_id": user_id,
        "chapter": chapter,
        "user_answers": user_answers,
        "status_check": status_check
    }

    # 將新紀錄加入到 user_history.json
    history_data.append(new_record)

    # 將更新的紀錄保存回檔案
    with open(user_history_path, 'w', encoding='utf-8') as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)
