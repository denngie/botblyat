#!/usr/bin/python3
''' A simple Discord bot '''

# from asyncio import TimeoutError as asyncio_TimeoutError
import asyncio
# import discord
from discord import Client, Game, Embed
from mysql.connector import connect
from settings import TOKEN
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE
from blyat import Blyat, UserExists, NoDB

CLIENT = Client()


@CLIENT.event
async def on_ready():
    ''' Defines what to do when coming online '''
    print('The bot is ready!')
    await CLIENT.change_presence(activity=Game(name='Making a bot'))


@CLIENT.event
async def on_message(message):
    ''' Defines what to do with incoming messages '''
    if message.content.startswith('!help'):
        channel = message.channel
        await channel.send('I support the following commands:\n'
                           '  - !greet\n'
                           '  - !user add\n'
                           '  - !beer [add/remove]\n'
                           '  - !score')

    elif message.content.startswith('!greet'):
        channel = message.channel
        await channel.send('Say hello!')

        def check(msg):
            return msg.content == 'hello' and msg.channel == channel

        try:
            await CLIENT.wait_for('message', check=check, timeout=60)
            await channel.send('Hello {.author}'.format(message))
        except asyncio.TimeoutError:
            await channel.send('I guess not {.author} :frog:'.format(message))

    elif message.content.startswith('!score'):
        channel = message.channel
        cnx = connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
                      host=MYSQL_HOST, database=MYSQL_DATABASE)
        cursor = cnx.cursor()
        cursor.execute('SELECT users.username, scoreboard.score, '
                       'DATE(scoreboard.last_updated) as date FROM scoreboard '
                       'INNER JOIN users ON scoreboard.user_id = users.id '
                       'ORDER BY score DESC; ')

        embed = Embed(title='Ölräkning', type='rich',
                      description='Visar antalet öl per person')

        for (username, score, date) in cursor:
            embed.add_field(name=username,
                            value='Antal: {}, '
                                  'senaste var {}'.format(score, date),
                            inline=False)

        cursor.close()
        cnx.close()

        await channel.send(embed=embed)

    elif message.content.startswith('!user add'):
        channel = message.channel
        nick = message.author.name

        try:
            blyat = Blyat(MYSQL_USER, MYSQL_PASSWORD,
                          MYSQL_HOST, MYSQL_DATABASE)
            blyat.add_user(nick)
            await channel.send('Du är nu tillagd {}'.format(nick))

        except NoDB:
            await channel.send('Något gick fel, förlåt {}'.format(nick))
        except UserExists:
            await channel.send('Du finns redan {}'.format(nick))

    elif message.content.startswith('!beer add'):
        channel = message.channel
        nick = message.author.name

        cnx = connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
                      host=MYSQL_HOST, database=MYSQL_DATABASE)
        cursor = cnx.cursor()
        beer_add = ('UPDATE scoreboard INNER JOIN users ON '
                    'scoreboard.user_id = users.id SET score = score + 1 '
                    'WHERE users.username = %s')
        cursor.execute(beer_add, nick)
        cnx.commit()

        cursor.close()
        cnx.close()
        await channel.send('En öl tillagd åt {}'.format(nick))

    elif message.content.startswith('!beer remove'):
        channel = message.channel
        nick = message.author.name

        cnx = connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
                      host=MYSQL_HOST, database=MYSQL_DATABASE)
        cursor = cnx.cursor()
        beer_add = ('UPDATE scoreboard INNER JOIN users ON '
                    'scoreboard.user_id = users.id SET score = score - 1 '
                    'WHERE users.username = %s')
        cursor.execute(beer_add, nick)
        cnx.commit()

        cursor.close()
        cnx.close()
        await channel.send('En öl borttagen åt {}'.format(nick))


CLIENT.run(TOKEN)
