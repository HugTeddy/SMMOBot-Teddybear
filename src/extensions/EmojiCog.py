from discord.ext import commands
import discord
import json

dir = CURRENT_WORKING_DIRECTORY
botID = DISCORD_BOT_ID
pmChannel = DISCORD_LOG_CHANNEL

with open(f'{dir}/blacklist/emoji.txt', 'r') as f:
    blacklist = json.load(f)

with open(f'{dir}/blacklist/guild_emoji.txt', 'r') as f:
    guild_blacklist = json.load(f)

class EmojiCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        global blacklist
        if message.guild is None or message.author is None:
            if message.channel.type == discord.ChannelType.private and message.author.id != botID:
                try:
                    channel = self.client.get_channel(pmChannel)
                    await channel.send(f'{message.author.name}: {message.content}')
                except:
                    return
                return
            return
        if message.author.id in blacklist:
            return
        if message.guild.id in guild_blacklist:
            return
        EmojiList=list(message.guild.emojis)
        for item in EmojiList:
            if item.name == message.content:
                await message.channel.send(str(item))
                return

    @commands.command()
    async def toggleEmoji(self, ctx):
        global blacklist
        if ctx.author.id in blacklist:
            blacklist.remove(ctx.author.id)
            await ctx.send("Enabled Context Emojis")
        else:
            blacklist.append(ctx.author.id)
            await ctx.send("Disabled Context Emojis")

        with open(f'{dir}/blacklist/emoji.txt', 'w') as f:
            json.dump(blacklist, f)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def toggleGuildEmoji(self, ctx):
        global guild_blacklist
        if ctx.guild.id in guild_blacklist:
            guild_blacklist.remove(ctx.guild.id)
            await ctx.send("Enabled Guild Context Emojis")
        else:
            guild_blacklist.append(ctx.guild.id)
            await ctx.send("Disabled Guild Context Emojis")

        with open(f'{dir}/blacklist/guild_emoji.txt', 'w') as f:
            json.dump(guild_blacklist, f)

def setup(client):
    client.add_cog(EmojiCog(client))
