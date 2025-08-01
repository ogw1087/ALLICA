import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 設定ファイルの読み込み
with open("data/config.json", encoding="utf-8") as f:
    config = json.load(f)

# Bot 初期化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
bot.config = config
bot.toggle_enabled = True  # 初期状態で有効

# コマンド読み込み
from commands.ask import setup as setup_ask
from commands.toggle import setup as setup_toggle
from commands.newsession import setup as setup_newsession
from commands.talk import setup as setup_talk
from commands.change_model import setup as setup_change_model
from commands.delete_session import setup as setup_delete_session

# リスナー読み込み
from listeners.mention_listener import setup as setup_mention_listener

@bot.event
async def on_ready():
    # Cogの登録
    setup_ask(bot)
    setup_toggle(bot)
    await setup_newsession(bot)
    await setup_talk(bot)
    await setup_mention_listener(bot)
    await setup_change_model(bot)
    await setup_delete_session(bot)

    await bot.tree.sync()
    print(f"✅ Bot is ready. Logged in as {bot.user}")

bot.run(DISCORD_TOKEN)