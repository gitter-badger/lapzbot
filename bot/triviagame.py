import requests

async def quiz(self, message):
    r = requests.get('http://jservice.io/api/random?')
    data = r.json()

    for player in data:
        await self.send_message(message.channel, player['question'])

        guess = await self.wait_for_message(timeout=10.0, author=message.author)
        guess_l = str(guess).lower()
        answer = str(player['answer']).lower()
        set1 = set(guess_l.split(' '))
        set2 = set(answer.split(' '))
        if guess_l is None:
            fmt = 'Sorry, you took too long. It was {}.'
            await self.send_message(message.channel, fmt.format(answer))
            return
        if set1 == set2:
            await self.send_message(message.channel, 'You are right!')
        else:
            await self.send_message(message.channel, 'Sorry. It is actually {}.'.format(answer))
