import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from context.session_manager import get_session_by_thread

class JoinVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ensure bot has voice_sessions mapping
        if not hasattr(self.bot, "voice_sessions"):
            self.bot.voice_sessions = {}  # map: str(thread_id) -> {'vc': VoiceClient, 'channel_id': int}

    @app_commands.command(
        name="join_vc",
        description="このセッションの読み上げを開始するため、あなたの現在のボイスチャンネルにBOTを接続します"
    )
    async def join_vc(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # 実行はスレッド内で行うべき
        channel = interaction.channel
        if not isinstance(channel, (discord.Thread, discord.TextChannel)):
            return await interaction.followup.send("このコマンドはテキストスレッド／チャンネル内で実行してください。", ephemeral=True)

        # ユーザーが VC に参加しているか
        voice_state = interaction.user.voice
        if not voice_state or not voice_state.channel:
            return await interaction.followup.send("ボイスチャンネルに接続した状態で実行してください。", ephemeral=True)

        voice_channel = voice_state.channel

        # session 確認
        session = get_session_by_thread(channel.id)
        if not session:
            return await interaction.followup.send("このスレッドにはセッションが登録されていません。", ephemeral=True)

        # Bot を VC に接続（既に接続済みなら reuse）
        existing_vc = None
        for pc in self.bot.voice_clients:
            if pc.guild.id == voice_channel.guild.id and pc.channel.id == voice_channel.id:
                existing_vc = pc
                break

        try:
            if existing_vc is None:
                vc = await voice_channel.connect()
            else:
                vc = existing_vc
        except Exception as e:
            return await interaction.followup.send(f"ボイスチャンネルへの接続に失敗しました: {e}", ephemeral=True)

        # マッピングを保存
        if not hasattr(self.bot, "voice_sessions"):
            self.bot.voice_sessions = {}
        self.bot.voice_sessions[str(channel.id)] = {"vc": vc, "channel_id": voice_channel.id}

        await interaction.followup.send(f"ボイスチャンネル **{voice_channel.name}** に接続しました。A.L.L.I.C.A. の発言を読み上げます。", ephemeral=True)

    async def cog_unload(self):
        # Cog がアンロードされたら接続も切る（保険）
        if hasattr(self.bot, "voice_sessions"):
            for info in list(self.bot.voice_sessions.values()):
                vc = info.get("vc")
                try:
                    if vc and vc.is_connected():
                        coro = vc.disconnect()
                        asyncio.ensure_future(coro)
                except Exception:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(JoinVC(bot))