import discord
from discord.ext import tasks, commands
from datetime import date
from bs4 import BeautifulSoup
from lxml import html
import urllib
import requests
import random
import json
from re import search
import string
import configparser
from extensions.BlacklistCog import checkBlacklist
from disputils import BotEmbedPaginator


dir = CURRENT_WORKING_DIRECTORY

config = configparser.ConfigParser()
config.read(f'{dir}/config.ini')
email = config.get('SMMO', 'email')
password = config.get('SMMO', 'password')

async def paginate(ctx, embeds):
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()

def createLeaderboardEmbed(data, icon, board, boardint):
    types = ["daily", "weekly", "monthly", "all"]
    embeds = []
    typeindex = 0
    for i in data:
        output = ""
        index = 1
        for user in i:
            output+= f'{index}. [{user[0]}](https://web.simple-mmo.com{user[3]}) - {user[2]}\n'
            index += 1
        embed = discord.Embed(
            title=f'{board.title()} - {types[typeindex].title()}',
            url=f'https://web.simple-mmo.com/battlearena?leaderboards_arena={boardint}',
            description=output,
            color=1612333
        )
        embed.set_thumbnail(url=icon)
        embeds.append(embed)
        typeindex += 1
    return embeds

class ArenaCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["bal"])
    @commands.cooldown(1, 60.0, commands.BucketType.user)
    async def baleaderboard(self, ctx, *, board):
        types = ["daily", "weekly", "monthly", "all"]
        boards = {"copper":1, "bronze":2, "silver":3, "gold":4, "platinum":5, "titanium":6, "7th circle":7, "ragnarok":8, "mount olympus":9, "rapture":10, "nirvana":11}
        boardicon = {"copper":"https://web.simple-mmo.com/img/icons/battlearena/1.png", "bronze":"https://web.simple-mmo.com/img/icons/battlearena/2.png", "silver":"https://web.simple-mmo.com/img/icons/battlearena/3.png", "gold":"https://web.simple-mmo.com/img/icons/battlearena/4.png", "platinum":"https://web.simple-mmo.com/img/icons/battlearena/5.png", "titanium":"https://web.simple-mmo.com/img/icons/battlearena/6.png", "7th circle":"https://web.simple-mmo.com/img/icons/S_Fire08.png", "ragnarok":"https://web.simple-mmo.com/img/icons/two/32px/RuneStone17_32.png", "mount olympus":"https://web.simple-mmo.com/img/icons/S_Earth07.png", "rapture":"https://web.simple-mmo.com/img/icons/one/icon174.png", "nirvana":"https://web.simple-mmo.com/img/icons/one/icon130.png"}
        if board.lower() not in list(boards.keys()):
            await ctx.send("Invalid BA League")
            await ctx.message.add_reaction("❌")
            return
        board = board.lower()
        icon = boardicon[board]
        tempmsg = await ctx.send("Fetching data...")
        session_requests = requests.session()
        login_url = "https://web.simple-mmo.com/login"
        result = session_requests.get(login_url)
        tree = BeautifulSoup(result.text, features="lxml")
        authenticity_token = tree.find('input', {"type":"hidden", "name":"_token"})['value']
        payload = {
            "email": email,
            "password": password,
            "_token": authenticity_token
        }
        result = session_requests.post(
            login_url,
            data = payload,
            headers = dict(referer=login_url)
        )
        data = []
        for type in types:
            leaderboard = []
            url = f'https://web.simple-mmo.com/battlearena?leaderboards_arena={str(boards[board])}&leaderboards_time={type}'
            result = session_requests.get(
                url,
                headers = dict(referer = url)
            )
            soup = BeautifulSoup(result.text, features="lxml")
            players = list(soup.findAll('li', {"class":"py-4 flex"}))
            for i in players:
                user = i.find('a')
                url = user['href']
                username = user.text.strip().replace("\n", "")
                userid = str(user['href']).split("/")[3]
                kills = list(i.findAll('p'))[1].text
                userdata = [username, userid, kills, url]
                leaderboard.append(userdata)
            data.append(leaderboard)
        await tempmsg.delete()
        embeds = createLeaderboardEmbed(data, icon, board, boards[board])
        await paginate(ctx, embeds)
        await ctx.message.add_reaction("✅")


def setup(client):
    client.add_cog(ArenaCog(client))
