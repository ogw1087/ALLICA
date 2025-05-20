import json
from discord import app_commands, Interaction

TOGGLE_FILE = "data/toggle_state.json"

def load_toggle_state():
    try:
        with open(TOGGLE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("enabled", True)
    except (FileNotFoundError, json.JSONDecodeError):
        return True

def save_toggle_state(state: bool):
    with open(TOGGLE_FILE, "w", encoding="utf-8") as f:
        json.dump({"enabled": state}, f, indent=2)

def setup(bot):
    bot.toggle_enabled = load_toggle_state()

    @bot.tree.command(name="toggle", description="BotのON/OFFを切り替えます（管理者専用）")
    async def toggle(interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("!注意! このコマンドは管理者のみ実行可能です。", ephemeral=True)
            return

        bot.toggle_enabled = not bot.toggle_enabled
        save_toggle_state(bot.toggle_enabled)
        status = "有効化" if bot.toggle_enabled else "無効化"
        await interaction.response.send_message(f"Botは現在: **{status}** されています。", ephemeral=True)