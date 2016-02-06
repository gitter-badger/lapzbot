#
# The MIT License (MIT)
#
# Copyright (c) 2016 lapoozza
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import discord
import osu
import triviagame
import musicplayer
import threading
import asyncio
import re
import requests
import random


class Bot(discord.Client):
    """
    This is the main lapzbot class. Its of type discord.Bot(). It has got 3 options which can be passed on to it
    before running the bot. These are prefix(command prefix), key(osu api key) and hchid(help channel id).
    """
    prefix = ''
    key = ''
    hchid = ''
    admin_ids = ['142517808570433536']

    def __init__(self):
        super().__init__()
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.starter = None
        self.player = None
        self.current = None

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.prefix + 'help'):
            help_channel = self.hchid
            # NOTE:- If help channel id is wrong then discord will display it as #deleted-channel
            await self.send_message(message.channel,
                                    'Hello {}'.format(message.author.mention) + ', please visit <#' + help_channel +
                                    '> for a complete list of commands')

        await chat_emotes(self, message, self.prefix)

        # MUSIC PLAYER---------------
        if message.content.startswith(self.prefix + 'load'):
            await musicplayer.load(self, message)

        if message.content.startswith(self.prefix + 'play '):
            await musicplayer.play(self, message)

        if message.content.startswith(self.prefix + 'pause'):
            await musicplayer.pause(self, message)

        if message.content.startswith(self.prefix + 'resume'):
            await musicplayer.resume(self, message)

        if message.content.startswith(self.prefix + 'stop'):
            await musicplayer.stop(self, message)

        if message.content.startswith(self.prefix + 'playlist'):
            await musicplayer.playlist(self, message)

        if message.content.startswith(self.prefix + 'next'):
            await musicplayer.next_song(self, message)

        if message.content.startswith(self.prefix + 'scan'):
            # TODO remove message line later
            for ids in self.admin_ids:
                if ids == message.author.id:
                    await self.send_message(message.channel, '```Scanning all local songs. '
                                                             'This might take some time.```')
                    t1 = threading.Thread(target=musicplayer.scan_local_songs())
                    t1.start()
                else:
                    await self.send_message(message.channel, '```This is an admin only command.```')

        # UTILITY FUNCTIONS------------------------------------
        # Number Guessing Game -->
        if message.content.startswith(self.prefix + 'guess'):
            now_playing = discord.Game(name='Guessing Game')
            await self.change_status(game=now_playing, idle=False)
            await guess(self, message)
            now_playing = discord.Game(name='')
            await self.change_status(game=now_playing, idle=False)

        # Trivia Quiz Game -->
        if message.content.startswith(self.prefix + 'quiz'):
            now_playing = discord.Game(name='Trivia Quiz')
            await self.change_status(game=now_playing, idle=False)
            await triviagame.quiz(self, message)
            now_playing = discord.Game(name='')
            await self.change_status(game=now_playing, idle=False)

        # OSU API FUNCTIONS -->
        if message.content.startswith(self.prefix + 'stats'):
            my_string = message.content
            await self.send_message(message.channel, osu.stats(my_string, self.key))

        if message.content.startswith(self.prefix + 'top'):
            my_string = message.content
            await self.send_message(message.channel,
                                    'Fetching the requested data. Please wait...\n\n')
            await self.send_message(message.channel, osu.top(my_string, self.key))

        # 8 Ball -->
        if message.content.startswith(self.prefix + '8ball'):
            await eightball(self, message)

        # Who am I? and Who Is? -->
        if message.content.startswith(self.prefix + 'whoami'):
            await whoami(self, message)

        if message.content.startswith(self.prefix + 'whois'):
            await whois(self, message)

        # Giphy GIF Search -->
        if message.content.startswith(self.prefix + 'giphy'):
            querry = str(message.content[7:])
            querry_format = querry.replace(' ', '+')
            print(querry)
            print(querry_format)
            await giphy(self, message, querry_format)

    async def on_ready(self):
        """
        This function is called once lapzbot logs in to discord and its Server list
        is populated.

        :return: This function returns a status message when it is ready.
        :rtype: discord.Client.change_status()
        """
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        # Game Status updating
        now_playing = discord.Game(name='type ' + self.prefix + 'help for help')
        await self.change_status(game=now_playing, idle=False)


# UTILITY FUNCTIONS----------------------------->
async def whoami(self, message):
    role = ''
    ids = message.author.id
    server = message.author.server
    joined = str(message.author.joined_at.year) + '-' + str(message.author.joined_at.month) \
             + '-' + str(message.author.joined_at.day)
    joined_time = str(message.author.joined_at.hour) + ':' + str(message.author.joined_at.minute)
    game = message.author.game
    for r in message.author.roles:
        r = str(r.name)
        role += r

    opstr = message.author.mention + '```ID: ' + str(ids) + '\nServer: ' + str(server) + '\nJoined on: ' + joined \
            + ' @ ' + joined_time + ' hrs ' + '\nGame: ' + str(game) + '\nRoles: ' + str(role) + '```'
    await self.send_message(message.channel, opstr)


async def whois(self, message):
    my_string = message.content
    splitted = my_string.split()
    user = str(splitted[1])
    idss = re.sub("[<@>]", '', user)

    membs = self.get_all_members()
    membslist = list(membs)

    for usr in membslist:
        usrid = usr.id
        print(usrid)
        if usrid == idss:
            role = ''
            ids = usr.id
            server = usr.server
            joined = str(usr.joined_at.year) + '-' + str(usr.joined_at.month) \
                     + '-' + str(usr.joined_at.day)
            joined_time = str(usr.joined_at.hour) + ':' + str(usr.joined_at.minute)
            game = usr.game
            for r in usr.roles:
                r = str(r.name) + ', '
                role += r

            opstr = message.author.mention + '```Whois' + '\nID: ' + str(ids) + '\nServer: ' + str(server) \
                    + '\nJoined on: ' + joined + ' @ ' + joined_time + ' hrs ' + '\nGame: ' + str(game) + '\nRoles: ' \
                    + str(role) + '```'
            await self.send_message(message.channel, opstr)
            return


async def giphy(self, message, querry):
    """
    GIPHY gif search

    :param self:
    :param message:
    :param querry: gif search querry (example: awesome+dogs+swag)
    :return: gif image matching search criteria
    """

    key = 'dc6zaTOxFJmzC'
    r = requests.get('http://api.giphy.com/v1/gifs/search?q=' + querry + '&api_key=' + key + '&limit=1&offset=0')
    payload = r.json()['data'][0]['images']
    image = payload['original']['url']
    await self.send_message(message.channel, str(image))
    # Use the line below for branding
    # await self.send_file(message.channel, './static/giphy_powered.png', 'giphy_powered.png')


async def chat_emotes(self, message, prefix):
    """
    Chat emoticons that are displayed inside lapzbot.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :param prefix: Command prefix

    :type self: discord.Client()
    :type message: discord.Message()
    :type prefix: str

    :return: Emoticon image
    :rtype: png
    """
    if message.content.startswith(prefix+'kappa'):
        await self.send_file(message.channel, './static/kappa.png', 'kappa.png')

    if message.content.startswith(prefix+'feelsbadman'):
        await self.send_file(message.channel, './static/feelsbadman.png', 'feelsbadman.png')

    if message.content.startswith(prefix+'feelsgoodman'):
        await self.send_file(message.channel, './static/feelsgoodman.png', 'feelsgoodman.png')

    if message.content.startswith(prefix+'lapz'):
        await self.send_file(message.channel, './static/lapz.png', 'lapz.png')


async def guess(self, message):
    """
    Number guessing game.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.

    :type self: discord.Client()
    :type message: discord.Message()

    :return: This function returns nothing.
    """
    await self.send_message(message.channel, 'Guess a number between 1 to 10')

    def guess_check(m1):
        return m1.content.isdigit()

    guesst = await self.wait_for_message(timeout=5.0, author=message.author, check=guess_check)
    answer = random.randint(1, 10)
    if guesst is None:
        fmt = 'Sorry, you took too long. It was {}.'
        await self.send_message(message.channel, fmt.format(answer))
        return
    if int(guesst.content) == answer:
        await self.send_message(message.channel, 'You are right!')
    else:
        await self.send_message(message.channel, 'Sorry. It is actually {}.'.format(answer))


responses = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes, definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you know",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful"
]

async def eightball(self, message):
    """
    8ball game. Ask any question to lapzbot and it gives a randomly selected answer is given.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.

    :type self: discord.Client()
    :type message: discord.Message()

    :return: Randomly generated answer
    :rtype: str
    """
    maxnum = len(responses) - 1
    rand = random.randint(0, maxnum)
    await self.send_message(message.channel, responses[rand])

