import os
import json

# ディレクトリ定義
SESSION_DIR = os.path.join("data", "session")
MEMORY_DIR = os.path.join("data", "memory")
SUMMARY_LIMIT = 10


def ensure_dir(path: str):
    """
    指定されたパスのディレクトリを作成
    """
    os.makedirs(path, exist_ok=True)


def get_session_file(user_id: str, session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"{user_id}_{session_id}.json")


def get_memory_file(user_id: str) -> str:
    return os.path.join(MEMORY_DIR, f"{user_id}.json")


def save_summary(user_id: str, session_id: str, summary_text: str):
    """
    要約履歴を追加保存。最大SUMMARY_LIMIT件まで保持。
    """
    ensure_dir(SESSION_DIR)
    path = get_session_file(user_id, session_id)
    # 読み込み
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    history.append(summary_text)
    # 件数制限
    history = history[-SUMMARY_LIMIT:]

    # 保存
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_summary(user_id: str, session_id: str) -> str:
    """
    セッションの要約履歴を結合して返す
    """
    path = get_session_file(user_id, session_id)
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        history = json.load(f)
    return "\n".join(history)


def save_memory(user_id: str, memory_text: str):
    """
    長期記憶を上書き保存
    """
    ensure_dir(MEMORY_DIR)
    path = get_memory_file(user_id)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(memory_text.strip())


def load_memory(user_id: str) -> str:
    """
    ユーザーの長期記憶を読み込んで返す
    """
    path = get_memory_file(user_id)
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()