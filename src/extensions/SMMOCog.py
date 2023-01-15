import configparser
import json
import discord
from discord import app_commands
from discord.ext import commands
from extensions.BlacklistCog import checkBlacklist
from extensions.util.datautil import discordLookup

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('DEFAULT', 'api_key')
email = config.get('SMMO', 'email')
password = config.get('SMMO', 'password')


def formatID(uuid, gid):
    isID = False
    if "<@" in uuid:
        uuid = uuid[2:-1]
        if "!" in uuid:
            uuid = uuid[1:]
        isID = True
    elif not uuid.isdigit():
        uuid = -1
        return uuid
    elif int(uuid) > 999999:
        isID = True

    with open(f'/home/teddybear/bot/data/{gid}/users.txt', 'r') as f:
        data = json.load(f)

    if isID:
        if str(uuid) in data:
            uuid = data[f'{uuid}']
            return uuid
        uuid = discordLookup(uuid)
        return uuid
    else:
        return uuid


class SMMOCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ctx_trade = app_commands.ContextMenu(
            name='[SMMO] Trade Menu',
            callback=self.context_trade,  # set the callback of the context menu to "my_cool_context_menu"
        )
        self.ctx_web = app_commands.ContextMenu(
            name='[SMMO] Web Profile',
            callback=self.context_web,  # set the callback of the context menu to "my_cool_context_menu"
        )
        self.client.tree.add_command(self.ctx_trade)
        self.client.tree.add_command(self.ctx_web)

    async def context_web(self, interaction: discord.Interaction, user: discord.User):
        with open(f'/home/teddybear/bot/data/{interaction.guild_id}/users.txt', 'r') as f:
            data = json.load(f)

        if str(user.id) not in data:
            userid = discordLookup(user.id)
            if userid == -1:
                await interaction.response.send_message('Unable to find linked profile.', ephemeral=True)
                return
        else:
            userid = data[str(user.id)]

        msg = "https://simplemmo.me/users/data/u" + str(userid) + ".html"
        await interaction.response.send_message(msg, ephemeral=True)

    async def context_trade(self, interaction: discord.Interaction, user1: discord.User):
        user2 = interaction.user
        user1id = formatID(f'<@{user1.id}>', interaction.guild.id)
        user2id = formatID(f'<@{user2.id}>', interaction.guild.id)
        goldurl = "https://simplemmo.me/mobile?page=sendgold/"
        itemurl = "https://simplemmo.me/mobile?page=inventory?sendid="
        messageurl = "https://simplemmo.me/mobile?page=chat/private?user_id="
        tradeurl = "https://simplemmo.me/mobile?page=trades/view-all?user_id="
        embed = discord.Embed(
            title=f'Trade Board',
            description=f"{user1.mention}",
            color=1623534
        )
        embed.add_field(name=f'[{user1id}] {user1.display_name}',
                        value=f'[Send Message]({messageurl}{user1id}?new_page=true) | [Send Gold]({goldurl}{user1id}) | [Send Item]({itemurl}{user1id}) | [Trade]({tradeurl}{user1id})',
                        inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @commands.hybrid_command(name="trade", brief='Opens Trade Menu w/ Player', aliases=["t"], with_app_command=True)
    @commands.check(checkBlacklist)
    async def trade(self, ctx, user1: discord.Member):
        user2 = ctx.author
        user1id = formatID(f'<@{user1.id}>', ctx.guild.id)
        user2id = formatID(f'<@{user2.id}>', ctx.guild.id)
        goldurl = "https://simplemmo.me/mobile?page=sendgold/"
        itemurl = "https://simplemmo.me/mobile?page=inventory?sendid="
        messageurl = "https://simplemmo.me/mobile?page=chat/private?user_id="
        tradeurl = "https://simplemmo.me/mobile?page=trades/view-all?user_id="
        embed = discord.Embed(
            title=f'Trade Board',
            description=f"{user1.mention} | {user2.mention}",
            color=1623534
        )
        embed.add_field(name=f'[{user1id}] {user1.display_name}',
                        value=f'[Send Message]({messageurl}{user1id}?new_page=true) | [Send Gold]({goldurl}{user1id}) | [Send Item]({itemurl}{user1id}) | [Trade]({tradeurl}{user1id})',
                        inline=False)
        embed.add_field(name=f'[{user2id}] {user2.display_name}',
                        value=f'[Send Message]({messageurl}{user2id}?new_page=true) | [Send Gold]({goldurl}{user2id}) | [Send Item]({itemurl}{user2id}) | [Trade]({tradeurl}{user2id})',
                        inline=False)
        await ctx.send(embed=embed)
        if not ctx.interaction:
            await ctx.message.add_reaction("✅")

async def setup(client):
    await client.add_cog(SMMOCog(client))