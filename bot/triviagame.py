import requests
import re

removebadtags = re.compile(r'<[^>]+>')
removebadarticles = re.compile('\\b(the)\\W', re.I)

async def quiz(self, message):
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
