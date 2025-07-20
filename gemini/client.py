import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_model(model_name: str):
    return genai.GenerativeModel(model_name)

def call_gemini(prompt: str, model: str = "gemini-2.0-flash-lite-001") -> str:
    """
    指定されたモデルでプロンプトを実行し、テキスト応答を返す。

    Args:
        prompt (str): ユーザーからの入力またはコンテキストを含むプロンプト。
        model (str): 使用するGeminiモデル名（例: "gemini-pro"）。

    Returns:
        str: Geminiからの応答テキスト。
    """
    model = get_model(model)
    response = model.generate_content(prompt)

    if hasattr(response, "text"):
        return response.text.strip()
    else:
        return "（Geminiから有効な応答が得られませんでした）"
    
import re

def strip_code_block(raw: str) -> str:
    """
    Geminiの返答の前後にあるコードブロック ```～``` を取り除く。
    例えば ```json ～ ``` のような形式を含めて対応する。
    """

    # 両端に ``` があるかチェック（``` で始まり、``` で終わる）
    pattern = r"^\s*```(?:\w+)?\n([\s\S]+?)\n\s*```$"
    match = re.match(pattern, raw.strip())

    if match:
        return match.group(1).strip()  # コード本体のみ返す
    return raw.strip()  # なければそのまま返す
