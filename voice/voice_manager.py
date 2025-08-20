import os
import tempfile
import asyncio
import requests
from typing import Optional

import discord
from discord import FFmpegPCMAudio

# VOICEVOX API のベースURL(ローカルでDocker起動)
VOICEVOX_API_BASE = os.getenv("VOICEVOX_API_BASE", "http://127.0.0.1:50021")
# DEFAULT_SPEAKER = int(os.getenv("VOICEVOX_SPEAKER", "61"))
DEFAULT_SPEAKER = int(os.getenv("VOICEVOX_SPEAKER", "91"))

# 内部マッピング: thread_id -> voice client object
# 実運用ではbotインスタンスに収納して管理しても良い
# ただしここでは関数呼び出し時にbotを渡してbot.voice_sessionsを使う想定
# bot.voice_sessions = { thread_id: {'vc': VoiceClient, 'channel_id': int} }

async def synthesize_voice(text: str, speaker: int = DEFAULT_SPEAKER) -> str:
    """
    VOICEVOX の HTTP API を使って合成音声を取得し、一時ファイルとして保存。
    return: 音声ファイルのパス(wav)
    """
    # audio_queryを呼ぶ
    q_url = f"{VOICEVOX_API_BASE}/audio_query"
    synth_url = f"{VOICEVOX_API_BASE}/synthesis"

    params = {"text": text, "speaker": speaker}
    resp = requests.post(q_url, params=params)
    resp.raise_for_status()
    query_json = resp.json()

    # synthesisを呼ぶ(query_jsonをJSON本文として送る)
    headers = {"Content-Type": "application/json"}
    resp2 = requests.post(synth_url, params={"speaker": speaker}, headers=headers, json=query_json, stream=True)
    resp2.raise_for_status()

    # 一時ファイルに保存(wav)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmp.name, "wb") as f:
        for chunk in resp2.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return tmp.name


async def play_audio_file(voice_client: discord.VoiceClient, file_path: str):
    """
    Discordのvoice_clientで再生。既に再生中ならキューを止めて上書き再生。
    """
    if not voice_client or not voice_client.is_connected():
        raise RuntimeError("Voice client is not connected")

    # 再生中なら停止して上書き
    if voice_client.is_playing():
        voice_client.stop()

    # FFmpegPCMAudio を使って再生
    source = FFmpegPCMAudio(file_path)
    voice_client.play(source)

    # 再生終了まで待機(オプション)
    while voice_client.is_playing():
        await asyncio.sleep(0.1)

    # 再生後ファイルを削除
    try:
        os.remove(file_path)
    except Exception:
        pass


async def synthesize_and_play(bot: discord.Client, thread_id: int, text: str, speaker: int = DEFAULT_SPEAKER):
    """
    高レベルAPI: botのthread_idから対応するVoiceClientを取り出して
    VOICEVOXで合成し、再生する。
    """
    # botには bot.voice_sessions : dict を用意しておくこと
    sess_map = getattr(bot, "voice_sessions", None)
    if not sess_map:
        raise RuntimeError("voice_sessions map is not initialized on bot")

    info = sess_map.get(str(thread_id)) or sess_map.get(thread_id)
    if not info:
        raise RuntimeError("No active voice session for this thread")

    voice_client: discord.VoiceClient = info.get("vc")
    if not voice_client or not voice_client.is_connected():
        raise RuntimeError("Voice client not connected")

    # IO / HTTP はブロッキングなのでexecutorで実行
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, lambda: asyncio.run_coroutine_threadsafe(synthesize_voice_sync(text, speaker), loop).result())
    # The above is a bit awkward because requests is blocking. Instead implement a small sync wrapper below.


# Helper sync wrapper to use with run_in_executor
def synthesize_voice_sync(text: str, speaker: int = DEFAULT_SPEAKER) -> str:
    """
    同期関数バージョン。内部でrequestsを使うためrun_in_executor用。
    """
    q_url = f"{VOICEVOX_API_BASE}/audio_query"
    synth_url = f"{VOICEVOX_API_BASE}/synthesis"

    params = {"text": text, "speaker": speaker}
    resp = requests.post(q_url, params=params, timeout=10)
    resp.raise_for_status()
    query_json = resp.json()

    headers = {"Content-Type": "application/json"}
    resp2 = requests.post(synth_url, params={"speaker": speaker}, headers=headers, json=query_json, stream=True, timeout=30)
    resp2.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmp.name, "wb") as f:
        for chunk in resp2.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return tmp.name


async def play_text_for_session(bot: discord.Client, thread_id: int, text: str, speaker: int = DEFAULT_SPEAKER):
    """
    外部から呼ぶ高レベル関数。
    - thread_idに紐づくvoice clientが存在すれば音声合成 → 再生を行う。
    """
    sess_map = getattr(bot, "voice_sessions", None)
    if not sess_map:
        raise RuntimeError("voice_sessions map is not initialized on bot")

    session_info = sess_map.get(str(thread_id)) or sess_map.get(thread_id)
    if not session_info:
        # そのセッションに対してjoinされていない
        return

    voice_client: Optional[discord.VoiceClient] = session_info.get("vc")
    if not voice_client or not voice_client.is_connected():
        return

    # synthesize(ブロッキングHTTP)をexecutorで実行
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, synthesize_voice_sync, text, speaker)

    try:
        await play_audio_file(voice_client, file_path)
    except Exception as e:
        print(f"[voice_manager] playback error: {e}")