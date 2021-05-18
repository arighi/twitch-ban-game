# TWITCH BAN GAME

Twitch Ban Game is a text-based game that can be played in the Twitch chat.

Users in chat can compete each other casting the spell "BAN" to ban other
players from the game and dominate the chat!

## Requirements

This program requires:
 - python3
 - pipenv

And the following python modules:
 - requests
 - twitchio

Example (tested on Ubuntu 21.04):

  $ sudo apt install python3 pipenv
  $ pipenv run pip3 install twitchio
  $ pipenv run pip3 install requests

## Running the game

The game engine is implemented by a bot that joins your Twitch chat. Before
starting the game you need to configure the credentials to allow the bot to log
into your chat. To do so create a file .env in this directory, the file should
look like this:

```
 TMI_TOKEN=oauth:<YOUR_OAUTH_TOKEN>
 CLIENT_ID=arighibot
 BOT_NICK=arighi_violin
 BOT_PREFIX=!
 CHANNEL=#arighi_violin
```

Where `<YOUR_OAUTH_TOKEN>` is a Twitch authentication token, see
https://dev.twitch.tv/docs/authentication for more information on how to get
one.

Also make sure to replace all variables with your Twitch username and rename
the bot `CLIENT_ID` as you prefer.

After the .env is created you can start the game using the run.sh script (in
Linux - there should be an equivalent way to start the game from Windows / Mac
as well):

```
  $ ./run.sh
  Loading .env environment variables…
  arighi_violin is online!
```

Once the game is started users in chat can start to play (see the Rules below).

## Rules

```
 - any <PLAYER> in chat can run:

   !ban <TARGET_PLAYER>

   <PLAYER> deals <N> "ban" damage to <TARGET_PLAYER>, where <N> is randomly
   modeled as a D20 roll:

   - a roll of 1 is always a MISS

   - a roll of 20 is a critical hit and it does x2 damage (=40 damage)

   - <PLAYER> gets (1 + 10-25%) of the damage back (to prevent spamming !ban)

 - each <PLAYER> starts with an initial health pool of 50 HP

   - when <PLAYER> runs the !ban command we initialize the health pool for
     <PLAYER> and <TARGET_PLAYER>

 - <PLAYER> can run a command !life to show in chat the amount of HP left !life
   <TARGET_PLAYER> can be used to show the amount of HP left of <TARGET_PLAYER>

 - when <PLAYER> reaches 0 HP, <PLAYER> is banned and cannot run the !ban
   command until <PLAYER> is resurrected (see !unban)

 - !unban <TARGET_PLAYER> heals <TARGET_PLAYER> to full health
   (this command can be executed only by broadcaster or mods)

 - <PLAYER> can get health back using <IMG_REVIVE> emotes in the chat (max +1
   HP for each message that contains the <IMG_REVIVE> emote)
```

## TODO

```
 - GFPSolutions: if you spam too many !ban => you enter in a vulnerable state
   and you can get a critical hit with a roll of 10+

 - Ysgramor3:
     Every time a user casts !ban, they take 2^n + random(0,4) damage.
     n is the current count of bans the user executed.
     n is initialized to 0
     n is incremented every time a user types !ban (unless he is "banned")
     n is decremented by one every 15 minutes.

 - implement an additional cooldown for the !ban command in addition to the
   damage backfire to prevent spamming ban even more

 - higher health pool for privileged users (mods, VIPs, etc.)
```

## CREDITS

Thanks to Ysgramor3 (https://www.twitch.tv/Ysgramor3) for the cool text lines
and the awesome suggestions!

Thanks to GFPSolutions (https://www.twitch.tv/GFPSolutions) for the game
mechanics/code suggestions!

Thanks to my Twitch friends for joining my streams and helping me to test the
game (https://www.twitch.tv/arighi_violin)! :)
