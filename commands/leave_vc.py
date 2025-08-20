import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class LeaveVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "voice_sessions"):
            self.bot.voice_sessions = {}

    @app_commands.command(
        name="leave_vc",
        description="このセッションの読み上げを停止し、ボイスチャンネルから切断します"
    )
    async def leave_vc(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        channel = interaction.channel
        session_map = getattr(self.bot, "voice_sessions", {})

        info = session_map.get(str(channel.id))
        if not info:
            return await interaction.followup.send("このスレッドは現在読み上げ対象になっていません。", ephemeral=True)

        vc = info.get("vc")
        try:
            if vc and vc.is_connected():
                await vc.disconnect()
        except Exception as e:
            print(f"[leave_vc] disconnect error: {e}")

        # マッピングを削除
        session_map.pop(str(channel.id), None)
        await interaction.followup.send("読み上げを停止し、ボイスチャネルから切断しました。", ephemeral=True)

    async def cog_unload(self):
        # Cog unload 保険
        if hasattr(self.bot, "voice_sessions"):
            for info in list(self.bot.voice_sessions.values()):
                vc = info.get("vc")
                try:
                    if vc and vc.is_connected():
                        asyncio.ensure_future(vc.disconnect())
                except Exception:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveVC(bot))