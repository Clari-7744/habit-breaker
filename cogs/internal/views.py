import discord, utils
from discord.ext import commands


class LogView(discord.ui.View):
    def __init__(self, bot: utils.Bot, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)


class LogButton(discord.ui.Button):
    def __init__(self, habit, *args, **kwargs):
        self.habit = habit
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        c = await self.view.bot.db.cursor()
        await c.execute(
            "SELECT (user_id, habit) FROM config WHERE user_id=?",
            (interaction.author.id,),
        )
        data = await c.fetchall()
        if not data:
            return await interaction.response.send_message(
                "You don't have any habits configured, use `/setup` to add one."
            )
        await interaction.response.send_message("no <3", ephemeral=True)
