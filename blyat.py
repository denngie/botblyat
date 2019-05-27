#!/usr/bin/python3
''' Blyat class for a simple bot in development '''

from mysql.connector import connect, errors


class NoDB(Exception):
    ''' Custom exception for when no connection to DB '''


class UserExists(Exception):
    ''' Custom exception for when user already exists '''


class Blyat():
    ''' Handle the SQL parts in a nice class '''
    def __init__(self, user, password, host, database):
        self._cnx = None
        self._cursor = None
        self._user = user
        self._password = password
        self._host = host
        self._database = database

    def _connect(self):
        ''' Connect to the database '''
        try:
            self._cnx = connect(user=self._user, password=self._password,
                                host=self._host, database=self._database)
            self._cursor = self._cnx.cursor()
        except errors.OperationalError:
            raise NoDB

    def _disconnect(self):
        ''' Disconnect from the database '''
        self._cursor.close()
        self._cursor = None
        self._cnx.close()
        self._cnx = None

    def user_add(self, user):
        ''' Add a user to the scoreboard '''
        self._connect()
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

        self._disconnect()

    def beer_add(self, user):
        ''' Add a beer to the users score '''
        self._connect()

        beer_add = ('UPDATE scoreboard INNER JOIN users ON '
                    'scoreboard.user_id = users.id SET score = score + 1 '
                    'WHERE users.username = %s')
        self._cursor.execute(beer_add, (user,))
        self._cnx.commit()

        self._disconnect()

    def beer_remove(self, date):
        ''' Add potential beer dates '''

    def date_add(self, date):
        ''' Add potential beer dates '''
