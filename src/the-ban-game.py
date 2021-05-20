import sys
import os
import json
import itertools
from requests import get
from random import randint
from twitchio.ext import commands

# Set-up the bot
bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)
STREAMER_NAME = os.environ['BOT_NICK']

# Game emotes
IMG_HIT = 'HypeHit'
IMG_MISS = 'HypeMiss'
IMG_RIP = 'HypeRIP'
IMG_HEALTH = 'HypeHeart'
IMG_SPELL = 'HypeMage'
IMG_REVIVE = 'arighiPastaDance'
IMG_EVIL = 'HypeRogue'
IMG_FAIL = 'HypeWho'
IMG_NONE = 'HypeLol'
IMG_CRIT = 'HypeTarget'

# Player's stats
INITIAL_HP = 50

players = {
}

@bot.event
async def event_ready():
    print(f"{os.environ['BOT_NICK']} is online!")

@bot.event
async def event_message(msg):
    if IMG_REVIVE in msg.content:
        # Heal player if the message contains the IMG_REVIVE emote
        player = msg.author.name
        init_player(player)
        if msg.author.is_subscriber:
            players[player] = min(players[player] + 1, INITIAL_HP)
    await bot.handle_commands(msg)

def init_player(player):
    if player not in players:
        players[player] = INITIAL_HP

def parse_args(ctx, command):
    return ctx.message.content.lower().removeprefix(command).strip().strip('@').split(' ')[0]

def is_valid_user(name):
    if name == '':
        return False
    r = get(f'http://tmi.twitch.tv/group/user/{STREAMER_NAME}/chatters')
    users = json.loads(r.text)['chatters']
    return name in itertools.chain.from_iterable([users[i] for i in users])

@bot.command(name='life')
async def life(ctx):
    player = ctx.author.name
    target = parse_args(ctx, '!life')

    if target != '' and not is_valid_user(target):
        await ctx.send(f"@{player} is trying to inspect someone that has long left the area {IMG_NONE}")
        return

    init_player(player)
    if is_valid_user(target):
        init_player(target)
    else:
        target = player

    if players[target] == 0:
        await ctx.send(f"@{target} is banned {IMG_RIP}")
    else:
        await ctx.send(f"@{target} has {players[target]} {IMG_HEALTH} left")

@bot.command(name='unban')
async def unban(ctx):
    player = ctx.author.name
    target = parse_args(ctx, '!unban')

    if not is_valid_user(target):
        await ctx.send(f"@{player} casts unban at someone that has long left the area {IMG_NONE}")
        return

    init_player(player)
    init_player(target)

    if ctx.author.is_mod:
        players[target] = INITIAL_HP
        if player == target:
            await ctx.send(f"@{target} self-heals back to {players[target]} {IMG_HEALTH}")
        else:
            await ctx.send(f"@{target} has been fully healed to {players[target]} {IMG_HEALTH}")
        return
    if players[player] == 0:
        await ctx.send(f"@{player} tried to cast healing from the realm of the banned {IMG_RIP}")
        return

    await ctx.send(f"@{player} spectacularly fails at casting an ancient healing spell that they haven't practiced enough {IMG_FAIL}")

    players[player] = max(players[player] - 1, 0)
    if players[player] == 0:
        await ctx.send(f"@{player} died trying to cast healing at {target} {IMG_RIP}")

@bot.command(name='ban')
async def ban(ctx):
    player = ctx.author.name
    target = parse_args(ctx, '!ban')

    if not is_valid_user(target):
        await ctx.send(f"@{player} casts ban at someone that has long left the area {IMG_NONE}")
        return

    init_player(target)
    init_player(player)

    # Check if player is dead
    if players[player] == 0:
        await ctx.send(f"@{player} shakes his fist from the realm of the banned {IMG_RIP}")
        return
    # Check if target is dead
    if players[target] == 0:
        await ctx.send(f"@{player} is beating the dead body of a banned @{target} {IMG_EVIL}")
        return

    # Generate the damage (D20 roll)
    damage = randint(1, 20)
    if damage == 1:
        damage = 0
    elif damage == 20:
        damage = 40
        await ctx.send(f"{player} {IMG_CRIT} CRITICAL HIT {IMG_CRIT}")

    # Get some damage back
    rand_perc = randint(10, 25)
    dmg_back = 1 + int(damage * rand_perc / 100)
    players[player] = max(players[player] - dmg_back, 0)
    await ctx.send(f"@{player} uses {dmg_back} life to cast the ban spell {IMG_SPELL}")
    if players[player] == 0:
        await ctx.send(f"@{player} died casting ban on @{target} {IMG_RIP}")
        return

    # Apply damage to target
    if damage > 0:
        players[target] = max(players[target] - damage, 0)
        await ctx.send(f"@{player} deals {damage} BAN damage to @{target} {IMG_HIT}")
        await ctx.send(f"@{player} {players[player]} / @{target} {players[target]} {IMG_HEALTH}")
        if players[target] == 0:
            await ctx.send(f"@{target} has been banned by @{player} {IMG_RIP}")
    else:
        await ctx.send(f"@{player} raises his hands to cast ban on @{target}. Everyone is holding their breath to see how this battle turns out... but @{target} ducks just in time for the spell to miss them {IMG_MISS}")

if __name__ == "__main__":
    bot.run()
