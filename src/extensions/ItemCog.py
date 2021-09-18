import discord
from discord.ext import tasks, commands
import sqlite3
import re
import json
from extensions.BlacklistCog import checkBlacklist
from disputils import BotEmbedPaginator

dir = CURRENT_WORKING_DIRECTORY
con = sqlite3.connect(f'{dir}/data/items/smmo.db')
cur = con.cursor()
regexmatch=["[[", "]]"]

with open(f'{dir}/blacklist/items.txt', 'r') as f:
    blacklist = json.load(f)

with open(f'{dir}/blacklist/guild_items.txt', 'r') as f:
    guild_blacklist = json.load(f)

def getIndex(row:int):
    cur.execute(f'SELECT * FROM Items WHERE "ItemID"={row}')
    data = cur.fetchall()[0]
    return data


async def paginate(ctx, embeds):
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()


def createItemListEmbed(data):
    index = 0
    embeds = []
    chunks = [data[x:x+10] for x in range(0, len(data), 10)]
    for ilist in chunks:
        output = ""
        for item in ilist:
            output += f'[[{int(item[0])}](https://web.simple-mmo.com/item/inspect/{int(item[0])}?new_page=true)] {item[1]} - Level {int(item[5])}\n'
        embed = discord.Embed(
            title="Item Search Results",
            description=output,
            color=152162
        )
        embeds.append(embed)
    return embeds


def createItemEmbed(data):
    attributes = ""
    index = [8,10,12]
    colors = {"Common":discord.Color.light_grey(), "Uncommon": discord.Color.blue(), "Rare": discord.Color.orange(), "Elite": discord.Color.red(), "Epic": discord.Color.blurple(), "Legendary": discord.Color.from_rgb(255,255,0), "Celestial": discord.Color.from_rgb(0,255,255)}
    if data[6] in colors.keys():
        color = colors[data[6]]
    else:
        color = discord.Color.default()
    for i in index:
        if data[i] != "none":
            if data[i] == "crit":
                attributes += f' {data[i]} +{data[i+1]}%'
            elif data[i] != None:
                attributes += f' {data[i]} +{format(int(data[i+1]), ",d")}'
    embed = discord.Embed(
        title=data[1],
        url='https://web.simple-mmo.com/item/inspect/'+ f'{int(data[0])}' + f'?new_page=true',
        description=f'SMMO Item ID: {int(data[0])}\nLast Updated: <t:{data[22]}:f>\nDescription: {data[3]}',
        color=color
    )
    if data[2] == "Background":
        embed.set_image(url=f"https://web.simple-mmo.com{data[17]}")
    else:
        embed.set_thumbnail(url=f"https://web.simple-mmo.com{data[17]}")
    embed.add_field(name='Type', value=f'{data[2]}', inline=True)
    embed.add_field(name='Level', value=f'{format(int(data[4]), ",d")}', inline=True)
    embed.add_field(name='Required Level', value=f'{format(int(data[4]), ",d")}', inline=True)
    embed.add_field(name='Rarity', value=f'{data[6]}', inline=True)
    embed.add_field(name='Value',value=f'{format(int(data[7]), ",d")}', inline=True)
    embed.add_field(name='Circulation', value=f'{format(int(data[18]), ",d")} Items', inline=True)
    embed.add_field(name='Market', value=f'{format(int(data[19]), ",d")} Items', inline=True)
    embed.add_field(name='Market Value', value=f'{format(int(data[20]), ",d")} - {format(int(data[21]), ",d")} Gold', inline=True)
    if int(data[14]) == 0:
        embed.add_field(name='Custom', value=f'❌', inline=True)
    else:
        embed.add_field(name='Custom', value=f'✅', inline=True)
    if attributes == "":
        embed.add_field(name='Attributes', value=f'`N/A`', inline=True)
    else:
        embed.add_field(name='Attributes', value=f'{attributes}', inline=True)
    return embed

class ItemCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author is None:
            return
        if message.author.id in blacklist:
            return
        if message.guild.id in guild_blacklist:
            return
        global itemlist
        global regexmatch
        embeds = []
        msg = message.content
        ctx = await self.client.get_context(message)
        items = []
        if all(x in msg for x in regexmatch):
            items = re.findall('(?<=\[\[)(.*?)(?=\]\])', msg)
            for iName in items:
                iName=iName.lower()
                cur.execute(f'SELECT * FROM Items WHERE LOWER("Name")="{iName}"')
                results = cur.fetchall()
                if len(results) > 0:
                    embed = createItemEmbed(results[0])
                    embeds.append(embed)
            if len(embeds) == 0:
                return
            if len(embeds) == 1:
                await message.channel.send(embed=embeds[0])
            else:
                await paginate(ctx, embeds)

    @commands.command()
    @commands.check(checkBlacklist)
    async def item(self, ctx, id:int):
        if id <= 0 or id >= 60000:
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
        await ctx.send(f'Filters include: String `type`, Integer `level`, String `rarity`, Integer `stat`, String `stat-type`, Boolean `custom`\ne.g. `~itemsearch "itemname" --type=weapon --rarity=common --stat=1000 --stat-type=str --custom=false`')
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["is"])
    @commands.check(checkBlacklist)
    async def itemSearch(self, ctx, *, query:str):
        custom = -1
        keywords = ["type", "level", "rarity", "stat", "stat-type"]
        raritytypes = ["common", "uncommon", "elite", "rare", "legendary", "celestial", "exotic"]
        stattypes = ["str", "def", "crit", "hp"]
        querylist = []
        itemname = ""

        if query.count("\"") == 2:
            itemname = "'%"+ re.search(r'\"(.+?)\"', query)[0][1:-1].strip() + "%'"
            resquery = query.split("\"")[2]
        elif query.count("\"") >= 2:
            await ctx.send('Unable to parse query. Please use keywords to phrase query\ni.e. `~itemsearch "itemname" --type=weapon --rarity=common --stat=1000 --stat-type=str --custom=false`')
            await ctx.message.add_reaction("❌")
            return
        else:
            resquery = query

        if "--" in resquery:
            restrictions = query.strip().replace(" ", "").lower().split("--")
        elif "--" not in resquery and itemname == "":
            await ctx.send('Unable to parse query. Please use keywords to phrase query\ni.e. `~itemsearch "itemname" --type=weapon --rarity=common --stat=1000 --stat-type=str --custom=false`')
            await ctx.message.add_reaction("❌")
            return
        else:
            restrictions = []
        if len(restrictions) != 0:
            for restriction in restrictions:
                if restriction.startswith("rarity"):
                    if restriction.split("=")[1] not in raritytypes:
                        continue
                    else:
                        querylist.append(f'LOWER("Rarity")="{restriction[7:]}"')
                elif restriction.startswith("type"):
                    querylist.append(f'LOWER("Type")="{restriction[5:]}"')
                elif restriction.startswith("stat-type"):
                    if restriction.split("=")[1] not in stattypes:
                        continue
                    else:
                        querylist.append(f'LOWER("Stat1")="{restriction[10:]}"')
                elif restriction.startswith("level"):
                    querylist.append(f'"Level"{restriction[5]}"{restriction[6:]}"')
                elif restriction.startswith("stat"):
                    if any(substring in restriction for substring in [">=", "<="]):
                        querylist.append(f'"Stat1-Value"{restriction[4:5]}"{restriction[6:]}"')
                    else:
                        querylist.append(f'"Stat1-Value"{restriction[4]}"{restriction[5:]}"')
                elif restriction.startswith("custom"):
                    if restriction[7:] == "true":
                        querylist.append(f'"Custom"=1')
                        custom = 1
                else:
                    continue
        if custom == -1:
            querylist.append(f'"Custom"=0')

        if itemname != "" and len(restrictions) != 0:
            final_query = f'SELECT * FROM Items WHERE "name" LIKE {itemname} AND ' + ' AND '.join(querylist)
        elif itemname != "" :
            final_query = f'SELECT * FROM Items WHERE "name" LIKE {itemname} AND "Custom"=0'
        else:
            final_query = f'SELECT * FROM Items WHERE ' + ' AND '.join(querylist)
        try:
            cur.execute(final_query)
            results = cur.fetchall()
            if len(results) == 0:
                await ctx.send("No Items Found")
                await ctx.message.add_reaction("❌")
                return
            elif len(results) == 1:
                embed = createItemEmbed(results[0])
                await ctx.send(embed=embed)
                await ctx.message.add_reaction("✅")
            else:
                embeds = createItemListEmbed(results)
                if len(embeds) >= 1:
                    await paginate(ctx, embeds)
                else:
                    await ctx.send(embed=embed)
                await ctx.message.add_reaction("✅")
        except Exception as e:
            print(f'ItemCog - {e}')
            await ctx.message.add_reaction("❌")
            return

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
