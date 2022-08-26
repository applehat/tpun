from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core import data_manager
import discord
import time
import asyncio
import json
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
        
        path = data_manager.cog_data_path(cog_instance=self)
        self.pingListPath = path / 'pingList.json'
        if self.pingListPath.exists():
            pass
        else:
            with self.pingListPath.open("w", encoding="utf-8") as f:
                f.write("{}")
        self.tempo: dict = {}

    def getPingList(self):
        try:
            with open(str(self.pingListPath), 'r') as pingList:
                x = json.load(pingList)
                return x
        except ValueError:
            self.log.exception("pingList.json failed to read")
            return None

    def parsePingList(self, guild):
        x = self.getPingList()
        for server, rolesList in x.items():
            if server == str(guild):
                return rolesList[0]

    def pingListRead(self, guild: int, roleArg: discord.role):
        i = self.parsePingList(guild)
        for role, cooldown in i.items():
            if role == roleArg.id:
                return cooldown

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None and "@" in message.content:
            guild = message.guild.id
            roles = {}
            roles = self.parsePingList(guild)
            for role, cooldown in roles.items():
                if bool(re.search(message.guild.get_role(int(role)).name, message.content, flags=re.I | re.X)
                ) or bool(re.search(message.guild.get_role(int(role)).name, message.content, flags=re.I)):
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
        guild = ctx.guild.id
        nC = {role.id: cooldown}
        with open(str(self.pingListPath), 'r') as pingList:
            try:
                x = json.load(pingList)
                if str(guild) in x:
                    y = x[str(guild)].copy()
                    y[0].update(nC)
                else:
                    x.update({str(guild): [{}]})
                    y = x[str(guild)].copy()
                    y[0].update(nC)
            except ValueError:
                self.log.exception("pingList.json read failed")
        with open(str(self.pingListPath), 'w') as pingList:
            try:
                json.dump(x, pingList)
                await ctx.send("{0} was added to the Timed Ping List with cooldown {1} seconds".format(role.mention, cooldown))
            except ValueError:
                self.log.exception("pingList.json write failed")

    @commands.guildowner_or_permissions()
    @tping.command(name="remove")
    async def remove(self, ctx: commands.Context, role: discord.Role):
        """
        Removes a role from the timed ping list
        """
        guild = ctx.guild.id
        with open(str(self.pingListPath), 'r') as pingList:
            try:
                x = json.load(pingList)
            except ValueError:
                self.log.exception("Failed to read to pingList.json")
        with open(str(self.pingListPath), 'w') as vcWrite:
            try:
                if str(guild) in x:
                    y = x[str(guild)].copy()
                    y[0].pop(str(role.id), None)
                    json.dump(x, vcWrite)
                    if x is None:
                        x = {}
            except ValueError:
                self.log.exception("Failed to write to pingList.json")
        await ctx.send("{0} was removed from the Timed Ping List".format(role.mention))

    @commands.guildowner_or_permissions()
    @tping.command(name="list")
    async def list(self, ctx: commands.Context):
        """
        Lists all the timed ping roles for the server
        """
        guild = ctx.guild.id
        roles = ""
        with open(str(self.pingListPath), 'r') as pingList:
            try:
                x = json.load(pingList)
                if str(guild) in x:
                    y = x[str(guild)].copy()
                    for i in y:
                        for role, cooldown in i.items():
                            roles = roles + "<@&{0}> with cooldown {1} seconds \n".format(role, cooldown)
                    mess1 = await ctx.send(roles)
                    await asyncio.sleep(120)
                    await mess1.delete()
            except ValueError:
                self.log.exception("Failed to read pingList.json")
