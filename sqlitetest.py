#!/usr/bin/python3
''' Some testing of sqlite3 module '''

import sqlite3

try:
    CONN = sqlite3.connect('file:blyat.db?mode=rw', uri=True)
    CONN.execute("PRAGMA foreign_keys = 1")
except sqlite3.OperationalError:
    CONN = sqlite3.connect('blyat.db')
    CONN.execute("PRAGMA foreign_keys = 1")
    CURSOR = CONN.cursor()
    CURSOR.execute('CREATE TABLE users ('
                   'user_id INTEGER PRIMARY KEY, '
                   'username text NOT NULL UNIQUE);')
    CURSOR.execute('CREATE TABLE scoreboard ('
                   'id INTEGER PRIMARY KEY, '
                   'user_id INTEGER NOT NULL, '
                   'score INTEGER DEFAULT 0, '
                   'last_updated text NOT NULL, '
                   'FOREIGN KEY(user_id) REFERENCES users(user_id));')

    CONN.commit()
    CONN.close()
