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
import asyncio


@asyncio.coroutine
def main(self, message, prefix):
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
        yield from self.send_message(message.channel, 'http://i.imgur.com/N5RzfBB.png')

    if message.content.startswith(prefix+'feelsbadman'):
        yield from self.send_message(message.channel, 'http://i.imgur.com/DfURIfh.png')

    if message.content.startswith(prefix+'feelsgoodman'):
        yield from self.send_message(message.channel, 'http://i.imgur.com/9Ggf2vs.png')

    if message.content.startswith(prefix+'lapz'):
        yield from self.send_message(message.channel, 'http://i.imgur.com/I0Lqf3w.png')
