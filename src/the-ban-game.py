import sys
import os
import json
import itertools
from requests import get
from random import randint
from twitchio.ext import commands
from time import time

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
IMG_LEADER = 'HypeFighter'

# Game mechanic parameters
MAX_HP = 50
BAN_COOLDOWN_SEC = 10

# Player main object
class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self._life = MAX_HP
        self.kills = 0
        self.last_ban_ts = 0
        self.weakness = 0

    def life(self):
        return self._life

    def heal(self, life):
        self._life = min(self._life + life, MAX_HP)

    def damage(self, life):
        self._life = max(self._life - life, 0)

# Store all players statistics here
players = {
}

@bot.event
async def event_ready():
    print(f"{os.environ['BOT_NICK']} is online!")

@bot.event
async def event_message(msg):
    life = msg.content.count(IMG_REVIVE)
    if life > 0:
        # Heal player if the message contains the IMG_REVIVE emote
        player = msg.author.name
        init_player(player)
        if msg.author.is_subscriber:
            players[player].heal(life)
    await bot.handle_commands(msg)

def init_player(player):
    if player not in players:
        players[player] = Player()

def parse_args(ctx, command):
    return ctx.message.content.lower().removeprefix(command).strip().strip('@').split(' ')[0]

def is_valid_user(name):
    if name == '':
        return False
    r = get(f'http://tmi.twitch.tv/group/user/{STREAMER_NAME}/chatters')
    users = json.loads(r.text)['chatters']
    return name in itertools.chain.from_iterable([users[i] for i in users])

def check_weakness(player, do_ban=False):
    delta_t = time() - players[player].last_ban_ts
    if delta_t > BAN_COOLDOWN_SEC:
        players[player].weakness = max(0, players[player].weakness - int(delta_t / BAN_COOLDOWN_SEC))
    elif do_ban:
        players[player].weakness += 1
    return players[player].weakness

@bot.command(name='score')
async def score(ctx):
    res = sorted(players, key=lambda x: players[x].kills, reverse=True)
    first_place = IMG_LEADER
    score = ''
    for player in res:
        score = score + f"{first_place} @{player}: {players[player].kills} bans"
        first_place = ' |'
    await ctx.send(score)

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
    hp = players[target].life()
    if hp == 0:
        await ctx.send(f"@{target} is banned {IMG_RIP}")
    else:
        weakness = check_weakness(target)
        await ctx.send(f"@{target} has {hp} {IMG_HEALTH} left, weakness is {weakness}")

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
        players[target].reset()
        if player == target:
            await ctx.send(f"@{target} self-heals back to {MAX_HP} {IMG_HEALTH}")
        else:
            await ctx.send(f"@{target} has been fully healed to {MAX_HP} {IMG_HEALTH}")
        return

    if players[target].life():
        await ctx.send(f"@{player} tried to cast healing from the realm of the banned {IMG_RIP}")
        return

    await ctx.send(f"@{player} spectacularly fails at casting an ancient healing spell that they haven't practiced enough {IMG_FAIL}")
    players[player].damage(1)
    if players[player].life() == 0:
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
    if players[player].life() == 0:
        await ctx.send(f"@{player} shakes his fist from the realm of the banned {IMG_RIP}")
        return
    # Check if target is dead
    if players[target].life() == 0:
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
    check_weakness(player, do_ban=True)

    dmg_back = 2**players[player].weakness + randint(0, 4)
    players[player].damage(dmg_back)
    await ctx.send(f"@{player} uses {dmg_back} life to cast the ban spell {IMG_SPELL}")
    player_hp = players[player].life()
    if player_hp == 0:
        await ctx.send(f"@{player} died casting ban on @{target} {IMG_RIP}")
        return
    players[player].last_ban_ts = time()

    # Apply damage to target
    if damage > 0:
        players[target].damage(damage)
        await ctx.send(f"@{player} deals {damage} BAN damage to @{target} {IMG_HIT}")
        target_hp = players[target].life()
        if target_hp == 0:
            if player != target:
                players[player].kills += 1
            await ctx.send(f"@{target} has been banned by @{player} {IMG_RIP}")
        else:
            await ctx.send(f"@{player} {player_hp} / @{target} {target_hp} {IMG_HEALTH}")
    else:
        await ctx.send(f"@{player} raises his hands to cast ban on @{target}. Everyone is holding their breath to see how this battle turns out... but @{target} ducks just in time for the spell to miss them {IMG_MISS}")

if __name__ == "__main__":
    bot.run()
