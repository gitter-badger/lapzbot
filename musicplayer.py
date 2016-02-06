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
import validators
import info_extractor

save_dir = 'audio_dl_caches'
qu = []
lapz_instance = None  # <---------This is the main instance of Lapzbot passed from run_lapzbot.py
scanned = False
ytdl_format_options = {'format': 'worst',
                       'extractaudio': True,
                       'audioformat': "mp3",
                       'outtmpl': '%(id)s',
                       'noplaylist': True,
                       'nocheckcertificate': True,
                       'ignoreerrors': True,
                       'quiet': False,
                       'no_warnings': False}


def make_save_path(title, savedir=save_dir):
    """
    This function creates the save paths for the downloaded songs.

    :param savedir: The downloaded songs will be saved in this relative directory.
    :param title: The filename with which the song will be saved.

    :type savedir: str
    :type title: str
    """
    return os.path.join(savedir, '%s.mp3' % title)


async def next_song(self, message):
    if qu:
        await stop(self, message)
        await play(self, qu[0])
        qu.remove(qu[0])

    elif not qu:
        await self.send_message(message.channel, '``` The queue is empty. Queue a song first.```')

async def load(self, message):
    """
    This function is called when the user uses `load` command.

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    await lapz_instance.send_message(message.channel, 'LOADED!!!')

    global voice_stream
    if self.is_voice_connected():
        await self.send_message(message.channel,
                                '```Discord API doesnt let me join multiple servers at the moment.```')

    else:
        await self.send_message(message.channel, '```Joined voice channel. To scan your local songs, use'
                                                 '{command_prefix}scan .```')
        voice_stream = await self.join_voice_channel(message.author.voice_channel)


async def play(self, message):
    """
    This function is called when the player uses `play` command

    :param self: An instance of lapzbot is passed onto this function.
    :param message: The message object while this function was called.
    :return: This function returns nothing.

    :type self: discord.Client()
    :type message: discord.Message()
    """
    if not scanned:
        await self.send_message(message.channel, '```Local songs are not yet scanned. '
                                                 'Ping the admin to scan them first.```')
        return

    elif not self.is_voice_connected():
        await self.send_message(message.channel, '```Please connect to voice channel first```')
        return

    if self.player is not None and self.player.is_playing():
        qu.append(message)
        print(qu)
        await self.send_message(message.channel, '```Already playing a song.' +
                                ' Your current request is queued. There are ' + str(len(qu)) + ' songs queued.```')
        return
    else:
        my_string = message.content
        splitted = my_string.split()
        second = splitted[1]

        # checks if its a digit or a url. If its a digit, then we play it normally.
        if second.isdigit():
            second_int = int(second)
            self.player = self.voice.create_ffmpeg_player(str(s_dict[second_int]))

            filename, duration = info_extractor.info_extract((s_dict[second_int]))

            await self.send_message(message.channel, '{0} playing your requested song: **'.format(message.author.mention) +
                                    filename + '**. Song duration is: **' + duration + '**.')
            # Game Status updating
            now_playing = discord.Game(name=filename)
            await self.change_status(game=now_playing, idle=False)

            self.player.start()

        # if play parameter is not a digit then we will treat it as a url
        elif validators.url(second):
            url = second
            ydl = youtube_dl.YoutubeDL(ytdl_format_options)

            await self.send_message(message.channel, '```Downloading the requested song...```')

            with ydl:
                try:
                    global result
                    result = ydl.extract_info(url, download=True)
                except Exception as e:
                    await self.send_message(message.channel, '```' + str(e) + '```')

            try:
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                if result is None:
                    print('Error')
                    return

                savepath = make_save_path(result['title'])

                # If the file existed, we're going to remove it to overwrite.
                if os.path.isfile(savepath):
                    print('This file exists. Deleting it for overwrite.')
                    os.unlink(savepath)

                # Move the temporary file to it's final location.
                os.rename(result['id'], savepath)
                await self.send_message(message.channel, '``` Song download and conversion successful.' +
                                        '```')

                self.player = self.voice.create_ffmpeg_player(savepath)
                filename, duration = info_extractor.ytinfo_extractor(savepath)

                await self.send_message(message.channel, '{0} playing your requested song: **'
                                        .format(message.author.mention) + filename +
                                        '**. Song duration is: **' + duration + '**.')
                # Game Status updating
                now_playing = discord.Game(name=filename)
                await self.change_status(game=now_playing, idle=False)

                self.player.start()
            except Exception:
                await self.send_message(message.channel, '```Oops! info extraction failed. Try another song.```')


async def pause(self, message):
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
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        if self.player.is_playing() == True and self.player.is_done() == False:
            self.player.pause()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def resume(self, message):
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
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == False and self.player.is_done() == False:
            self.player.resume()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def stop(self, message):
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
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == True and self.player.is_done() == False:
            now_playing = discord.Game(name='')
            await self.change_status(game=now_playing, idle=False)

            self.player.stop()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def playlist(self, message):
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
            plistfinal += str(song + ' (code: ' + str(idq) + ')\n')
            idq += 1

        await self.send_message(message.channel, '```Local Playlist:\n' + plistfinal + '```')
    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


def scan_local_songs():
    print('Scanning all local songs.')
    try:
        global scanned
        global s_playlist
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

                    # await self.send_message(message.channel,
                    #                         title + ' - ' + artist + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(title + ' - ' + artist)
                except LookupError:
                    head, tail = os.path.split(a)
                    filename = os.path.splitext(tail)[0]
                    # await self.send_message(message.channel,
                    #                         filename + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(filename)

            except Exception as e:
                print(str(e))
    except FileExistsError as e:
        print(str(e))

    s_playlist_dict = dict(s_playlist[i:i + 2] for i in range(0, len(s_playlist), 2))
    with open('playListInfo.yaml', 'w') as f2:
        yaml.dump(s_playlist_dict, f2, default_flow_style=False)

    del s_playlist  # Deleting this variable cause already the data is dumped to playListInfo.yaml

    s_dict = dict(s_list[i:i + 2] for i in range(0, len(s_list), 2))

    print('\nScanning completed.')
    scanned = True
