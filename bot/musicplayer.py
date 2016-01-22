from __future__ import unicode_literals
import json
import glob
import yaml
import subprocess as sp
import discord
import youtube_dl
import os

# For Youtube downloader only--------------------------------------
save_dir = 'audio_dl_caches'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


def make_save_path(title, savedir=save_dir):
    return os.path.join(savedir, '%s.mp3' % title)

# Ends here-----------------------------------------------------

async def load(self, message):
    await self.send_message(message.channel, 'Hooked to the voice channel. Please wait while'
                                             ' I populate the list of songs.')

    global s_playlist
    global voice_stream
    # global queue
    # queue = []

    if self.is_voice_connected():
        await self.send_message(message.channel,
                                '```Discord API doesnt let me join multiple servers at the moment.```')

    else:
        voice_stream = await self.join_voice_channel(message.author.voice_channel)

    # TODO get a better way to store local playlist
    try:
        global ids  # The sole purpose for this is to be used with !playlist
        ids = 0
        global s_dict
        global s_list
        s_list = []
        s_playlist = []
        a = glob.glob('../audio_library/*.mp3')
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

                    await self.send_message(message.channel,
                                            title + ' - ' + artist + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(title + ' - ' + artist)
                except LookupError:
                    head, tail = os.path.split(a)
                    filename = os.path.splitext(tail)[0]
                    await self.send_message(message.channel,
                                            filename + ' (code: **' + str(ids) + '**)')
                    s_playlist.append(ids)
                    s_playlist.append(filename)

            except Exception as e:
                print(str(e))
    except FileExistsError as e:
        await self.send_message(message.channel,
                                '``' + str(e) + '```')

    s_playlist_dict = dict(s_playlist[i:i + 2] for i in range(0, len(s_playlist), 2))
    with open('../configuration/playListInfo.yaml', 'w') as f2:
        yaml.dump(s_playlist_dict, f2, default_flow_style=False)

    del s_playlist  # Deleting this variable cause already the data is dumped to playListInfo.yaml

    s_dict = dict(s_list[i:i + 2] for i in range(0, len(s_list), 2))


async def play(self, message):
    try:
        if self.player is not None and self.player.is_playing():
            await self.send_message(message.channel, '```Already playing a song.' +
                                    ' Wait till the song is over or use stop.```')
            # queue.append(message)
            # print(queue)
            return
        else:
            # queue.append(message)
            # my_string = queue[0].content
            # print(queue)
            my_string = message.content
            splitted = my_string.split()
            second = splitted[1]

            # checks if its a digit or a url. If its a digit, then we play it normally--------------------------------
            if second.isdigit():
                second_int = int(second)
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
                    await self.send_message(message.channel, 'Currently playing **' + title + ' - ' + artist +
                                            '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')
                    # Game Status updating
                    now_playing = discord.Game(name=title)
                    await self.change_status(game=now_playing, idle=False)
                except LookupError:
                    file_name = str(s_dict[second_int])
                    head, tail = os.path.split(file_name)
                    filename = os.path.splitext(tail)[0]
                    leng = op_json['format']['duration']
                    seconds = float(leng)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    await self.send_message(message.channel, 'Currently playing **' + filename +
                                            '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')
                    # Game Status updating
                    now_playing = discord.Game(name=filename)
                    await self.change_status(game=now_playing, idle=False)

                self.player.start()

            # if play parameter is not a digit then we will treat it as a url
            else:

                url = second
                ytdl_format_options = {'format': 'worst',
                                       'extractaudio': True,
                                       'audioformat': "mp3",
                                       'outtmpl': '%(id)s',
                                       'noplaylist': True,
                                       'nocheckcertificate': True,
                                       'ignoreerrors': False,
                                       'quiet': False,
                                       'no_warnings': False}
                ydl = youtube_dl.YoutubeDL(ytdl_format_options)

                await self.send_message(message.channel, '```Downloading the requested song...```')

                with ydl:
                    try:
                        result = ydl.extract_info(url, download=True)
                        print('Extracting info')

                        savepath = make_save_path(result['title'])

                        if os.path.isfile(savepath):
                            os.unlink(savepath)

                        os.rename(result['id'], savepath)
                        await self.send_message(message.channel, '``` Song download and conversion successful.' +
                                                '```')

                    except Exception as e:
                        await self.send_message(message.channel, '```' + str(e) + '```')

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
                    await self.send_message(message.channel, 'Currently playing **' + filename +
                                            '**. Song duration is **%d:%02d:%02d' % (h, m, s) + '**.')

                    print(filename)
                    # Game Status updating
                    now_playing = discord.Game(name=filename)
                    await self.change_status(game=now_playing, idle=False)

                    self.player.start()
                except Exception as e:
                    await self.send_message(message.channel, '```' + str(e) + '```')

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def pause(self, message):
    try:
        if not self.is_voice_connected():
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        if self.player.is_playing() == True and self.player.is_done() == False:
            await self.send_message(message.channel, 'Paused')

            self.player.pause()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def resume(self, message):
    try:
        if not self.is_voice_connected():
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == False and self.player.is_done() == False:
            await self.send_message(message.channel, 'Resumed')

            self.player.resume()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def stop(self, message):
    try:
        if not self.is_voice_connected():
            await self.send_message(message.channel, '```Please connect to voice channel first```')

        elif self.player.is_playing() == True and self.player.is_done() == False:
            await self.send_message(message.channel, 'stopped')

            now_playing = discord.Game(name='')
            await self.change_status(game=now_playing, idle=False)

            self.player.stop()

    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')


async def playlist(self, message):
    try:
        # Loading configurations from config.yaml
        with open('../configuration/playListInfo.yaml', 'r') as f3:
            plist = yaml.load(f3)
        idq = 1
        plistfinal = ''
        while idq <= ids:
            song = plist[idq]
            plistfinal += str(song + ' (code: **' + str(idq) + '**)\n')
            idq += 1

        await self.send_message(message.channel, plistfinal)
    except Exception as e:
        await self.send_message(message.channel,
                                '```' + str(e) + '```')
