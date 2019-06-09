#!/usr/bin/python3
''' Blyat class for a simple bot in development '''

# from mysql.connector import connect, errors
from sqlite3 import connect, IntegrityError, OperationalError
from datetime import date, datetime

COMMANDS = ['!help', '!user add', '!beer add', '!beer remove', '!score',
            '!date add', '!beer dates']


class ItemExists(Exception):
    ''' Custom exception for when item already exists '''


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
            raise ItemExists()

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

    def date_add(self, beer_date):
        ''' Add potential beer dates '''
        try:
            beer_date = datetime.strptime(beer_date, '%Y-%m-%d')
            if beer_date.date() >= date.today():
                try:
                    date_add = 'INSERT INTO beer_dates (date) VALUES (?)'
                    self._cursor.execute(date_add, (beer_date.date(),))
                except IntegrityError:
                    raise ItemExists()
            else:
                raise InvalidDate()
        except ValueError:
            raise InvalidDate()

    def show_dates(self):
        ''' Return the dates '''
        self._cursor.execute('SELECT date FROM beer_dates ORDER BY date ASC;')
        return self._cursor.fetchall()
