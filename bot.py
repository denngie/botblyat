#!/usr/bin/python3
''' A simple Discord bot '''

from discord import Client, Game, Embed
from settings import TOKEN
from blyat import Blyat, COMMANDS, UserExists

CLIENT = Client()


@CLIENT.event
async def on_ready():
    ''' Defines what to do when coming online '''
    print('The bot is ready!')
    await CLIENT.change_presence(activity=Game(name='Making a bot'))


@CLIENT.event
async def on_message(message):
    ''' Defines what to do with incoming messages '''
    if message.content in COMMANDS:
        channel = message.channel
        nick = message.author.name
        blyat = Blyat()

    if message.content.startswith('!help'):
        text = 'Jag stödjer följande kommandon:'
        for command in COMMANDS:
            text += '\n  - {}'.format(command)
        await channel.send(text)

    elif message.content.startswith('!user add'):
        try:
            blyat.user_add(nick)
            await channel.send('Du är nu tillagd {}'.format(nick))
        except UserExists:
            await channel.send('Du finns redan {}'.format(nick))

    elif message.content.startswith('!beer'):
        if message.content.startswith('!beer add'):
            operation = '+'
            text = 'En öl tillagd åt {}'.format(nick)
        elif message.content.startswith('!beer remove'):
            operation = '-'
            text = 'En öl borttagen åt {}'.format(nick)
        else:
            return

        blyat.beer_alter(nick, operation)
        await channel.send(text)

    elif message.content.startswith('!score'):
        result = blyat.show_score()

        embed = Embed(title='Ölräkning', type='rich',
                      description='Visar antalet öl per person')

        for (username, score, date) in result:
            embed.add_field(name=username, inline=False,
                            value='Antal: {}, '
                                  'senaste var {}'.format(score, date))
        await channel.send(embed=embed)

CLIENT.run(TOKEN)
