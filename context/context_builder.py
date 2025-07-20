import os
import json

HISTORY_DIR = "data/history"
MEMORY_DIR = "data/memory"
DEFAULT_PROMPT_PATH = "prompts/ask.txt"

def load_json_safe(path: str) -> list | dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return [] if path.endswith(".json") else {}

def save_history(user_id: str, tag: str, user_msg: str, bot_msg: str):
    # 履歴を保存（最大N件
    filename = f"{user_id}_{tag}.json"
    path = os.path.join(HISTORY_DIR, filename)
    history = load_json_safe(path)
    history.append({"user": user_msg, "bot": bot_msg})
    history = history[-10:]  # 上限件数
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_context_for_session(user_id: str, tag: str) -> dict:
    # セッションに基づいた履歴・記憶・テンプレートの読み込み
    history_path = os.path.join(HISTORY_DIR, f"{user_id}_{tag}.json")
    memory_path = os.path.join(MEMORY_DIR, f"{user_id}_{tag}.json")

    history_data = load_json_safe(history_path)
    memory_data = load_json_safe(memory_path)

    history_text = "\n".join([f"{h['user']}\n{h['bot']}" for h in history_data])
    memory_text = "\n".join(memory_data if isinstance(memory_data, list) else [])

    with open(DEFAULT_PROMPT_PATH, encoding="utf-8") as f:
        prompt_template = f.read()

    return {
        "prompt_template": prompt_template,
        "recent_history": history_text,
        "memory": memory_text
    }
