import discord
from discord import app_commands
import google.generativeai as genai

# テキストファイル化したプロンプトの読み込み
def load_prompt_template(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()

# Geminiへの質問
def setup(bot):
    @bot.tree.command(name="ask", description="アリカに質問する")
    @app_commands.describe(
        question="質問内容",
        model="使用するモデルを選択"
    )
    @app_commands.choices(
        model=[
            app_commands.Choice(name="2.5_flash",           value="gemini-2.5-flash"),
            app_commands.Choice(name="2.5_flash-lite",      value="gemini-2.5-flash-lite-preview-06-17"),
            app_commands.Choice(name="2.0_flash",           value="gemini-2.0-flash-001"),
            app_commands.Choice(name="2.0_flash-lite",      value="gemini-2.0-flash-lite-001"),
        ]
    )
    async def ask(interaction: discord.Interaction, question: str, model: app_commands.Choice[str]):
        if not bot.toggle_enabled:
            await interaction.response.send_message("Botは現在一時停止中です。", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        prompt_template = load_prompt_template(bot.config.get("ask_prompt_template_path", "prompts/ask.txt"))
        prompt = prompt_template.replace("{input}", question)
        if "thinking" in model.value:
            prompt = "あなたは思考ステップを丁寧に示しながら答えます。\n" + prompt

        try:
            selected_model = genai.GenerativeModel(model.value)
            response = selected_model.generate_content(prompt)

            embed = discord.Embed(
                title="💬 しつもん！",
                description=f"**あなたの質問：**\n{question}\n\n**回答：**\n{response.text}",
                color=0x7AAEDC
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {e}")