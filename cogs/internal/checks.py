import DPyUtils
from discord.ext import commands


def dm_or_slash():
    async def inner(ctx: DPyUtils.Context):
        if (not ctx.interaction) and (ctx.guild is not None):
            raise commands.PrivateMessageOnly(
                "This command can only be used as a slash command or in DMs to protect your privacy."
            )
        return True

    return commands.check(inner)
