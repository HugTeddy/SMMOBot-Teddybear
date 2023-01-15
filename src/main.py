import configparser
import json
import os
import traceback
from datetime import timedelta, datetime
from discord import app_commands
import discord
from discord.ext import commands

def get_prefix(client, message):
    with open('prefix.txt', 'r') as f:
        prefixes = json.load(f)
    if message.guild is None:
        return '~'
    if str(message.guild.id) not in prefixes.keys():
        return '~'
    return prefixes[str(message.guild.id)]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('DEFAULT', 'Token')
api_key = config.get('DEFAULT', 'Api_Key')
bot_owner = int(config.get('DEFAULT', 'Bot_Owner'))

@client.command()
async def reload(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    await client.unload_extension(f'extensions.{extension}')
    await client.load_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.command()
async def load(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    await client.load_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.command()
async def unload(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    await client.unload_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            name='SimpleMMO', type=discord.ActivityType.competing))
    channel = client.get_channel(00000000000000000000)
    await channel.send("[🟢] Bot Connected")
    print('Bot is ready.')

@client.command()
async def loadCogs(ctx):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Missing Permissions')
        return
    for filename in os.listdir('./extensions'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'extensions.{filename[:-3]}')
            except:
                await ctx.send(f'Error Loading: {filename}')
    await ctx.message.add_reaction("✅")

@client.event
async def on_guild_join(guild):
    with open('prefix.txt', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '~'
    with open('prefix.txt', 'w') as f1:
        json.dump(prefixes, f1)

@client.event
async def on_guild_remove(guild):
    with open('prefix.txt', 'r') as f:
        prefixes = json.load(f)
    del prefixes[str(guild.id)]
    with open('prefix.txt', 'w') as f1:
        json.dump(prefixes, f1)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.add_reaction("❌")
        await ctx.send('Missing required arguments!', delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction("❓")
        await ctx.send('Invalid Command!', delete_after=10)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.message.add_reaction("❌")
        await ctx.send('Missing Permissions!', delete_after=10)
    elif isinstance(error, commands.MissingRole):
        await ctx.message.add_reaction("❌")
        await ctx.send('Missing Role!', delete_after=10)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.message.add_reaction("❌")
        await ctx.send(f'Retry in {str(timedelta(seconds=round(error.retry_after)))}')
    elif isinstance(error, commands.BadArgument):
        await ctx.message.add_reaction("❌")
        await ctx.send('Incorrect Parameters', delete_after=5)
    elif isinstance(error, commands.CheckFailure):
        await ctx.message.add_reaction("❌")
    elif isinstance(error, OSError):
        await ctx.message.add_reaction("❌")
        if datetime.now().hour == 0:
            await ctx.send('Data is processing for SimpleMMO daily reset... Please try again later.', delete_after=10)
        else:
            await ctx.send('Data has not yet loaded... Please try again later.', delete_after=10)
    else:
        await ctx.send('An error occurred, if persistent please check out our Discord Support Server `^aboutme`.', delete_after=60)
        embed = discord.Embed(title=':x: Command Error', colour=0xe74c3c)
        embed.add_field(name='Error', value=error)
        embed.add_field(name='Author', value=str(ctx.author.name))
        if ctx.guild:
            embed.add_field(name='Guild', value=str(ctx.guild.name))
        embed.description = '```py\n%s\n```' % traceback.format_exc()
        embed.timestamp = datetime.utcnow()
        with open("/home/teddybear/errorlog/errors.txt", "a") as f:
            f.write(f'{error}\n')
        app_info = await client.application_info()
        await app_info.owner.send(embed=embed)

@client.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c)
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.utcnow()
    AppInfo = await client.application_info()
    await AppInfo.owner.send(embed=embed)

@client.command()
@commands.has_permissions(manage_guild=True)
async def changeprefix(ctx, prefix):
    with open('prefix.txt', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefix.txt', 'w') as f1:
        json.dump(prefixes, f1)
    await ctx.message.add_reaction("✅")

@client.command()
async def botstop(ctx):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    await ctx.send('Bye Bye')
    await client.close()

@client.command()
async def guildList(ctx):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    output = "Current Guilds:\n"
    for item in client.guilds:
        output += f'- {str(item.name)} ID: {str(item.id)}\n'
        if len(output) > 1500:
            await ctx.send(output)
            output = ""
    await ctx.send(output)

@commands.command()
async def syncCommands(ctx):
    if ctx.author.id == bot_owner:
        await client.tree.sync()
        await ctx.message.add_reaction("✅")
    else:
        await ctx.send("Error")

client.run(token)

