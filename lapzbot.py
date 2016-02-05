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


from __future__ import unicode_literals
import discord
import osu
import guessgame
import triviagame
import chatemotes
import eightball
import musicplayer
import asyncio


class Bot(discord.Client):
    """
    This is the main lapzbot class. Its of type discord.Bot(). It has got 3 options which can be passed on to it
    before running the bot. These are prefix(command prefix), key(osu api key) and hchid(help channel id).
    """
    prefix = ''
    key = ''
    hchid = ''

    def __init__(self):
        super().__init__()
        self.starter = None
        self.current = None
        self.player = None

    @asyncio.coroutine
    def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.prefix + 'help'):
            help_channel = self.hchid
            # NOTE:- If help channel id is wrong then discord will display it as #deleted-channel
            yield from self.send_message(message.channel,
                                         'Hello {}'.format(
                                             message.author.mention) + ', please visit <#' + help_channel +
                                         '> for a complete list of commands')

        yield from chatemotes.main(self, message, self.prefix)

        # MUSIC PLAYER---------------

        if message.content.startswith(self.prefix + 'load'):
            yield from musicplayer.load(self, message)

        if message.content.startswith(self.prefix + 'play '):
            yield from musicplayer.play(self, message)

        if message.content.startswith(self.prefix + 'pause'):
            yield from musicplayer.pause(self, message)

        if message.content.startswith(self.prefix + 'resume'):
            yield from musicplayer.resume(self, message)

        if message.content.startswith(self.prefix + 'stop'):
            yield from musicplayer.stop(self, message)

        if message.content.startswith(self.prefix + 'playlist'):
            yield from musicplayer.playlist(self, message)

        # Music player ends here-----------

        if message.content.startswith(self.prefix + 'guess'):
            now_playing = discord.Game(name='Guessing Game')
            yield from self.change_status(game=now_playing, idle=False)
            yield from guessgame.guess(self, message)
            now_playing = discord.Game(name='')
            yield from self.change_status(game=now_playing, idle=False)

        if message.content.startswith(self.prefix + 'quiz'):
            now_playing = discord.Game(name='Trivia Quiz')
            yield from self.change_status(game=now_playing, idle=False)
            yield from triviagame.quiz(self, message)
            now_playing = discord.Game(name='')
            yield from self.change_status(game=now_playing, idle=False)

        if message.content.startswith(self.prefix + 'stats'):
            my_string = message.content
            yield from self.send_message(message.channel, osu.stats(my_string, self.key))

        if message.content.startswith(self.prefix + 'top'):
            my_string = message.content
            yield from self.send_message(message.channel,
                                         'Fetching the requested data. Please wait...\n\n')
            yield from self.send_message(message.channel, osu.top(my_string, self.key))

        if message.content.startswith(self.prefix + '8ball'):
            yield from eightball.main(self, message)

    @asyncio.coroutine
    def on_ready(self):
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
        yield from self.change_status(game=now_playing, idle=False)
