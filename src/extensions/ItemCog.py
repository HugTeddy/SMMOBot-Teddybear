import configparser
import discord
import pytz
from discord.ext import tasks, commands
from datetime import date, datetime
from PIL import Image
from io import BytesIO
import requests
import html
import re
import json
from extensions.BlacklistCog import checkBlacklist
from extensions.DatabaseCog import discordLookup
from disputils import BotEmbedPaginator
import mysql.connector
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)

dir = CURRENT_WORKING_DIRECTORY
config = configparser.ConfigParser()
config.read(f'{dir}/config.ini')
API_KEY = config.get('DEFAULT', 'Api_Key')
mysql_host = config.get('MYSQL', 'host')
mysql_user = config.get('MYSQL', 'user')
mysql_password = config.get('MYSQL', 'pwd')

regexmatch = ["[[", "]]"]

with open(f'{dir}/blacklist/items.txt', 'r') as f:
    blacklist = json.load(f)

with open(f'{dir}/blacklist/guild_items.txt', 'r') as f:
    guild_blacklist = json.load(f)


def createSQLCommand(lib):
    res_lib = dict(lib)

    res_lib["name"] = lib["name"].replace("\"", "\\\"")

    if lib["description"] and len(lib["description"]) != 0:
        res_lib["description"] = lib["description"].replace("\"", "\\\"")
    else:
        del res_lib["description"]

    del res_lib["image_url"]
    res_lib["image"] = lib["image_url"]

    del res_lib["market"]
    res_lib["pmin"] = lib["market"]["low"]
    res_lib["pmax"] = lib["market"]["high"]

    del res_lib["custom_item"]
    res_lib["custom"] = lib["custom_item"]
    if res_lib["custom"] == 1:
        res_lib["obtainable"] = 1

    res_lib["equipable"] = int(lib["equipable"])
    res_lib["circulation"] = int(lib["circulation"])

    del res_lib["stat1"]
    del res_lib["stat2"]
    del res_lib["stat3"]
    del res_lib["stat1modifier"]
    del res_lib["stat2modifier"]
    del res_lib["stat3modifier"]

    if lib["stat1"] != None:
        if lib["stat1"] == "str":
            res_lib["strength"] = lib["stat1modifier"]
        elif lib["stat1"] == "def":
            res_lib["defense"] = lib["stat1modifier"]
        elif lib["stat1"] == "crit":
            res_lib["critical"] = lib["stat1modifier"]
        elif lib["stat1"] == "hp":
            res_lib["health"] = lib["stat1modifier"]

    if lib["stat2"] != None:
        if lib["stat2"] == "str":
            res_lib["strength"] = lib["stat2modifier"]
        elif lib["stat2"] == "def":
            res_lib["defense"] = lib["stat2modifier"]
        elif lib["stat2"] == "crit":
            res_lib["critical"] = lib["stat2modifier"]
        elif lib["stat2"] == "hp":
            res_lib["health"] = lib["stat2modifier"]

    if lib["stat3"] != None:
        if lib["stat3"] == "str":
            res_lib["strength"] = lib["stat3modifier"]
        elif lib["stat3"] == "def":
            res_lib["defense"] = lib["stat3modifier"]
        elif lib["stat3"] == "crit":
            res_lib["critical"] = lib["stat3modifier"]
        elif lib["stat3"] == "hp":
            res_lib["health"] = lib["stat3modifier"]

    res_lib["created_at"] = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
    res_lib["updated_at"] = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')

    command_list = []
    col_list = []
    col_data = []

    for data in res_lib.keys():
        if type(res_lib[data]) == str:
            if data != "created_at":
                command_list.append(f'{data}=\"{res_lib[data]}\"')
            col_list.append(str(data))
            col_data.append(f'\"{res_lib[data]}\"')
        else:
            command_list.append(f"{data}={res_lib[data]}")
            col_list.append(str(data))
            col_data.append(f'{res_lib[data]}')

    cmd_string = ",".join(command_list)
    col_string = ",".join(col_list)
    data_string = ",".join(col_data)
    command = f'INSERT INTO Items2 ({col_string}) VALUES ({data_string}) ON DUPLICATE KEY UPDATE {cmd_string};'
    print(command)
    return command


def getIndex(row: int):
    mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database="smmo"
    )
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT * FROM Items2 WHERE id={row}')
    data = mycursor.fetchall()[0]
    mydb.close()
    return data


async def getUpdateList(itemid):
    mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database="smmo"
    )
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT name FROM Items2 WHERE id={itemid}')
    cur_data = mycursor.fetchall()
    if len(cur_data) > 0:
        return True
    else:
        return False


async def checkSupporter(ctx):
    mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database="smmo"
    )
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT smmoID FROM Users WHERE discordID={ctx.author.id}')
    cur_data = mycursor.fetchall()
    if len(cur_data) > 0:
        smmoID = cur_data[0]
        with open(f'{dir}/data/tags/donator.txt', 'r') as f:
            smmo_data = json.load(f)
        if smmoID in smmo_data:
            return True
    return True


async def paginate(ctx, embeds):
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()


def createItemEmbed(data):
    attributes = ""
    colors = {"Common": discord.Color.light_grey(), "Uncommon": discord.Color.blue(), "Rare": discord.Color.orange(),
              "Elite": discord.Color.red(), "Epic": discord.Color.blurple(),
              "Legendary": discord.Color.from_rgb(255, 255, 0), "Celestial": discord.Color.from_rgb(0, 255, 255)}
    if data[6] in colors.keys():
        color = colors[data[6]]
    else:
        color = discord.Color.default()
    if data[8] != None:
        attributes += f"hp +{data[8]} "
    if data[9] != None:
        attributes += f"str +{data[9]} "
    if data[10] != None:
        attributes += f"def +{data[10]} "
    if data[11] != None:
        attributes += f"crit +{data[11] / 10}% "

    if data[3] not in ["none", None, "0", 0, ""]:
        desc = html.unescape(data[3])
    else:
        desc = "No Description"

    last_update = round(data[22].replace(tzinfo=pytz.timezone('US/Eastern')).astimezone(tz=None).timestamp())

    embed = discord.Embed(
        title=html.unescape(data[1]),
        url='https://simplemmo.me/mobile?page=item/inspect/' + f'{int(data[0])}' + f'?new_page=true',
        description=f'SMMO Item ID: {int(data[0])}\nLast Updated: <t:{last_update}:f>\nDescription: *{desc}*',
        color=color
    )
    if data[2] == "Background":
        embed.set_image(url=f"https://web.simple-mmo.com{data[17]}")
    else:
        embed.set_thumbnail(url=f"https://web.simple-mmo.com{data[17]}")
    embed.add_field(name='Type', value=f'{data[2]}', inline=True)
    if data[4] is None:
        data[4] = 0
    embed.add_field(name='Level', value=f'{format(int(data[5]), ",d")}', inline=True)
    embed.add_field(name='Required Level', value=f'{format(int(data[5]), ",d")}', inline=True)
    embed.add_field(name='Rarity', value=f'{data[6]}', inline=True)
    if data[7] is None:
        data[7] = 0
    embed.add_field(name='Value', value=f'{format(int(data[7]), ",d")}', inline=True)
    if data[18] is None:
        data[18] = 0
    embed.add_field(name='Circulation', value=f'{format(int(data[18]), ",d")} Items', inline=True)
    if data[19] is None:
        data[19] = 0
    if data[20] is None:
        data[20] = 0
    embed.add_field(name='Market Value', value=f'{format(int(data[19]), ",d")} to {format(int(data[20]), ",d")} Gold',
                    inline=True)
    if int(data[12]) == 0:
        embed.add_field(name='Custom', value=f'❌', inline=True)
    else:
        embed.add_field(name='Custom', value=f'✅', inline=True)
    if attributes != "":
        embed.add_field(name='Attributes', value=f'{attributes}', inline=True)
    return embed


class ItemCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author is None:
            return
        global itemlist
        global regexmatch
        embeds = []
        msg = message.content
        ctx = await self.client.get_context(message)
        items = []
        if all(x in msg for x in regexmatch):
            items = re.findall('(?<=\[\[)(.*?)(?=\]\])', msg)
            if items[0].lower() == "market":
                smmoid = discordLookup(message.author.id)
                if smmoid != -1:
                    await message.channel.send(f"{message.author.mention}'s Market", components=[
                        Button(style=5, label="Market",
                               url=f'https://web.simple-mmo.com/market/listings?user_id={smmoid}&new_page=true')])
                else:
                    await message.channel.send("Unable to find linked account, please `~verify`", delete_after=10)
                return
            elif items[0].lower() in ["myavatar", "myava", "ava"]:
                smmoid = discordLookup(message.author.id)
                if smmoid != -1:
                    with open(f'{dir}/datalog/{date.today()}.txt', 'r') as f:
                        userdata = json.load(f)
                    if str(smmoid) in userdata.keys():
                        pilImage = Image.open(
                            requests.get(f'https://web.simple-mmo.com{userdata[str(smmoid)]["avatar"]}',
                                         stream=True).raw)
                        if pilImage.size[0] < 50:
                            pilImage = pilImage.resize((pilImage.size[0] * 4, pilImage.size[1] * 4), Image.ANTIALIAS)
                        else:
                            pilImage = pilImage.resize((pilImage.size[0] * 3, pilImage.size[1] * 3), Image.ANTIALIAS)
                        with BytesIO() as image_binary:
                            pilImage.save(image_binary, 'GIF')
                            image_binary.seek(0)
                            await message.channel.send(file=discord.File(fp=image_binary, filename='avatar.gif'))
                else:
                    await message.channel.send("Unable to find linked account, please `~verify`", delete_after=10)
                return
            else:
                if message.author.id in blacklist:
                    return
                if message.guild.id in guild_blacklist:
                    return

                mydb = mysql.connector.connect(
                    host=mysql_host,
                    user=mysql_user,
                    password=mysql_password,
                    database="smmo"
                )
                mycursor = mydb.cursor()
                for iName in items:
                    iName = html.escape(iName.lower(), quote=True).replace("&#x27;", "&#039;")
                    mycursor.execute(f'SELECT * FROM Items2 WHERE LOWER(name)="{iName}"')
                    results = mycursor.fetchall()
                    if len(results) > 0:
                        if results[0][12] == 0:
                            embed = createItemEmbed(results[0])
                        else:
                            embed = createItemEmbed(results[-1])
                        embeds.append(embed)
                mydb.close()
                if len(embeds) == 0:
                    return
                if len(embeds) == 1:
                    await message.channel.send(embed=embeds[0])
                else:
                    await paginate(ctx, embeds)

    @commands.command()
    @commands.check(checkBlacklist)
    async def item(self, ctx, id: int):
        if id <= 0 or id >= 100000:
            await ctx.send("Unable to locate item.")
            await ctx.message.add_reaction("❌")
            return
        data = getIndex(id)
        if data == None or data[1] == None:
            await ctx.send("Unable to locate item.")
            await ctx.message.add_reaction("❌")
            return
        else:
            embed = createItemEmbed(data)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")

    @commands.command(aliases=["isf"])
    @commands.check(checkBlacklist)
    async def itemSearchFilter(self, ctx):
        await ctx.send("Please check out: https://smmo-db.com/items/search")
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["is"])
    @commands.check(checkBlacklist)
    async def itemSearch(self, ctx, *, query: str):
        await ctx.send("Please check out: https://smmo-db.com/items/search")
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.check(checkBlacklist)
    async def toggleItems(self, ctx):
        global blacklist
        if ctx.author.id in blacklist:
            blacklist.remove(ctx.author.id)
            await ctx.send("Enabled Context Items")
        else:
            blacklist.append(ctx.author.id)
            await ctx.send("Disabled Context Items")

        with open(f'{dir}/blacklist/items.txt', 'w') as f:
            json.dump(blacklist, f)

    @commands.command()
    @commands.check(checkBlacklist)
    @commands.has_permissions(manage_guild=True)
    async def toggleGuildItems(self, ctx):
        global guild_blacklist
        if ctx.guild.id in guild_blacklist:
            guild_blacklist.remove(ctx.guild.id)
            await ctx.send("Enabled Guild Context Items")
        else:
            guild_blacklist.append(ctx.guild.id)
            await ctx.send("Disabled Guild Context Items")

        with open(f'{dir}/blacklist/guild_items.txt', 'w') as f:
            json.dump(guild_blacklist, f)


def setup(client):
    client.add_cog(ItemCog(client))
