import discord
import json
from discord.ext import commands

from context.session_manager import get_session_by_thread, update_session_model
from context.memory_utils import load_summary, save_summary, load_memory, save_memory
from gemini.client import call_gemini, strip_code_block

class MentionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 無視条件：Bot自身、他のBot、メンションなし、DM
        if message.author.bot or message.guild is None:
            return

        if self.bot.user not in message.mentions:
            return
        
        print("\nMention catched.\n")

        # メンションを除いた本文（@Bot名 を除去）
        mention_text = message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
        if not mention_text:
            return await message.reply("にゃ？ 呼んだだけで満足ですか、ご主人？", mention_author=False)

        # スレッド or チャンネルIDからセッション取得
        thread_id = message.channel.id
        user_id = str(message.author.id)

        session = get_session_by_thread(thread_id)
        if not session:
            print("\nerr: このスレッドに対応するセッションが存在しません。")
            return await message.reply("このスレッドに対応するセッションが見つかりませんにゃ。", mention_author=False)

        model_name = session["model"]
        session_id = session["session_id"]
        topic      = session["topic"]

        # 文脈と記憶の読み込み
        history_text = load_summary(user_id, session_id) or "（履歴なし）"
        memory_text  = load_memory(user_id) or "なし"

        # プロンプトテンプレート読み込み
        with open("prompts/talk.txt", encoding="utf-8") as f:
            prompt_template = f.read()

        prompt = (
            prompt_template
            .replace("{history}", history_text)
            .replace("{memory}", memory_text)
            .replace("{input}", mention_text)
        )

        # Gemini 呼び出し
        raw = call_gemini(prompt, model=model_name)
        cleaned_raw = strip_code_block(raw)

        try:
            output = json.loads(cleaned_raw)
        except json.JSONDecodeError:
            print("text = \n"+raw+"\nerr: Geminiの出力が正しいJSONではありませんでした。")
            return await message.reply("ふにゃっ！？……ちょ、ちょっとお待ちください、ご主人っ！\n" +
                "アリカの回路がちょっぴり混線して、うまくお返事がまとめられなかったみたいです……（ぐぬぬ）。\n" +
                "もう一度話しかけてもらえたら、今度こそきちんとお答えしますにゃ！", mention_author=False)

        reply   = output.get("reply", "")
        summary = output.get("summary", "")
        new_mem = output.get("long_term_memory", "なし")

        # 要約と記憶を更新
        save_summary(user_id, session_id, summary)
        save_memory(user_id, new_mem)

        # 返信を送信（Embed 形式）
        embed = discord.Embed(
            title=f"A.L.L.I.C.A. — {topic}",
            description=reply,
            color=0x7AAEDC
        )
        await message.channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MentionListener(bot))
