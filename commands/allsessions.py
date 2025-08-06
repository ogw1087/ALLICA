import discord
from discord import app_commands
from discord.ext import commands
from context.session_manager import get_sessions_by_user

class AllSessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="allsessions",
        description="あなたが参加中のセッション一覧を表示します"
    )
    async def allsessions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)
        sessions = get_sessions_by_user(user_id)

        if not sessions:
            return await interaction.followup.send("現在参加中のセッションはありません。", ephemeral=True)

        embed = discord.Embed(
            title="あなたの参加セッション",
            color=0x81D4FA
        )
        for s in sessions:
            embed.add_field(
                name=s["topic"],
                value=(
                    f"スレッド: <#{s['thread_id']}>\n"
                    f"モデル: `{s['model']}`"
                ),
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AllSessions(bot))