# commands/change_model.py

import discord
from discord import app_commands
from discord.ext import commands

from context.session_manager import get_session_by_thread, update_session_model

class ChangeModel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="change_model",
        description="このセッションで使用する Gemini モデルを変更します"
    )
    @app_commands.describe(
        model="新しく使用する Gemini モデルを選択してください"
    )
    @app_commands.choices(
        model=[
            app_commands.Choice(name="2.5_flash",           value="gemini-2.5-flash"),
            app_commands.Choice(name="2.5_flash-lite",      value="gemini-2.5-flash-lite-preview-06-17"),
            app_commands.Choice(name="2.0_flash",           value="gemini-2.0-flash-001"),
            app_commands.Choice(name="2.0_flash-lite",      value="gemini-2.0-flash-lite-001"),
        ]
    )
    async def change_model(
        self,
        interaction: discord.Interaction,
        model: app_commands.Choice[str]
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        thread_id = interaction.channel.id
        session = get_session_by_thread(thread_id)

        if not session:
            return await interaction.followup.send(
                "このスレッドに対応するセッションが存在しません。",
                ephemeral=True
            )

        # セッションの所有者確認
        if session["user_id"] != str(interaction.user.id):
            return await interaction.followup.send(
                "このセッションのモデルを変更できるのは、セッション作成者のみです。",
                ephemeral=True
            )

        old_model = session["model"]
        new_model = model.value

        if old_model == new_model:
            return await interaction.followup.send(
                f"既に `{new_model}` を使用しています。",
                ephemeral=True
            )

        update_session_model(thread_id, new_model)

        await interaction.followup.send(
            f"このセッションの使用モデルを `{old_model}` から `{new_model}` に変更しました。",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ChangeModel(bot))
