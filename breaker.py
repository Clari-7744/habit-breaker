import discord, DPyUtils, jishaku, aiohttp, aiosqlite, os
from discord.ext import commands
from dotenv import load_dotenv
import schemas

load_dotenv(verbose=True)


class Breaker(DPyUtils.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            commands.when_mentioned_or("&"),
            slash_commands=True,
            intents=discord.Intents.all(),
            **kwargs,
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

    async def db_schema(self, *tables):
        n = "\n"
        schema = await (
            await bot.db.execute(
                "SELECT sql FROM sqlite_master"
                + (
                    " WHERE name IN ({})".format(
                        ", ".join(f"'{table}'" for table in tables)
                    )
                    if tables
                    else ""
                )
            )
        ).fetchall()
        return f"```sql\n{n.join([''.join(x) for x in schema if any(x) and not x[0].startswith('sqlite_autoindex')])}```"

    async def setup(self):
        async with bot.db.cursor() as c:
            for schema in schemas.all_schemas:
                await c.execute(schema)
        await bot.db.commit()
        DPyUtils.load_extensions(bot, extra_cogs=["jishaku", "DPyUtils.ContextEditor"])
        await self.create_slash_commands()

    async def on_command_error(
        self, ctx: DPyUtils.Context, error
    ):  # pylint: disable=arguments-renamed
        await super().on_command_error(ctx, error)
        if isinstance(
            error,
            (
                commands.CommandNotFound,
                commands.NoPrivateMessage,
                commands.PrivateMessageOnly,
                commands.CheckFailure,
            ),
        ):
            return await ctx.send(str(error))
        return await ctx.send(
            "an error has occurred, please ping clari and ask her to check the logs lol"
        )


bot = Breaker()
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.HIDE = True


bot.run(os.getenv("BREAKER_TOKEN"))
