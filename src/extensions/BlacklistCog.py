import discord
from discord.ext import tasks, commands
import json

dir = CURRENT_WORKING_DIRECTORY

async def checkBlacklist(ctx):
    with open(f'{dir}/blacklist/blacklist.txt', 'r') as f:
        data = json.load(f)
    if ctx.author.id in data:
        await ctx.send("Your account has been flagged!")
        return False
    else:
        return True

class BlacklistCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ban(self, ctx, user: discord.Member):
        with open(f'{dir}/blacklist/blacklist.txt', 'r') as f:
            data = json.load(f)

        data.append(user.id)

        with open(f'{dir}/blacklist/blacklist.txt', 'w') as f:
            json.dump(data, f)

        await ctx.message.delete()

    @commands.command()
    async def unban(self, ctx, user: discord.Member):
        with open(f'{dir}/blacklist/blacklist.txt', 'r') as f:
            data = json.load(f)

        if user.id in data:
            data.remove(user.id)
            with open(f'{dir}/blacklist/blacklist.txt', 'w') as f:
                json.dump(data, f)
            await ctx.message.delete()
        else:
            await ctx.send("Invalid User", delete_after=5)
            await ctx.message.delete()

def setup(client):
    client.add_cog(BlacklistCog(client))
