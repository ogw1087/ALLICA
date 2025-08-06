import discord
from discord import app_commands
from discord.ext import commands
from context.session_manager import get_session_by_thread, add_participant

class ShareSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="share_session",
        description="他のユーザーをこのセッションに招待します"
    )
    @app_commands.describe(user="招待するユーザー")
    async def share_session(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)

        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            return await interaction.followup.send("このコマンドはスレッド内でのみ使用可能です。", ephemeral=True)

        session = get_session_by_thread(thread.id)
        if not session:
            return await interaction.followup.send("このスレッドにはセッションが存在しません。", ephemeral=True)

        await thread.add_user(user)
        add_participant(thread.id, str(user.id))

        await interaction.followup.send(f"{user.mention} をこのセッションに招待しました。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ShareSession(bot))