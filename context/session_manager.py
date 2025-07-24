import os
import json

# ファイルパス定義
SESSION_FILE = os.path.join("data/session", "session_threads.json")


def ensure_dir():
    """
    dataディレクトリとSESSION_FILEの保存先ディレクトリを作成
    """
    dir_path = os.path.dirname(SESSION_FILE)
    os.makedirs(dir_path, exist_ok=True)


def create_session(thread_id: int, user_id: str, topic: str, model: str, session_id: str):
    """
    新しいセッションエントリを作成し、session_threads.jsonに保存する

    :param thread_id: DiscordスレッドのID
    :param user_id: ユーザーID（文字列）
    :param topic: 主題タグ
    :param model: 使用モデル名
    :param session_id: 内部管理用セッションID
    """
    ensure_dir()
    # 既存セッション読み込み
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
    else:
        sessions = {}

    # 追加・上書き
    sessions[str(thread_id)] = {
        "session_id": session_id,
        "user_id": user_id,
        "topic": topic,
        "model": model
    }

    # 保存
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def get_session_by_thread(thread_id: int):
    """
    スレッドIDからセッション情報を取得

    :param thread_id: DiscordスレッドのID
    :return: セッション情報の辞書 または None
    """
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, 'r', encoding='utf-8') as f:
        sessions = json.load(f)
    return sessions.get(str(thread_id))

def update_session_model(thread_id: int, new_model: str):
    """
    モデル変更時にdata/session/session_threads.json内のmodelフィールドを更新
    """
    ensure_dir()
    with open(SESSION_FILE, 'r', encoding='utf-8') as f:
        sessions = json.load(f)
    if str(thread_id) in sessions:
        sessions[str(thread_id)]["model"] = new_model
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)

def delete_session(thread_id: int):
    """
    スレッド ID に紐づくセッションを session_threads.json から削除する。
    """
    import json
    import os

    path = os.path.join("data", "session", "session_threads.json")
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    str_id = str(thread_id)
    if str_id in data:
        del data[str_id]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
