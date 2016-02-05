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
import requests
import time
import bs4
import asyncio


def stats(instring, keystring):
    """
    This function uses the OSU API to return user statistics.

    :param instring: The message object while this function was called.
    :param keystring: OSU API Key

    :type instring: discord.Message()
    :type keystring: str

    :return: User stats
    :rtype: str
    """
    # extracting username from the string
    splitted = instring.split()
    uname = splitted[1]
    # key loaded from config.yaml
    key = keystring
    r = requests.get('https://osu.ppy.sh/api/get_user?k=' + key + '&u=' + uname)
    data = r.json()
    try:
        for player in data:
            op = str('https://a.ppy.sh/' + player['user_id'] + '\nUsername : ' + player['username']
                     + '\nPerformance Points : ' + "{0:.2f}".format(float(player['pp_raw'])) + '\nAccuracy : '
                     + "{0:.2f}".format(float(player['accuracy'])) + '\nPlaycount : ' + player['playcount']
                     + '\nProfile Link : `osu.ppy.sh/u/' + player['user_id'] + '`')
            result = op
        try:
            return result
        except UnboundLocalError:
            return str('```Username doesnt exist. Try again.```')
        # NOTE:- if the result is 'string indices must be integers' that means the API key is wrong
    except Exception as e:
        return str(e)


def top(instring, keystring):
    """
    This function uses the OSU API to return user top 5 plays.

    :param instring: The message object while this function was called.
    :param keystring: OSU API Key

    :type instring: discord.Message()
    :type keystring: str

    :return: User top plays
    :rtype: str
    """
    # extracting username from the string
    splitted = instring.split()
    uname = splitted[1]
    start_time = time.time()
    # key loaded from config.yaml
    key = keystring
    r = requests.get('https://osu.ppy.sh/api/get_user_best?k=' + key + '&u=' + uname + '&limit=5')
    data = r.json()
    msg = ''
    try:
        for player in data:
            thr = int(player['count300'])
            hun = int(player['count100'])
            fif = int(player['count50'])
            miss = int(player['countmiss'])
            tph = int(300 * thr + 100 * hun + 50 * fif)
            tnh = int(thr + hun + fif + miss)
            acc = float(tph / (tnh * 3))
            # TODO work on parsing with LXML
            bitits = requests.get('https://osu.ppy.sh/b/' + player['beatmap_id'])
            html = bs4.BeautifulSoup(bitits.text, 'html.parser')
            tits = html.title.text
            msg += str(
                    'Beatmap : ' + tits + ' `osu.ppy.sh/b/' + player['beatmap_id']
                    + '`' + '\n Acc : ' + "{0:.2f}".format(float(acc)) + ' | ' + 'Rank : '
                    + player['rank'] + ' | ' + 'PP : ' + player['pp'] + '\n')

        result = str(msg + '\nThis request took `' + "{0:.2f}".format((time.time() - start_time))
                      + ' seconds` to process.')

        try:
            return result
        except UnboundLocalError:
            return str('```Username doesnt exist. Try again.```')
        # NOTE:- if the result is 'string indices must be integers' that means the API key is wrong
    except Exception as e:
        return str(e)
