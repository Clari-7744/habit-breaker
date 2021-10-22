import discord, DPyUtils
from discord.ext import commands


class OwnerCog(commands.Cog):
    def __init__(self, bot: utils.Bot):
        self.bot = bot

    @commands.command(name="addslash")
    @commands.is_owner()
    async def addslash(self, ctx: DPyUtils.Context, guild_id: int):
        async with self.bot.db.cursor() as c:
            await c.execute("INSERT INTO slash_guilds VALUES (?)", (guild_id,))
        await self.bot.db.commit()
        await (
            ctx.message.add_reaction("✅")
            if not ctx.interaction
            else ctx.send(f"Added {guild_id}", ephemeral=True)
        )


def setup(bot: utils.Bot):
    bot.add_cog(OwnerCog(bot))
