import os
import uuid
import json
import discord
from discord import app_commands
from discord.ext import commands
from gemini.client import call_gemini, strip_code_block
from context.session_manager import create_session
from context.memory_utils import save_summary, save_memory

class NewSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="newsession",
        description="新規セッション（文脈付き会話）を開始します"
    )
    @app_commands.describe(
        message="会話の最初の一言（自由記述）",
        model="使用する Gemini モデルを選択"
    )
    @app_commands.choices(
        model=[
            app_commands.Choice(name="2.5_flash",           value="gemini-2.5-flash"),
            app_commands.Choice(name="2.5_flash-lite",      value="gemini-2.5-flash-lite-preview-06-17"),
            app_commands.Choice(name="2.0_flash",           value="gemini-2.0-flash-001"),
            app_commands.Choice(name="2.0_flash-lite",      value="gemini-2.0-flash-lite-001"),
        ]
    )
    async def newsession(
        self,
        interaction: discord.Interaction,
        message: str,
        model: app_commands.Choice[str]  # Choice 型で受け取る
    ):
        await interaction.response.defer(thinking=True)

        owner_id = str(interaction.user.id)
        # model.value にモデル名文字列が入る
        model_name = model.value if model else "gemini-2.0-flash-lite-001"

        # 長期記憶の読み込み
        mem_path = os.path.join("data", "memory", f"{owner_id}.json")
        user_memory = open(mem_path, encoding="utf-8").read().strip() if os.path.exists(mem_path) else "なし"

        # プロンプト生成
        prompt = open("prompts/newsession.txt", encoding="utf-8").read()
        prompt = prompt.replace("{memory}", user_memory).replace("{input}", message).replace("{user}", interaction.user.display_name)

        # Gemini 呼び出し
        raw = call_gemini(prompt, model=model_name)
        cleaned_raw = strip_code_block(raw)
        try:
            output = json.loads(cleaned_raw)
        except json.JSONDecodeError:
            print("text = \n"+raw+"\n")
            return await interaction.followup.send("err: Gemini の出力が JSON ではありませんでした。", ephemeral=True)

        topic    = output.get("topic", "未分類")
        reply    = output.get("reply", "")
        summary  = output.get("summary", "")
        new_mem  = output.get("long_term_memory", "なし")

        # スレッド作成 & 招待
        thread = await interaction.channel.create_thread(
            name=topic,
            type=discord.ChannelType.private_thread,
            invitable=False
        )
        await thread.add_user(interaction.user)

        # セッション登録
        session_id = str(uuid.uuid4())
        create_session(thread.id, owner_id, topic, model_name, session_id)

        # 要約・記憶更新
        save_summary(owner_id, session_id, summary)
        save_memory(owner_id, new_mem)

        # ユーザーからのメッセージをログとしてスレッドに表示
        await thread.send(f">>> **{interaction.user.display_name}**: {message}")

        # スレッド内へ返答
        await thread.send(reply)

        # ユーザーへの通知
        await interaction.followup.send(
            f"新規セッションを開始しました。\n"
            # f"`Session ID:` {session_id}\n"
            f"`Topic:` {topic}\n"
            f"`Thread:` {thread.mention}",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(NewSession(bot))