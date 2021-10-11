from discord.ext import tasks, commands
import discord
import random
import json
import math
import asyncio
import sqlite3
from discord.utils import get
from disputils import BotConfirmation, BotMultipleChoice
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)


async def confirm(ctx, game, challenger, user, bet):
    confirmation = BotConfirmation(ctx, 0x012345)
    if bet == None:
        await confirmation.confirm(f'Would you like to accept this challenge?\nGame: `{game}`\nChallenger: `{challenger.display_name}`', user)
    else:
        await confirmation.confirm(f'Would you like to accept this challenge?\nGame: `{game}`\nChallenger: `{challenger.display_name}`\nBet: `{bet}`', user)
    if confirmation.confirmed:
        if bet != None:
            await confirmation.update(f"Confirmed\nGame: `{game}`\nChallenger: `{challenger.display_name}`\nBet: `{bet}`", color=0x55ff55)
        else:
            await confirmation.update("Confirmed", color=0x55ff55)
        return True
    else:
        await confirmation.update("Not confirmed", color=0xff5555)
        return False

def createDREmbed(player, user, author, roll, status):
    embed = discord.Embed(
        title=f'{author.display_name} vs. {user.display_name} - Death Roll',
        description=f'Game Status: {status}\n{player.mention} has rolled a `{roll}`',
        color=156236
    )
    return embed

async def choice(ctx, user):
    choice = BotMultipleChoice(ctx, ["Heads","Tails"], f"{user.display_name}'s Coin Flip", closeable = False)
    res = await choice.run([user])
    await res[1].delete()
    if res[0] == "Heads":
        return 1
    else:
        return 0

def convert(val):
    try:
        val = float(val)
    except ValueError:
        lookup = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        unit = val[-1]
        try:
            number = float(val[:-1])
        except ValueError:
            return 'Null'
        if unit in lookup:
            return lookup[unit] * number
        return float(val)
    return val

class CoinCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.current_games = {}
        self.button_enabled = [
                    Button(style=ButtonStyle.green, label="Roll"),
                    Button(style=ButtonStyle.red, label="Forfeit"),
                    Button(style=ButtonStyle.grey, label="Close")
                ]
        self.button_disabled = [
                    Button(style=ButtonStyle.green, label="Roll", disabled=True),
                    Button(style=ButtonStyle.red, label="Forfeit", disabled=True),
                    Button(style=ButtonStyle.grey, label="Close", disabled=True)
                ]
        self.button_listener.start()

    def cog_unload(self):
        self.button_listener.cancel()

    @tasks.loop(hours=128.0, count=1)
    async def button_listener(self):
        while True:
            res = await self.client.wait_for("button_click")
            if str(res.message.id) in self.current_games:
                curGame = self.current_games[str(res.message.id)]
                author = await self.client.fetch_user(curGame[4])
                player = await self.client.fetch_user(curGame[3])
                bet = curGame[1]
                if res.component.label == "Roll":
                    if res.user.id != curGame[2]:
                        await res.respond(
                            content=f'It is not your turn/game.', delete_after=3
                        )
                    else:
                        roll = random.randint(1, curGame[0])
                        if roll != 1:
                            await res.respond(
                                type=7, embed=createDREmbed(res.user, player, author, roll, "Ongoing"), components=[self.button_enabled]
                            )
                            if res.user == player:
                                self.current_games[str(res.message.id)] = [roll, bet, author.id, player.id, author.id]
                            else:
                                self.current_games[str(res.message.id)] = [roll, bet, player.id, player.id, author.id]
                        else:
                            if res.user == player:
                                await res.respond(
                                    type=7, embed=createDREmbed(res.user, player, author, roll, f"Final - <@{author.id}> Won!"), components=[self.button_disabled]
                                )
                            else:
                                await res.respond(
                                    type=7, embed=createDREmbed(res.user, player, author, roll, f"Final - <@{player.id}> Won!"), components=[self.button_disabled]
                                )
                            del self.current_games[str(res.message.id)]
                elif res.component.label == "Forfeit":
                    if res.user.id == author.id or res.user.id == player.id:
                        if res.user == player:
                            await res.respond(
                                type=7, embed=createDREmbed(res.user, player, author, 0, f"Final (Forfeit) - <@{author.id}> Won!"), components=[self.button_disabled]
                            )
                        else:
                            await res.respond(
                                type=7, embed=createDREmbed(res.user, player, author, 0, f"Final (Forfeit) - <@{author.id}> Won!"), components=[self.button_disabled]
                            )
                        del self.current_games[str(res.message.id)]
                    else:
                        await res.respond(
                            content=f'It is not your turn/game.', delete_after=3
                        )
                elif res.component.label == "Close":
                    if res.user.id != 151819430026936320:
                        await res.respond(
                            content=f'You are not an admin.', delete_after=3
                        )
                    else:
                        await res.respond(
                            type=7, embed=createDREmbed(res.user, player, author, 0, f"Game Closed"), components=[self.button_disabled]
                        )
                        del self.current_games[str(res.message.id)]

    @commands.command(brief='Coin Flip', aliases=["cf"])
    async def coinflip(self, ctx, user: discord.User, *, bet=None):
        if not await confirm(ctx, "Coin Flip", ctx.author, user, bet):
            await ctx.send('Player has declined your challenge.')
            await ctx.message.add_reaction("❌")
            return
        answer = random.choice([0, 1])
        result = {"0":"Tails", "1":"Heads"}
        if await choice(ctx, user) == answer:
            await ctx.send("Flipping the coin...", delete_after=3)
            await asyncio.sleep(3)
            await ctx.send(f'{user.mention} won!\nThe correct answer was `{result[str(answer)]}`')
        else:
            await ctx.send("Flipping the coin...", delete_after=3)
            await asyncio.sleep(3)
            await ctx.send(f'{ctx.author.mention} won!\nThe correct answer was `{result[str(answer)]}`')
        await ctx.message.add_reaction("✅")

    @commands.command(brief='Dice')
    async def dice(self, ctx, user: discord.User, *, bet=None):
        if not await confirm(ctx, "Dice", ctx.author, user, bet):
            await ctx.send('Player has declined your challenge.')
            await ctx.message.add_reaction("❌")
            return
        await ctx.send("Rolling D20's...", delete_after=3)
        await asyncio.sleep(3)
        user1 = random.randint(1, 20)
        user2 = random.randint(1, 20)
        await ctx.send(f'{ctx.author.mention} rolled a `{user1}`\n{user.mention} rolled a `{user2}`')
        if user1 > user2:
            await ctx.send(f'{ctx.author.mention} won!')
        elif user2 > user1:
            await ctx.send(f'{user.mention} won!')
        else:
            await ctx.send(f'It was a tie!')
        await ctx.message.add_reaction("✅")

    @commands.command(brief='Death Roll', aliases=['dr'])
    async def deathRoll(self, ctx, user: discord.User, *, bet=None):
        gamedata = self.current_games.values()
        activeplayer = []
        for game in gamedata:
            activeplayer.append(game[3])
            activeplayer.append(game[4])
        if user.id in activeplayer or ctx.author.id in activeplayer:
            await ctx.send('You or your opponent is already in a game, please finish one before starting another.')
            await ctx.message.add_reaction("❌")
            return
        elif user.id == ctx.author.id:
            await ctx.send('Find a friend to play with.')
            await ctx.message.add_reaction("❌")
            return
        else:
            if not await confirm(ctx, "Death Roll", ctx.author, user, bet):
                await ctx.send('Player has declined your challenge.')
                await ctx.message.add_reaction("❌")
                return
            roll = int(random.randint(1,100000))
            embed = createDREmbed(ctx.author, user, ctx.author, roll, "Ongoing")
            msg = await ctx.send(embed=embed, components=[self.button_enabled])
            self.current_games[str(msg.id)] = [roll, bet, user.id, user.id, ctx.author.id]
            await ctx.message.add_reaction("✅")


def setup(client):
    client.add_cog(CoinCog(client))
