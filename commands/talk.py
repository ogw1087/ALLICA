import discord
from discord import app_commands
from discord.ext import commands
import json

from context.session_manager import get_session_by_thread, update_session_model
from context.memory_utils import load_summary, save_summary, load_memory, save_memory
from gemini.client import call_gemini, strip_code_block

class Talk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="talk",
        description="アリカと会話します(セッション内限定)"
    )
    @app_commands.describe(
        message="話しかける内容を入力してください",
        model="このセッションで使うモデルを変更できます（省略時はセッション開始時のモデルを使用）"
    )
    @app_commands.choices(
        model=[
            app_commands.Choice(name="2.5_flash",           value="gemini-2.5-flash"),
            app_commands.Choice(name="2.5_flash-lite",      value="gemini-2.5-flash-lite-preview-06-17"),
            app_commands.Choice(name="2.0_flash",           value="gemini-2.0-flash-001"),
            app_commands.Choice(name="2.0_flash-lite",      value="gemini-2.0-flash-lite-001"),
        ]
    )
    async def talk(
        self,
        interaction: discord.Interaction,
        message: str,
        model: app_commands.Choice[str] = None
    ):
        await interaction.response.defer(thinking=True)

        thread_id = interaction.channel.id
        user_id = str(interaction.user.id)

        # セッション取得
        session = get_session_by_thread(thread_id)
        if not session:
            return await interaction.followup.send(
                "err: このスレッドに対応するセッションが存在しません。",
                ephemeral=True
            )

        # モデルの選択 or セッション既定
        model_name = model.value if model else session["model"]
        # 指定があった場合はセッション情報も更新しておく
        if model and model.value != session["model"]:
            update_session_model(thread_id, model.value)

        session_id = session["session_id"]
        topic      = session["topic"]

        # 文脈（要約履歴）と長期記憶 をロード
        history_text = load_summary(user_id, session_id) or "（履歴なし）"
        memory_text  = load_memory(user_id) or "なし"

        # プロンプトテンプレート読み込み
        prompt_template = open("prompts/talk.txt", encoding="utf-8").read()
        prompt = (
            prompt_template
            .replace("{history}", history_text)
            .replace("{memory}", memory_text)
            .replace("{input}", message)
        )

        # Gemini呼び出し
        raw = call_gemini(prompt, model=model_name)
        cleaned_raw = strip_code_block(raw)
        try:
            output = json.loads(cleaned_raw)
        except json.JSONDecodeError:
            print("text = \n"+raw+"\n")
            return await interaction.followup.send(
                "err: Geminiの出力が正しいJSONではありませんでした。",
                ephemeral=True
            )

        # JSONから抽出
        reply   = output.get("reply", "")
        summary = output.get("summary", "")
        new_mem = output.get("long_term_memory", "なし")

        # 要約と記憶を更新
        save_summary(user_id, session_id, summary)
        save_memory(user_id, new_mem)

        # 返答を埋め込みでスレッドに送信
        embed = discord.Embed(
            title=f"A.L.L.I.C.A. — {topic}",
            description=reply,
            color=0x7AAEDC
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Talk(bot))