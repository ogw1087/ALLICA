# commands/delete_session.py

import discord
from discord import app_commands
from discord.ext import commands
import os
import shutil

from context.session_manager import get_session_by_thread, delete_session

class DeleteSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="delete_session",
        description="現在のスレッドのセッションを削除します（セッション開始ユーザー限定）"
    )
    async def delete_session(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            return await interaction.followup.send(
                "このコマンドはスレッド内でのみ使用可能です。",
                ephemeral=True
            )

        session = get_session_by_thread(thread.id)
        if not session:
            return await interaction.followup.send(
                "このスレッドにはセッションが存在しません。",
                ephemeral=True
            )

        # セッション作成者のみが削除可能
        user_id = str(interaction.user.id)
        if session["user_id"] != user_id:
            return await interaction.followup.send(
                "セッションを削除できるのは開始ユーザーのみです。",
                ephemeral=True
            )

        session_id = session["session_id"]

        # セッションファイルを削除
        delete_session(thread.id)

        # 文脈・履歴ファイルを削除
        try:
            summary_path = os.path.join("data", "context", f"{user_id}_{session_id}.txt")
            if os.path.exists(summary_path):
                os.remove(summary_path)
        except Exception as e:
            print(f"[Warning] セッション情報の削除に失敗しました。: {e}")

        # スレッド削除
        try:
            await thread.delete(reason=f"セッション削除によるスレッド終了: {thread.name}")
        except discord.Forbidden:
            await interaction.followup.send("セッションは削除されましたが、スレッドの削除権限がありません。サーバー管理者にお問い合わせください。", ephemeral=True)
        else:
            await interaction.followup.send(f"セッションとスレッド「**{thread.name}**」を削除しました。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DeleteSession(bot))
