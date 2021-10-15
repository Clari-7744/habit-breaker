import discord, utils
from discord.ext import commands
from utils import TextChannel, Member
from typing import Optional


class SetupCog(commands.Cog):
    def __init__(self, bot: utils.Bot):
        self.bot = bot

    @commands.command(name="setup")
    async def setup(
        self, ctx: commands.Context, *, habit: str = commands.Option(description="The habit you'd like to track")
    ):
        """
        Sets up a new habit to break.
        """
        if (not ctx.interaction) and ctx.guild:
            raise commands.PrivateMessageOnly(
                "This command can only be used in DMs for privacy reasons"
            )
        c = await self.bot.db.cursor()
#        await c.execute(
#            "INSERT INTO config(user_id, habit) VALUES (?, ?)",
#            (ctx.author.id, habit),
#        )
        await ctx.send(habit, ephemeral=True)

def setup(bot: utils.Bot):
    bot.add_cog(SetupCog(bot))
