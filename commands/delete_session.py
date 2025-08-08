import discord
from discord import app_commands
from discord.ext import commands
import os
import json

from context.session_manager import delete_session, get_session_by_thread

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, author_id, timeout=30):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("この操作はセッション作成者のみが行えます。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="削除する", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="やめる", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.send_message("キャンセルしました。", ephemeral=True)

class DeleteSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="delete_session",
        description="現在のスレッドとセッションを削除します"
    )
    async def delete_session_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        thread = interaction.channel
        user_id = str(interaction.user.id)

        if not isinstance(thread, discord.Thread):
            return await interaction.followup.send("このコマンドはスレッド内でのみ使用できます。", ephemeral=True)

        session = get_session_by_thread(thread.id)
        if not session:
            return await interaction.followup.send("このスレッドに対応するセッションは存在しません。", ephemeral=True)

        if session["owner_id"] != user_id:
            return await interaction.followup.send("このセッションを削除できるのは作成者のみです。", ephemeral=True)

        topic = session["topic"]

        # 確認画面を表示
        view = ConfirmDeleteView(author_id=interaction.user.id)
        await interaction.followup.send(
            f"⚠️ 本当にセッション「**{topic}**」を削除しますか？ この操作は元に戻せません。",
            view=view,
            ephemeral=True
        )

        # ユーザーの操作を待つ
        timeout = await view.wait()
        if view.value is None:
            return await interaction.followup.send("時間切れのためキャンセルされました。", ephemeral=True)

        if view.value is False:
            return  # キャンセル時はボタン処理側で送信済み
        
        session_id = session["session_id"]

        # data/session/session_threads.jsonからセッション情報を削除
        delete_session(thread.id)

        # 文脈情報ファイルを削除
        try:
            summary_path = os.path.join("data", "session", f"{session_id}.json")
            if os.path.exists(summary_path):
                os.remove(summary_path)
        except Exception as e:
            print(f"[Warning] セッション情報の削除に失敗しました。: {e}")

        # スレッドを削除
        try:
            await thread.delete(reason=f"セッション削除によるスレッド終了: {topic}")
        except discord.Forbidden:
            await interaction.followup.send("セッションは削除されましたが、スレッドの削除権限がありません。サーバー管理者にお問い合わせください。", ephemeral=True)
        else:
            #await thread.parent.send(f"セッションとスレッド「**{topic}**」を削除しました。", ephemeral=True)
            await thread.parent.send(f"セッションとスレッド「**{topic}**」を削除しました。")

async def setup(bot: commands.Bot):
    await bot.add_cog(DeleteSession(bot))
