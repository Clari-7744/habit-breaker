import discord, DPyUtils, datetime
from discord.ext import commands
from typing import Optional
from cogs.internal.checks import dm_or_slash
from cogs.internal import fmt_habit
from DPyUtils import duration


class SetupCog(commands.Cog):
    def __init__(self, bot: DPyUtils.Bot):
        self.bot = bot

    @commands.command(name="add")
    @dm_or_slash()
    async def add(
        self,
        ctx: DPyUtils.Context,
        *,
        habit: str = commands.Option(description="The habit you'd like to add"),
    ):
        """
        Sets up a new habit to break.
        """
        cur = await self.bot.db.cursor()
        await cur.execute(
            "SELECT * FROM config WHERE user_id=? AND habit=?",
            (ctx.author.id, fmt_habit(habit)),
        )
        if await cur.fetchone():
            return await ctx.send(
                f"You already have a habit configured with the name `{habit}`"
            )
        await cur.execute(
            "INSERT INTO config(user_id, habit, pretty_name) VALUES (?, ?, ?)",
            (ctx.author.id, fmt_habit(habit), habit),
        )
        await self.bot.db.commit()
        await ctx.send(f"Configured {habit}", ephemeral=True)

    @commands.command(name="log")
    @dm_or_slash()
    async def log(
        self,
        ctx: DPyUtils.Context,
        override_time: Optional[int] = commands.Option(
            default=None,
            description="Override time that you'd like to log (UTC timestamp)",
        ),
        *,
        habit: str = commands.Option(description="The habit you'd like to log"),
    ):
        """
        Logs an occurence of a configured habit.
        """
        cur = await self.bot.db.cursor()
        await cur.execute(
            "SELECT (pretty_name) FROM config WHERE user_id=? AND habit=?",
            (ctx.author.id, fmt_habit(habit)),
        )
        if not await cur.fetchone():
            return await ctx.send(
                f'You have no habit configured with the name "{habit}". Type `{ctx.prefix}list` to view configured habits.',
                ephemeral=True,
            )
        ts = datetime.datetime.now()
        if override_time:
            ts = datetime.datetime.fromtimestamp(override_time)
        await cur.execute(
            "INSERT INTO logs(user_id, habit, timestamp) VALUES (?, ?, ?)",
            (ctx.author.id, fmt_habit(habit), int(ts.timestamp())),
        )
        await self.bot.db.commit()
        await ctx.send(f"Logged `{habit}`", ephemeral=True)

    @commands.command(name="check")
    @dm_or_slash()
    async def check(
        self,
        ctx: DPyUtils.Context,
        *,
        habit: str = commands.Option(description="The habit you'd like to check"),
    ):
        """
        Shows info about the specified habit.
        """
        cur = await self.bot.db.cursor()
        data = ctx.author.id, fmt_habit(habit)
        await cur.execute(
            "SELECT (pretty_name) FROM config WHERE user_id=? AND habit=?",
            data,
        )
        p = await cur.fetchone()
        if not p:
            return await ctx.send(
                f'You have no habit configured with the name "{habit}". Type `{ctx.prefix}list` to view configured habits.',
                ephemeral=True,
            )
        p = p[0]
        await cur.execute("SELECT COUNT(*) FROM logs WHERE user_id=? AND habit=?", data)
        num = (await cur.fetchone())[0]
        if not num:
            return await ctx.send(f"You haven't logged any `{p}` yet.", ephemeral=True)
        await cur.execute(
            "SELECT timestamp FROM logs WHERE user_id=? AND habit=?", data
        )
        (ts,) = await cur.fetchone()
        await ctx.send(
            embed=discord.Embed(
                title=f"{p}",
                description=f"# of occurrences: `{num}`\nLast ocurrence: <t:{ts}:F>\nYou've been {p} free for {duration.strfdur(datetime.datetime.now().timestamp()-ts)}",
            ),
            ephemeral=True,
        )

    @commands.command(name="list")
    @dm_or_slash()
    async def hlist(self, ctx: DPyUtils.Context):
        """
        Lists your configured habits.
        """
        cur = await self.bot.db.cursor()
        await cur.execute(
            "SELECT habit, pretty_name FROM config WHERE user_id=?", (ctx.author.id,)
        )
        habits = await cur.fetchall()
        if not habits:
            return await ctx.send(
                f"You have no habits configured. Type `{ctx.prefix}add HABIT` to add one.",
                ephemeral=True,
            )
        await ctx.send(
            embed=discord.Embed(
                title="Configured Habits",
                description=", ".join(f"`{p}`" for _, p in habits),
            ),
            ephemeral=True,
        )

    @commands.command(name="remove")
    @dm_or_slash()
    async def remove(
        self,
        ctx: DPyUtils.Context,
        *,
        habit: str = commands.Option(description="The habit you'd like to remove"),
    ):
        """
        Removes a configured habit.
        """
        cur = await self.bot.db.cursor()
        await cur.execute(
            "DELETE FROM config WHERE user_id=? AND habit=? RETURNING pretty_name",
            (ctx.author.id, fmt_habit(habit)),
        )
        if not await cur.fetchone():
            return await ctx.send(
                f"You have no habit configured with the name `{habit}`", ephemeral=True
            )
        await self.bot.db.commit()
        await ctx.send(f"Removed `{habit}`", ephemeral=True)

    @commands.command(name="invite")
    async def invite(self, ctx: DPyUtils.Context, *, guild_id: int = None):
        """
        Get an invite link for the bot.
        """

        def url(bot: bool = 0):
            return discord.utils.oauth_url(
                self.bot.user.id,
                permissions=discord.Permissions(139586784320),
                scopes=("bot" if bot else "", "applications.commands"),
                guild=discord.Object(guild_id) if guild_id else discord.utils.MISSING,
            )

        t = f"[Invite Bot]({url(1)})\n[Slash Commands Only]({url()})"
        if ctx.interaction:
            return await ctx.send(t)
        await ctx.send(
            embed=discord.Embed(
                title="Invite", description=t, color=discord.Color.random()
            )
        )


def setup(bot: DPyUtils.Bot):
    bot.add_cog(SetupCog(bot))
