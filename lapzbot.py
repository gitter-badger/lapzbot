import discord
import json
import requests
import bs4
import time
from discord import opus
import subprocess as sp
import glob
import random


class Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.player = None

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('{} hello'.format(self.user.mention)):
            await self.send_message(message.channel,
                                    'Hello {} , how are you doing today?'.format(message.author.mention))

        if message.content.startswith('{} help'.format(self.user.mention)):
            await self.send_message(message.channel,
                                    'Hello {}, the following commands are available:- `@lapzbot hello`, `@lapzbot help`, `@lapzbot stats <username>`, `@lapzbot top <username>`, `wtf`'.format(
                                            message.author.mention) + '\n The following emoticons are supported :- `!kappa`,`!feelsbadman` ,`!feelsgoodman`, `!lapz`')

        if message.content.startswith('{} wtf'.format(self.user.mention)):
            await self.send_message(message.channel, 'WTF!!! {}'.format(message.author.mention))

        if message.content.startswith('{} who are you'.format(self.user.mention)):
            await self.send_message(message.channel,
                                    'Hello {}, I am utility bot created by Lapoozza. Feel free to talk to me in case you are bored. I can also perform a range of functions. Use`@lapzbot help` to access my comamnds list.'.format(
                                            message.author.mention))

        # Music Player codes------------------------------------------------------------------------------------
        if message.content.startswith('!load'.format(self.user.mention)):
            await self.send_message(message.channel, 'Hooked to the voice channel. Please wait while'
                                                     ' I populate the list of songs.')

            opus.load_opus('libopus-0.x86.dll')
            global player
            global voice_stream
            global file_name

            if self.is_voice_connected() == True:
                await self.send_message(message.channel,
                                        '```Discord API doesnt let me join multiple servers at the moment.```')

            else:
                voice_stream = await self.join_voice_channel(message.author.voice_channel)

            # TODO get a better way to store local playlist
            try:
                ids = 0
                global s_dict
                s_list = []
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
                        title = op_json['format']['tags']['title']
                        artist = op_json['format']['tags']['artist']
                        await self.send_message(message.channel,
                                                title + ' - ' + artist + ' (code: **' + str(ids) + '**)')

                    except Exception as e:
                        print(str(e))
            except:
                await self.send_message(message.channel,
                                        '```No songs in the directory lol.```')

            s_dict = dict(s_list[i:i + 2] for i in range(0, len(s_list), 2))
            print(s_dict[1])

        if message.content.startswith('!play '):

            try:
                if self.player is not None and self.player.is_playing():
                    await self.send_message(message.channel, 'Already playing a song')
                    return
                else:
                    my_string = message.content
                    splitted = my_string.split()
                    second = int(splitted[1])

                    self.player = self.voice.create_ffmpeg_player(str(s_dict[second]))

                    # FFProbing for info
                    p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                                  str(s_dict[second])], stdout=sp.PIPE, stderr=sp.PIPE)
                    op = p.communicate()
                    op_json = json.loads(op[0].decode('utf-8'))
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

                    self.player.start()

                # else:
                #     await self.send_message(message.channel, '```Please connect to voice channel first```')

            except Exception as e:
                await self.send_message(message.channel,
                                        '```' + str(e) + '```')

        if message.content.startswith('!pause'):

            try:
                if self.is_voice_connected() == False:
                    await self.send_message(message.channel, '```Please connect to voice channel first```')

                if player.is_playing() == True and player.is_done() == False:
                    await self.send_message(message.channel, 'Paused')

                    now_playing = discord.Game(name='Paused')
                    await self.change_status(game=now_playing, idle=False)

                    player.pause()

            except Exception as e:
                await self.send_message(message.channel,
                                        '```' + str(e) + '```')

        if message.content.startswith('!resume'):

            try:
                if self.is_voice_connected() == False:
                    await self.send_message(message.channel, '```Please connect to voice channel first```')

                elif player.is_playing() == True and player.is_done() == False:
                    await self.send_message(message.channel, 'Paused')

                    now_playing = discord.Game(name='Paused')
                    await self.change_status(game=now_playing, idle=False)

                    player.resume()

            except Exception as e:
                await self.send_message(message.channel,
                                        '```' + str(e) + '```')

        if message.content.startswith('!stop'):

            try:
                if self.is_voice_connected() == False:
                    await self.send_message(message.channel, '```Please connect to voice channel first```')

                elif self.player.is_playing() == True and self.player.is_done() == False:
                    await self.send_message(message.channel, 'Paused')

                    now_playing = discord.Game(name='')
                    await self.change_status(game=now_playing, idle=False)

                    player.stop()

            except Exception as e:
                await self.send_message(message.channel,
                                        '```' + str(e) + '```')

# Yes/No API Codes---------

        if message.content.startswith('{} '.format(self.user.mention)):
            x = message.content
            if x.startswith('<@134962024324136960> is') or x.startswith('<@134962024324136960> are') or x.startswith(
                    '<@134962024324136960> will') or x.startswith('<@134962024324136960> do') or x.startswith(
                    '<@134962024324136960> would'):
                print(x)
                r = requests.get('http://yesno.wtf/api')
                data = r.json()
                await self.send_message(message.channel, data['answer'] + '\n' + data['image'])
            if x.startswith('<@134962024324136960> what') or x.startswith('<@134962024324136960> why') or x.startswith(
                    '<@134962024324136960> when') or x.startswith('<@134962024324136960> how') or x.startswith(
                    '<@134962024324136960> where'):
                print(x)
                await self.send_message(message.channel,
                                        'Oww, my creator has instructed me not to answer that question. Next question please...')

        if message.content.startswith('!guess'):
            await self.send_message(message.channel, 'Guess a number between 1 to 10')

            def guess_check(m):
                return m.content.isdigit()

            guess = await self.wait_for_message(timeout=5.0, author=message.author, check=guess_check)
            answer = random.randint(1, 10)
            if guess is None:
                fmt = 'Sorry, you took too long. It was {}.'
                await self.send_message(message.channel, fmt.format(answer))
                return
            if int(guess.content) == answer:
                await self.send_message(message.channel, 'You are right!')
            else:
                await self.send_message(message.channel, 'Sorry. It is actually {}.'.format(answer))

        # TODO implement other osu!API Functions
        if message.content.startswith('{} stats'.format(self.user.mention)):
            my_string = message.content
            splitted = my_string.split()
            third = splitted[2]
            # first = splitted[0]
            # second = splitted[1]


            r = requests.get('https://osu.ppy.sh/api/get_user?k=API KEY&u=' + third)
            data = r.json()
            for player in data:
                await self.send_message(message.channel,
                                        'https://a.ppy.sh/' + player['user_id'] + '\nUsername : ' + player[
                                            'username'] + '\nPerformance Points : ' + "%.2f" % float(
                                                player['pp_raw']) + '\nAccuracy : ' + "%.2f" % float(
                                                player['accuracy']) + '\nPlaycount : ' + player[
                                            'playcount'] + '\nProfile Link : `osu.ppy.sh/u/' + player['user_id'] + '`')

        if message.content.startswith('{} top'.format(self.user.mention)):
            my_string = message.content
            splitted = my_string.split()
            # first = splitted[0]
            # second = splitted[1]
            third = splitted[2]

            await self.send_message(message.channel,
                                    'Parsing the requested data. I may take some time. Please be patient.\n*Dont send me any other request before current request is completed, coz I am gonna ignore it.*\n\n')
            start_time = time.time()
            r = requests.get(
                    'https://osu.ppy.sh/api/get_user_best?k=API KEY&u=' + third + '&limit=5')
            data = r.json()
            msg = ''
            for player in data:
                thr = int(player['count300'])
                hun = int(player['count100'])
                fif = int(player['count50'])
                miss = int(player['countmiss'])
                tph = int(300 * thr + 100 * hun + 50 * fif)
                tnh = int(thr + hun + fif + miss)
                acc = float(tph / (tnh * 3))

                bitits = requests.get('https://osu.ppy.sh/b/' + player['beatmap_id'])
                html = bs4.BeautifulSoup(bitits.text, "lxml")
                tits = html.title.text

                msg += str(
                        'Beatmap : ' + tits + ' `osu.ppy.sh/b/' + player[
                            'beatmap_id'] + '`' + '\n Acc : ' + "%.2f" % float(
                                acc) + ' | ' + 'Rank : ' + player['rank'] + ' | ' + 'PP : ' + player['pp'] + '\n')

            await self.send_message(message.channel, msg + '\nThis request took `' + "%.2f" % (
                time.time() - start_time) + ' seconds` to process. Screw Peppy.')

        # TODO get more Chat Emotes
        if message.content.startswith('!kappa'):
            await self.send_message(message.channel, 'http://i.imgur.com/N5RzfBB.png')

        if message.content.startswith('!feelsbadman'):
            await self.send_message(message.channel, 'http://i.imgur.com/DfURIfh.png')

        if message.content.startswith('!feelsgoodman'):
            await self.send_message(message.channel, 'http://i.imgur.com/9Ggf2vs.png')

        if message.content.startswith('!lapz'):
            await self.send_message(message.channel, 'http://i.imgur.com/I0Lqf3w.png')

    # async def on_member_update(before, after):
    #     bf_serv = before.server
    #     af_serv = after.server
    #     bf_status = before.status
    #     af_status = after.status
    #
    #     if bf_status == 'offline' and af_status == 'online':
    #         await self.send_message(af_serv, 'Wassup {0}, welcome back !'.format(after.mention))

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


bot = Bot()
bot.run('discord_username', 'discord_password')
