from discord.ext import commands
import discord
import random

dir = CURRENT_WORKING_DIRECTORY

def getrandom(afile):
    lines = afile.read().splitlines()
    return random.choice(lines)

def createPictureEmbed(type, user, link):
    embed = discord.Embed(
        title=f'{type}',
        description='',
        color=discord.Colour.purple()
        )
    embed.set_image(url=link)
    embed.set_footer(text="Command invoked by {}".format(user.display_name))
    return embed

def createEmoteEmbed(type, user1, user2, link):
    embed = discord.Embed(
        title=f'{user1.display_name} {type} {user2.display_name}',
        description='',
        color=discord.Colour.purple()
        )
    embed.set_image(url=link)
    return embed

def isAuction(ctx):
    if ctx.guild.id == 730461551097806949:
        return False
    return True

class EmoteCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(isAuction)
    async def bunny(self, ctx):
        with open(dir + 'bunny.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Bunny", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def cat(self, ctx):
        with open(dir + 'cat.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Cat", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def dog(self, ctx):
        with open(dir + 'dog.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Dog", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def duck(self, ctx):
        with open(dir + 'duck.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Duck", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def wolf(self, ctx):
        with open(dir + 'wolf.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Wolf", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def deer(self, ctx):
        with open(dir + 'deer.txt', 'r') as f:
            link = getrandom(f)
        embed = createPictureEmbed("Deer", ctx.author, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def hug(self, ctx, user: discord.User):
        with open(dir + 'hug.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("hugs", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def kill(self, ctx, user: discord.User):
        with open(dir + 'kill.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("murders", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def kiss(self, ctx, user: discord.User):
        with open(dir + 'kiss.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("kisses", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def pat(self, ctx, user: discord.User):
        with open(dir + 'pat.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("pats", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def poke(self, ctx, user: discord.User):
        with open(dir + 'poke.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("pokes", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isAuction)
    async def wave(self, ctx, user: discord.User):
        with open(dir + 'wave.txt', 'r') as f:
            link = getrandom(f)
        embed = createEmoteEmbed("waves at", ctx.author, user, link)
        await ctx.message.delete()
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(EmoteCog(client))
