#!/usr/bin/python3
''' Blyat class for a simple bot in development '''

# from mysql.connector import connect, errors
from sqlite3 import connect, IntegrityError, OperationalError
from re import search
COMMANDS = ['!help', '!user add', '!beer add', '!beer remove', '!score']


class UserExists(Exception):
    ''' Custom exception for when user already exists '''


class InvalidDate(Exception):
    ''' Custom exception for when date input is invalid '''


class Blyat():
    ''' Handle the DB parts in a nice class '''
    def __init__(self):
        ''' Connect to the database '''
        try:
            self._conn = connect('file:blyat.db?mode=rw', uri=True)
            self._conn.execute("PRAGMA foreign_keys = 1")
            self._cursor = self._conn.cursor()
        except OperationalError:
            self._conn = connect('blyat.db')
            self._conn.execute("PRAGMA foreign_keys = 1")
            self._cursor = self._conn.cursor()
            self._create_db()

    def __del__(self):
        ''' Save and disconnect from the database '''
        self._conn.commit()
        self._conn.close()

    def _create_db(self):
        self._cursor.execute('CREATE TABLE scoreboard ('
                             'username text PRIMARY KEY, '
                             'score INTEGER DEFAULT 0, '
                             'last_updated TIMESTAMP '
                             'DEFAULT CURRENT_TIMESTAMP);')
        self._cursor.execute('CREATE TABLE beer_dates ('
                             'date date PRIMARY KEY);')

    def user_add(self, user):
        ''' Add a user to the scoreboard '''
        try:
            user_add = 'INSERT INTO scoreboard (username) VALUES (?)'
            self._cursor.execute(user_add, (user,))
        except IntegrityError:
            raise UserExists()

    def beer_alter(self, user, operation):
        ''' Add a beer to the users score '''
        beer_add = ('UPDATE scoreboard SET score = score {} 1, '
                    'last_updated = CURRENT_TIMESTAMP '
                    'WHERE username = ?'.format(operation))
        self._cursor.execute(beer_add, (user,))

    def show_score(self):
        ''' Return the scoreboard '''
        self._cursor.execute('SELECT username, score, DATE(last_updated) AS '
                             'date FROM scoreboard ORDER BY score DESC;')

        return self._cursor.fetchall()

    def date_add(self, date):
        ''' Add potential beer dates '''
        if not search('^\\d{4}-\\d{2}-\\d{2}$', date):
            raise InvalidDate()

        try:
            date_add = 'INSERT INTO beer_dates (date) VALUES (?)'
            self._cursor.execute(date_add, (date,))
        except IntegrityError:
            raise UserExists()
