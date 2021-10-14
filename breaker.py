import discord, utils, jishaku, aiohttp, aiosqlite
from discord.ext import commands


class Breaker(utils.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            commands.when_mentioned_or("&"),
            slash_commands=True,
            intents=discord.Intents.all(),
            **kwargs
        )
        self.session: aiohttp.ClientSession
        self.db: aiosqlite.Connection

    async def start(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session, aiosqlite.connect(
            "data.db"
        ) as connection:
            self.session: aiohttp.ClientSession = session
            self.db: aiosqlite.Connection = connection
            await super().start(*args, **kwargs)

    async def setup(self):
        c = await self.db.cursor()
        await c.execute("SELECT * FROM slash_guilds")
        guilds = [
            t[0] for t in await c.fetchall() if t[0] in map(lambda g: g.id, self.guilds)
        ]
        self.slash_command_guilds = guilds
        await super().setup()


bot = Breaker()
utils.load_extensions(bot, extra_cogs=["jishaku"])
jishaku.Flags.NO_UNDERSCORE = True


bot.run("ODk4MDI3NTI2NjI5MjU3MzA2.YWePTg.iUwU_S0h5OxC3BaOn6AVjZoy4pc")
