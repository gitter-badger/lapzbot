import requests
import yaml
import time
import bs4

try:
    # Loading configurations from config.yaml
    with open('../configuration/config.yaml', 'r') as f:
        doc = yaml.load(f)
except FileNotFoundError:
    print('The config.yaml file was not found inside the configuration folder.' +
          '\n Make sure the file is present and run the bot again.')
    quit()


def stats(instring):
    # extracting username from the string
    splitted = instring.split()
    uname = splitted[1]
    # key loaded from config.yaml
    key = doc['OSU_API']['KEY']
    r = requests.get('https://osu.ppy.sh/api/get_user?k=' + key + '&u=' + uname)
    data = r.json()
    try:
        for player in data:
            op = str('https://a.ppy.sh/' + player['user_id'] + '\nUsername : ' + player['username']
                     + '\nPerformance Points : ' + "{0:.2f}".format(float(player['pp_raw'])) + '\nAccuracy : '
                     + "{0:.2f}".format(float(player['accuracy'])) + '\nPlaycount : ' + player['playcount']
                     + '\nProfile Link : `osu.ppy.sh/u/' + player['user_id'] + '`')
            result = op
        return result
        # NOTE:- if the result is 'string indices must be integers' that means the API key is wrong
    except Exception as e:
        return str(e)


def top(instring):
    # extracting username from the string
    splitted = instring.split()
    uname = splitted[1]
    start_time = time.time()
    # key loaded from config.yaml
    key = doc['OSU_API']['KEY']
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
                    'Beatmap : ' + tits + ' `osu.ppy.sh/b/' + player[
                        'beatmap_id'] + '`' + '\n Acc : ' + "{0:.2f}".format(float(
                            acc)) + ' | ' + 'Rank : ' + player['rank'] + ' | ' + 'PP : ' + player['pp'] + '\n')

        result = str(msg + '\nThis request took `' + "{0:.2f}".format((
            time.time() - start_time)) + ' seconds` to process.')

        return result
        # NOTE:- if the result is 'string indices must be integers' that means the API key is wrong
    except Exception as e:
        return str(e)
