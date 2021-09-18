import discord
from discord.ext import tasks, commands
import configparser
import random
from datetime import datetime, timedelta
import time
import requests
import json
import asyncio

api_key = SIMPLEMMO_PUBLIC_API_KEY
dir = CURRENT_WORKING_DIRECTORY

with open(f'{dir}/worldboss/channels.txt', 'r') as f:
    channelList = json.load(f)
times = [0, 1, 5, 10, 15, 30, 60]
pinged = [0, 0, 0, 0, 0, 0, 0]
messages = []
pictures = []
res = []
counter = 0

def updateBoss():
    endpoint = "https://api.simple-mmo.com/v1/worldboss/all"
    payload = {'api_key': api_key}
    r = requests.post(url = endpoint, data = payload)
    res = r.json()
    with open(f'{dir}/worldboss/boss.txt', 'w') as f2:
        json.dump(res, f2)
    sortBossList()

def sortBossList():
    with open(f'{dir}/worldboss/boss.txt', 'r') as f:
        data = json.load(f)
    data = sorted(data, key = lambda i: i['enable_time'])
    with open(f'{dir}/worldboss/boss.txt', 'w') as f1:
        json.dump(data, f1)

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def createTimer(data):
    bosstime = data["enable_time"]
    bosstime = datetime.fromtimestamp(bosstime)
    currenttime = datetime.now()
    countdown = bosstime-currenttime
    countdown = strfdelta(countdown, "{days} d {hours} h {minutes} m {seconds} s")
    return countdown

def createEmbed(data):
    embed = discord.Embed(
        title=data["name"],
        description='',
        url='https://web.simple-mmo.com/worldboss/all',
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://web.simple-mmo.com/img/sprites/"+data["avatar"]+".png")
    embed.add_field(name='Level', value=f'{format(int(data["level"]), ",d")}', inline=False)
    embed.add_field(name='HP', value=f'{format(int(data["current_hp"]), ",d")}/{format(int(data["max_hp"]), ",d")}', inline=False)
    embed.add_field(name='Strength', value=f'{format(int(data["str"]), ",d")}', inline=True)
    embed.add_field(name='Defence', value=f'{format(int(data["def"]), ",d")}', inline=True)
    embed.add_field(name='Dexterity', value=f'{format(int(data["dex"]), ",d")}', inline=True)
    embed.add_field(name='Active', value=f'<t:{data["enable_time"]}:R> (<t:{data["enable_time"]}:f>)', inline=False)
    return embed

def createPingEmbed(data, time):
    timename = {"0":"World Boss Ping", "1":"1 Min - World Boss Ping", "5":"5 Min - World Boss Ping", "10":"10 Min - World Boss Ping", "15":"15 Min - World Boss Ping", "30":"30 Min - World Boss Ping", "60":"60 Min - World Boss Ping"}
    names = ""
    roles = ""

    if not data["user"]:
        names = "`None`"
    else:
        for id in data["user"]:
            names += f'<@{id}> '

    if not data["role"]:
        roles = "`None`"
    else:
        for id in data["role"]:
            roles += f'<@&{id}> '

    embed = discord.Embed(
        title=timename[str(time)],
        description='Currently registered pings for this guild.',
        color=discord.Color.blue()
    )
    embed.add_field(name='Users:', value=names, inline=False)
    embed.add_field(name='Roles:', value=roles, inline=False)
    return embed

def openPingList(time):
    if time == 0:
        with open(f'{dir}/worldboss/pings/ping.txt', 'r') as f:
            pingList = json.load(f)
    else:
        with open(f'{dir}/worldboss/pings/ping{time}.txt', 'r') as f:
            pingList = json.load(f)
    return pingList

def closePingList(pingList, time):
    if time == 0:
        with open(f'{dir}/worldboss/pings/ping.txt', 'w') as f:
            json.dump(pingList, f)
    else:
        with open(f'{dir}/worldboss/pings/ping{time}.txt', 'w') as f:
            json.dump(pingList, f)

def stringPings(data, time):
    if time == 0:
        output = "World Boss Now! "
    else:
        output = f'World Boss in {time} Minutes '
    for id in data["user"]:
        output += f'<@{id}> '
    for id in data["role"]:
        output += f'<@&{id}> '
    return output

async def updateBossList(self, data):
    global channelList
    global messages
    global pictures
    global pinged
    channels=channelList.values()

    for msg in pictures:
        try:
            await msg.delete()
        except:
            continue
    for msg in messages:
        try:
            await msg.delete()
        except:
            continue
    pictures = []
    messages = []

    if len(data) > 1:
        data.pop(0)
        self.index = 0
        curBoss = data[0]
        pinged = [0, 0, 0, 0, 0, 0, 0]
        with open(f'{dir}/worldboss/boss.txt', 'w') as f1:
            json.dump(data, f1)
    else:
        updateBoss()
        await asyncio.sleep(1800)
        return

async def checkPings(self, curBoss, timeleft):
    global channelList
    global messages
    global pictures
    global pinged

    if timeleft <= timedelta(hours=1) and pinged[6] == 0:
        with open(f'{dir}/worldboss/pings/ping60.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 60)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[6]=1
    elif timeleft <= timedelta(minutes=30) and pinged[5] == 0:
        with open(f'{dir}/worldboss/pings/ping30.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 30)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[5]=1
    elif timeleft <= timedelta(minutes=15) and pinged[4] == 0:
        with open(f'{dir}/worldboss/pings/ping15.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 15)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[4]=1
    elif timeleft <= timedelta(minutes=10) and pinged[3] == 0:
        with open(f'{dir}/worldboss/pings/ping10.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 10)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[3]=1
    elif timeleft <= timedelta(minutes=5) and pinged[2] == 0:
        with open(f'{dir}/worldboss/pings/ping5.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 5)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[2]=1
    elif timeleft <= timedelta(minutes=1) and pinged[1] == 0:
        with open(f'{dir}/worldboss/pings/ping1.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 1)
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[1]=1
    elif timeleft <= timedelta(seconds=5) and pinged[0] == 0:
        with open(f'{dir}/worldboss/pings/ping.txt', 'r') as f:
            toPing = json.load(f)
        for id in toPing.keys():
            try:
                channel = self.client.get_channel(int(channelList[id]))
                msg = stringPings(toPing[id], 0) + "\nLink <https://web.simple-mmo.com/worldboss/all>"
                await channel.send(msg, delete_after=60)
            except:
                continue
        pinged[0]=1
    return


class BossCog(commands.Cog):
    def __init__(self, client):
        self.index = 0
        self.client = client
        self.printEmbeds.start()

    @commands.Cog.listener()
    async def on_error(self, event):
        if isinstance(error, discord.errors.HTTPException):
            asyncio.sleep(30)
        elif isinstance(error, discord.errors.Forbidden):
            asyncio.sleep(30)
        elif isinstance(error, discord.errors.DiscordServerError):
            asyncio.sleep(30)
        else:
            with open(f'{dir}/errorlog/errors.txt', 'a') as f:
                f.write(f'{str(datetime.now())}: {event}\n')
            asyncio.sleep(30)

        for msg in pictures:
            try:
                await msg.delete()
            except:
                pass
        for msg in messages:
            try:
                await msg.delete()
            except:
                pass
        pictures = []
        messages = []
        self.index = 0
        self.printEmbeds.start()

    @tasks.loop(seconds=4.0)
    async def printEmbeds(self):
        global channelList
        global messages
        global pictures

        channels=channelList.values()

        with open(f'{dir}/worldboss/boss.txt', 'r') as f1:
            data = json.load(f1)

        if len(data) > 0:
            curBoss = data[0]
            timeleft = (datetime.fromtimestamp(curBoss["enable_time"])-datetime.now())
        else:
            await updateBossList(self, data)
            return

        if datetime.fromtimestamp(curBoss["enable_time"]) < datetime.now():
            await updateBossList(self, data)
            return

        try:
            await checkPings(self, curBoss, timeleft)
        except:
            pass

        embed=createEmbed(data[0])
        countdown=createTimer(data[0])

        if self.index == 0:
            for i in channels:
                try:
                    channel = self.client.get_channel(int(i))
                    pictures.append(await channel.send(embed=embed))
                except:
                    pass

        self.index += 1

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def addWorldBoss(self, ctx, txtch: discord.TextChannel):
        global channelList
        global pictures
        global messages

        if txtch.id in channelList.values():
            await ctx.send('Channel is already used for a world boss timer')
            await ctx.message.add_reaction("❌")
            return
        else:
            if str(ctx.guild.id) in channelList.keys():
                await ctx.send('This guild already has a world boss channel! Overwriting Now.', delete_after=5)
            self.printEmbeds.cancel()
            for msg in pictures:
                try:
                    await msg.delete()
                except:
                    continue
            for msg in messages:
                try:
                    await msg.delete()
                except:
                    continue
            pictures = []
            messages = []
            self.index = 0

            channelList[str(ctx.guild.id)] = txtch.id

            with open(f'{dir}/worldboss/channels.txt', 'w') as f:
                json.dump(channelList, f)
            self.printEmbeds.start()
            await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def removeWorldBoss(self, ctx, txtch: discord.TextChannel):
        global channelList
        global pictures
        global messages
        global times

        if str(ctx.guild.id) not in channelList.keys():
            await ctx.send('This guild does not have a world boss timer!')
            await ctx.message.add_reaction("❌")
            return
        elif txtch.id not in channelList.values():
            await ctx.send('Channel is not registered for a world boss timer')
            await ctx.message.add_reaction("❌")
            return
        else:
            self.printEmbeds.cancel()
            for msg in pictures:
                try:
                    await msg.delete()
                except:
                    continue
            for msg in messages:
                try:
                    await msg.delete()
                except:
                    continue
            pictures = []
            messages = []
            self.index = 0

            for item in times:
                pingList=openPingList(item)
                if str(ctx.guild.id) in pingList.keys():
                    del pingList[str(ctx.guild.id)]

            del channelList[str(ctx.guild.id)]

            with open(f'{dir}/worldboss/channels.txt', 'w') as f:
                json.dump(channelList, f)
            self.printEmbeds.start()
            await ctx.message.add_reaction("✅")

    @commands.command(aliases=['ap'])
    async def addPing(self, ctx, time:int=0):
        global times
        global channelList
        if str(ctx.guild.id) not in channelList.keys():
            await ctx.send("An admin needs to setup a world boss channel first!")
            await ctx.message.add_reaction("❌")
            return
        if time not in times:
            await ctx.send("Incorrect time, please choose from `1`, `5`, `10`, `15`, `30` or `60`")
            await ctx.message.add_reaction("❌")
            return

        pingList=openPingList(time)

        if str(ctx.guild.id) in pingList.keys():
            if ctx.author.id in pingList[str(ctx.guild.id)]["user"]:
                await ctx.send("You are already registered for this notification.")
                await ctx.message.add_reaction("❌")
                return
            else:
                pingList[str(ctx.guild.id)]["user"].append(ctx.author.id)
        else:
            pingList[str(ctx.guild.id)]={"user":[ctx.author.id], "role":[]}

        closePingList(pingList, time)

        await ctx.message.add_reaction("✅")

    @commands.command(aliases=['rp'])
    async def removePing(self, ctx, time:int=0):
        global times
        global channelList
        if str(ctx.guild.id) not in channelList.keys():
            await ctx.send("An admin needs to setup a world boss channel first!")
            await ctx.message.add_reaction("❌")
            return
        if time not in times:
            await ctx.send("Incorrect time, please choose from `1`, `5`, `10`, `15`, `30` or `60`")
            await ctx.message.add_reaction("❌")
            return

        pingList=openPingList(time)

        if str(ctx.guild.id) not in pingList.keys():
            await ctx.send("Unable to find ping registration. Please check parameters.")
            await ctx.message.add_reaction("❌")
            return
        else:
            if ctx.author.id in pingList[str(ctx.guild.id)]["user"]:
                pingList[str(ctx.guild.id)]["user"].remove(ctx.author.id)
                closePingList(pingList, time)
            else:
                await ctx.send("Unable to find ping registration. Please check parameters.")
                await ctx.message.add_reaction("❌")
                return

        await ctx.message.add_reaction("✅")

    @commands.command(aliases=['curPings', 'cp'])
    async def currentPings(self, ctx, time:int=0):
        global times
        if time not in times:
            await ctx.send("Incorrect time, please choose from `1`, `5`, `10`, `15`, `30` or `60`")
            await ctx.message.add_reaction("❌")
            return

        pingList=openPingList(time)

        if str(ctx.guild.id) not in pingList.keys():
            await ctx.send("No registered pings.")
            await ctx.message.add_reaction("❌")
            return
        else:
            embed = createPingEmbed(pingList[str(ctx.guild.id)], time)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")

    @commands.command(aliases=['arp'])
    @commands.has_permissions(manage_guild=True)
    async def addRolePing(self, ctx, role:discord.Role, time:int=0):
        global times
        global channelList
        if str(ctx.guild.id) not in channelList.keys():
            await ctx.send("An admin needs to setup a world boss channel first!")
            await ctx.message.add_reaction("❌")
            return
        if time not in times:
            await ctx.send("Incorrect time, please choose from `1`, `5`, `10`, `15`, `30` or `60`")
            await ctx.message.add_reaction("❌")
            return

        pingList=openPingList(time)

        if str(ctx.guild.id) in pingList.keys():
            if role.id in pingList[str(ctx.guild.id)]["role"]:
                await ctx.send("This role is already registered for this notification.")
                await ctx.message.add_reaction("❌")
                return
            else:
                pingList[str(ctx.guild.id)]["role"].append(role.id)
        else:
            pingList[str(ctx.guild.id)]={"user":[], "role":[role.id]}

        closePingList(pingList, time)

        await ctx.message.add_reaction("✅")

    @commands.command(aliases=['rrp'])
    @commands.has_permissions(manage_guild=True)
    async def removeRolePing(self, ctx, role:discord.Role, time:int=0):
        global times
        global channelList
        if str(ctx.guild.id) not in channelList.keys():
            await ctx.send("An admin needs to setup a world boss channel first!")
            await ctx.message.add_reaction("❌")
            return
        if time not in times:
            await ctx.send("Incorrect time, please choose from `1`, `5`, `10`, `15`, `30` or `60`")
            await ctx.message.add_reaction("❌")
            return

        pingList=openPingList(time)

        if str(ctx.guild.id) not in pingList.keys():
            await ctx.send("Unable to find ping registration. Please check parameters.")
            await ctx.message.add_reaction("❌")
            return
        else:
            if role.id in pingList[str(ctx.guild.id)]["role"]:
                pingList[str(ctx.guild.id)]["role"].remove(role.id)
                closePingList(pingList, time)
            else:
                await ctx.send("Unable to find ping registration. Please check parameters.")
                await ctx.message.add_reaction("❌")
                return

        await ctx.message.add_reaction("✅")

    @commands.command()
    async def clearWorldBoss(self, ctx):
        global pictures
        global messages

        if ctx.author.id != 151819430026936320 and ctx.author.id != 609728408112332811:
            await ctx.message.add_reaction("❌")

        self.printEmbeds.cancel()
        for msg in pictures:
            try:
                await msg.delete()
            except:
                continue
        for msg in messages:
            try:
                await msg.delete()
            except:
                continue
        pictures = []
        messages = []
        await ctx.message.delete()
        self.index = 0

def setup(client):
    client.add_cog(BossCog(client))
