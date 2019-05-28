#!/usr/bin/python3
''' Blyat class for a simple bot in development '''

from mysql.connector import connect, errors
COMMANDS = ['!help', '!user add', '!beer add', '!beer remove', '!score']


class NoDB(Exception):
    ''' Custom exception for when no connection to DB '''


class UserExists(Exception):
    ''' Custom exception for when user already exists '''


class Blyat():
    ''' Handle the SQL parts in a nice class '''
    def __init__(self, user, password, host, database):
        try:
            self._cnx = connect(user=user, password=password,
                                host=host, database=database)
            self._cursor = self._cnx.cursor()
        except errors.OperationalError:
            raise NoDB

    def __del__(self):
        ''' Disconnect from the database '''
        if self._cursor is not None:
            self._cursor.close()
        if self._cnx is not None:
            self._cnx.close()
        print('Cleaning upp Blyat class')

    def user_add(self, user):
        ''' Add a user to the scoreboard '''
        try:
            add_user = ('INSERT INTO users (username) '
                        'VALUES (%s)')
            self._cursor.execute(add_user, (user,))

            add_score = ('INSERT INTO scoreboard (user_id, score) '
                         'VALUES (%s, %s)')
            self._cursor.execute(add_score, (self._cursor.lastrowid, 0))
            self._cnx.commit()

        except errors.IntegrityError:
            raise UserExists()

    def beer_alter(self, user, operation):
        ''' Add a beer to the users score '''
        beer_add = ('UPDATE scoreboard INNER JOIN users ON '
                    'scoreboard.user_id = users.id SET score = score %s '
                    'WHERE users.username = %s')
        self._cursor.execute(beer_add, (user, operation))
        self._cnx.commit()

    def show_score(self):
        ''' Return the scoreboard '''
        self._cursor.execute('SELECT users.username, scoreboard.score, '
                             'DATE(scoreboard.last_updated) as date '
                             'FROM scoreboard INNER JOIN users '
                             'ON scoreboard.user_id = users.id '
                             'ORDER BY score DESC; ')

        return self._cursor.fetchall()

    def date_add(self, date):
        ''' Add potential beer dates '''
