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


import random

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
