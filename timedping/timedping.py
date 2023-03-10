from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
import discord
import time
import asyncio
import re
import logging


class timedping(commands.Cog):
    """
    Timed Ping cog
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.log = logging.getLogger('red.tpun.timedping')
        self.config = Config.get_conf(
            self,
            identifier=365398642334498816
        )
        default_guild = {
            "pingableroles": {}
        }
        self.config.register_guild(**default_guild)
        self.tempo: dict = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None and "@" in message.content:
            guild = message.guild
            roles = await self.config.guild(guild).pingableroles()
            for role, cooldown in roles.items():
                if bool(re.search(guild.get_role(int(role)).name, message.content, flags=re.I | re.X)
                    ) or bool(re.search(guild.get_role(int(role)).name, message.content, flags=re.I)):
                    if role not in self.tempo.keys():
                        await message.reply("<@&{0}>".format(int(role)))
                        newTempo = {str(role): int(time.time() + cooldown)}
                        self.tempo.update(newTempo)
                    elif self.tempo[role] > time.time():
                        await message.reply("There is a {0} second cooldown in between uses. There is <t:{1}:R>"
                            .format(str(cooldown), int(self.tempo[role]))
                            + "remaining in the cooldown"
                        )
                    else:
                        await message.reply("<@&{0}>".format(int(role)))
                        newTempo = {str(role): int(time.time() + cooldown)}
                        self.tempo.update(newTempo)

    @commands.group(name="tping")
    async def tping(self, ctx):
        """
        Base command for all timed ping commands
        """
        pass

    @commands.guildowner_or_permissions()
    @tping.command(name="add")
    async def add(self, ctx: commands.Context, role: discord.Role, cooldown: int):
        """
        Adds a role to the timed ping list
        """
        guild = ctx.guild
        nC = {role.id: cooldown}
        pingableRoles = await self.config.guild(guild).pingableroles()
        pingableRoles.update(nC)
        await self.config.guild(guild).pingableroles.set(pingableRoles)
        await ctx.send("{0} was added to the Timed Ping List with cooldown {1} seconds".format(role.mention, cooldown))

    @commands.guildowner_or_permissions()
    @tping.command(name="remove")
    async def remove(self, ctx: commands.Context, role: discord.Role):
        """
        Removes a role from the timed ping list
        """
        guild = ctx.guild
        pingableRoles = await self.config.guild(guild).pingableroles()
        pingableRoles.pop(str(role.id), None)
        await self.config.guild(guild).pingableroles.set(pingableRoles)
        await ctx.send("{0} was removed from the Timed Ping List".format(role.mention))

    @commands.guildowner_or_permissions()
    @tping.command(name="list")
    async def list(self, ctx: commands.Context):
        """
        Lists all the timed ping roles for the server
        """
        guild = ctx.guild
        roles = ""
        pingableRoles = await self.config.guild(guild).pingableroles()
        for role, cooldown in pingableRoles.items():
            roles = roles + "<@&{0}> with cooldown {1} seconds \n".format(role, cooldown)
        if roles != "":
            mess1 = await ctx.send(roles)
        else:
            mess1 = await ctx.send("There are no pingable roles set up yet")
        await asyncio.sleep(120)
        await mess1.delete()
