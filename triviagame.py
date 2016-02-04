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

import requests
import re

removebadtags = re.compile(r'<[^>]+>')
removebadarticles = re.compile('\\b(the)\\W', re.I)

async def quiz(self, message):
    """
    Trivia quiz game.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.

    :type self: discord.Client()
    :type message: discord.Message()

    :return: This function returns nothing.
    """
    r = requests.get('http://jservice.io/api/random?')
    data = r.json()

    for player in data:
        await self.send_message(message.channel, player['question'])

        guess = await self.wait_for_message(timeout=15.0, author=message.author)
        guess_l = removebadarticles.sub('', removebadtags.sub('', str(guess.content).strip().casefold()))
        answer = removebadarticles.sub('', removebadtags.sub('', str(player['answer']).strip().casefold()))

        set1 = set(guess_l.split(' '))
        set2 = set(answer.split(' '))

        if guess_l is None:
            fmt = 'Sorry, you took too long. It was {}.'
            await self.send_message(message.channel, fmt.format(answer))
            return
        elif set1 == set2:
            fmt = 'You are right! {} is the correct answer!'
            await self.send_message(message.channel, fmt.format(player['answer'].capitalize()))
