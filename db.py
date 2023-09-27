import sqlite3
from aiogram.types import Message

class SQLite:
    # region stuff
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        self.do("""CREATE TABLE IF NOT EXISTS user (
    id       INTEGER PRIMARY KEY
                     UNIQUE
                     NOT NULL,
    name     TEXT,
    is_admin INTEGER DEFAULT (0) 
);""")

        self.do("""CREATE TABLE IF NOT EXISTS command (
    id      INTEGER PRIMARY KEY AUTOINCREMENT
                    UNIQUE
                    NOT NULL,
    user_id INTEGER REFERENCES user (id),
    name    TEXT,
    args    TEXT,
    active  INTEGER DEFAULT (0) 
);""")

    def do(self, query: str, values=()) -> None:
        self.cursor.execute(query, values)
        self.connection.commit()

    def read(self, query: str, values=(), one=False) -> tuple:
        self.cursor.execute(query, values)
        return self.cursor.fetchone() if one else self.cursor.fetchall()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    # endregion
    # region user

    def user_exists(self, user_id: str) -> bool:
        result = self.read('SELECT id FROM user WHERE id = ?', (user_id,), one=True)
        return bool(result is None)

    def new_user(self, user_id: int, username: str) -> None:
        self.do('INSERT INTO user (id, name) VALUES (?, ?)', (user_id, username))

    def is_admin(self, message: Message) -> bool:
        return not bool(self.read('SELECT is_admin FROM user WHERE id = ?', (message.from_user.id,))[0])
    # endregion
    # region command_bot

    def add_command(self, user_id: int, command: str, command_name: str) -> None:
        self.do('INSERT INTO command (user_id, name, args) VALUES (?, ?, ?)', (user_id, command_name, command))

    def delete_command(self, command_id: int) -> None:
        self.do('DELETE FROM command WHERE id = ?', (command_id,))

    def activate_command(self, command_id: int) -> None:
        self.do('UPDATE command SET active = 1 WHERE id = ?', (command_id,))

    def deactivate_command(self) -> None:
        self.do('UPDATE command SET active = 0 WHERE active = 1')

    def read_for_bot(self, user_id: int) -> tuple:
        return self.read('SELECT id, name FROM command WHERE user_id IS NULL OR user_id = ?', (user_id,))

    def command_name_from_id(self, command_id: int) -> str:
        return self.read('SELECT name FROM command WHERE id = ?', (command_id,), one=True)[0]
    # endregion
    # region command_api

    def api_read(self):
        result = self.read('SELECT args FROM command WHERE active = 1', one=True)

        if result is not None:
            result = result[0]

            if result.count(', ') != 0:
                result = result.split(', ')
            else:
                result = [result]

        return result

    # endregion
