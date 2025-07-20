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
bot = commands.Bot(command_prefix="/", intents=intents)
bot.config = config
bot.toggle_enabled = True  # 初期状態で有効

# コマンド読み込み
from commands.ask import setup as setup_ask
from commands.toggle import setup as setup_toggle
from commands.newsession import setup as setup_newsession
from commands.talk import setup as setup_talk

@bot.event
async def on_ready():
    # Cogの登録
    setup_ask(bot)
    setup_toggle(bot)
    await setup_newsession(bot)
    await setup_talk(bot)

    # コマンド同期
    #GUILD = discord.Object(id=761990190637121537)
    #await bot.tree.sync(guild=GUILD)
    await bot.tree.sync()
    print(f"✅ Bot is ready. Logged in as {bot.user}")

bot.run(DISCORD_TOKEN)