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
import json
import glob
import yaml
import subprocess as sp
import discord
import youtube_dl
import os
import asyncio

save_dir = 'audio_dl_caches'


def make_save_path(title, savedir=save_dir):
    """
    This function creates the save paths for the downloaded songs.

    :param savedir: The downloaded songs will be saved in this relative directory.
    :param title: The filename with which the song will be saved.

    :type savedir: str
    :type title: str
    """
    return os.path.join(savedir, '%s.mp3' % title)


@asyncio.coroutine
def load(self, message):
    """
    This function is called when the user uses `load` command.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    yield from self.send_message(message.channel, 'Hooked to the voice channel. Please wait while'
                                                  ' I populate the list of songs.')

    global s_playlist
    global voice_stream

    if self.is_voice_connected():
        yield from self.send_message(message.channel,
                                     '```Discord API doesnt let me join multiple servers at the moment.```')

    else:
        voice_stream = yield from self.join_voice_channel(message.author.voice_channel)

    # TODO get a better way to store local playlist
    try:
        global ids  # The sole purpose for this is to be used with !playlist
        ids = 0
        global s_dict
        global s_list
        s_list = []
        s_playlist = []
        a = glob.glob('./audio_library/*.mp3')
        for a in a:
            try:
                b = a.replace('\\', '/')
                ids += 1
                s_list.append(ids)
                s_list.append(b)
                print(b)
                p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                              b], stdout=sp.PIPE, stderr=sp.PIPE)
                op = p.communicate()
                op_json = json.loads(op[0].decode('utf-8'))

                try:
                    title = op_json['format']['tags']['title']
                    artist = op_json['format']['tags']['artist']

                    yield from self.send_message(message.channel,
                                                 title + ' - ' + artist + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(title + ' - ' + artist)
                except LookupError:
                    head, tail = os.path.split(a)
                    filename = os.path.splitext(tail)[0]
                    yield from self.send_message(message.channel,
                                                 filename + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(filename)

            except Exception as e:
                print(str(e))
    except FileExistsError as e:
        yield from self.send_message(message.channel,
                                     '``' + str(e) + '```')

    s_playlist_dict = dict(s_playlist[i:i + 2] for i in range(0, len(s_playlist), 2))
    with open('playListInfo.yaml', 'w') as f2:
        yaml.dump(s_playlist_dict, f2, default_flow_style=False)

    del s_playlist  # Deleting this variable cause already the data is dumped to playListInfo.yaml

    s_dict = dict(s_list[i:i + 2] for i in range(0, len(s_list), 2))


@asyncio.coroutine
def play(self, message):
    """
    This function is called when the player uses `play` command

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    try:
        if self.player is not None and self.player.is_playing():
            yield from self.send_message(message.channel, '```Already playing a song.' +
                                         ' Your current request is queued.```')
            return
        else:
            my_string = message.content
            splitted = my_string.split()
            second = splitted[1]

            # checks if its a digit or a url. If its a digit, then we play it normally--------------------------------
            if second.isdigit():
                second_int = int(second)
                # self.play_next_song.clear()
                # self.current = yield from self.songs.get()
                self.player = self.voice.create_ffmpeg_player(str(s_dict[second_int]))

                # FFProbing for info
                p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                              str(s_dict[second_int])], stdout=sp.PIPE, stderr=sp.PIPE)
                op = p.communicate()
                op_json = json.loads(op[0].decode('utf-8'))

                try:
                    title = op_json['format']['tags']['title']
                    artist = op_json['format']['tags']['artist']
                    leng = op_json['format']['duration']
                    seconds = float(leng)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    print('title:', title)
                    print('artist:', artist)
                    yield from self.send_message(message.channel, 'Currently playing **' + title + ' - ' + artist +
                                                 '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')
                    # Game Status updating
                    now_playing = discord.Game(name=title)
                    yield from self.change_status(game=now_playing, idle=False)
                except LookupError:
                    file_name = str(s_dict[second_int])
                    head, tail = os.path.split(file_name)
                    filename = os.path.splitext(tail)[0]
                    leng = op_json['format']['duration']
                    seconds = float(leng)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    yield from self.send_message(message.channel, 'Currently playing **' + filename +
                                                 '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')
                    # Game Status updating
                    now_playing = discord.Game(name=filename)
                    yield from self.change_status(game=now_playing, idle=False)

                self.player.start()
                # yield from self.play_next_song.wait()

            # if play parameter is not a digit then we will treat it as a url
            else:

                url = second
                ytdl_format_options = {'format': 'worst',
                                       'extractaudio': True,
                                       'audioformat': "mp3",
                                       'outtmpl': '%(id)s',
                                       'noplaylist': True,
                                       'nocheckcertificate': True,
                                       'ignoreerrors': True,
                                       'quiet': False,
                                       'no_warnings': False}
                ydl = youtube_dl.YoutubeDL(ytdl_format_options)

                yield from self.send_message(message.channel, '```Downloading the requested song...```')

                with ydl:
                    try:
                        result = ydl.extract_info(url, download=True)
                        print('Extracting info')
                        if not os.path.exists(save_dir):
                            os.makedirs(save_dir)

                        savepath = make_save_path(result['title'])

                        # If the file existed, we're going to remove it to overwrite.
                        if os.path.isfile(savepath):
                            print('This file exists. Deleting it for overwrite.')
                            os.unlink(savepath)

                        # Move the temporary file to it's final location.
                        os.rename(result['id'], savepath)
                        yield from self.send_message(message.channel, '``` Song download and conversion successful.' +
                                                     '```')

                    except Exception as e:
                        yield from self.send_message(message.channel, '```' + str(e) + '```')

                try:
                    self.player = self.voice.create_ffmpeg_player(savepath)

                    p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                                  savepath], stdout=sp.PIPE, stderr=sp.PIPE)
                    op = p.communicate()
                    op_json = json.loads(op[0].decode('utf-8'))

                    head, tail = os.path.split(savepath)
                    filename = os.path.splitext(tail)[0]
                    leng = op_json['format']['duration']
                    seconds = float(leng)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    yield from self.send_message(message.channel, 'Currently playing **' + filename +
                                                 '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')

                    print(filename)
                    # Game Status updating
                    now_playing = discord.Game(name=filename)
                    yield from self.change_status(game=now_playing, idle=False)

                    self.player.start()
                except Exception as e:
                    yield from self.send_message(message.channel, '```' + str(e) + '```')

    except Exception as e:
        yield from self.send_message(message.channel,
                                     '```' + str(e) + '```')


@asyncio.coroutine
def pause(self, message):
    """
    This function is called when the player uses `pause` command.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    try:
        if not self.is_voice_connected():
            yield from self.send_message(message.channel, '```Please connect to voice channel first```')

        if self.player.is_playing() == True and self.player.is_done() == False:
            yield from self.send_message(message.channel, 'Paused')

            self.player.pause()

    except Exception as e:
        yield from self.send_message(message.channel,
                                     '```' + str(e) + '```')


@asyncio.coroutine
def resume(self, message):
    """
    This function is called when the player uses `resume` command.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    try:
        if not self.is_voice_connected():
            yield from self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == False and self.player.is_done() == False:
            yield from self.send_message(message.channel, 'Resumed')

            self.player.resume()

    except Exception as e:
        yield from self.send_message(message.channel,
                                     '```' + str(e) + '```')


@asyncio.coroutine
def stop(self, message):
    """
    This function is called when the player uses `stop` command.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    try:
        if not self.is_voice_connected():
            yield from self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == True and self.player.is_done() == False:
            yield from self.send_message(message.channel, 'stopped')

            now_playing = discord.Game(name='')
            yield from self.change_status(game=now_playing, idle=False)

            self.player.stop()

    except Exception as e:
        yield from self.send_message(message.channel,
                                     '```' + str(e) + '```')


@asyncio.coroutine
def playlist(self, message):
    """
    This function is called when the player uses `playlist` command. The `playlist` command
    currently displays the list of songs inside the `audio_library` folder.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing

    :type self: discord.Client()
    :type message: discord.Message()
    """
    try:
        # Loading configurations from config.yaml
        with open('playListInfo.yaml', 'r') as f3:
            plist = yaml.load(f3)
        idq = 1
        plistfinal = ''
        while idq <= ids:
            song = plist[idq]
            plistfinal += str(song + ' (code: **' + str(idq) + '**)\n')
            idq += 1

        yield from self.send_message(message.channel, plistfinal)
    except Exception as e:
        yield from self.send_message(message.channel,
                                     '```' + str(e) + '```')
