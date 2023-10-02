import aiosqlite
from aiogram.types import Message

class SQLite:
    # region stuff
    def __init__(self, db_name):
        self.connection = None
        self.cursor = None
        self.db_name = db_name

    async def init(self):
        db_name = self.db_name
        self.connection = await aiosqlite.connect(db_name)
        self.cursor = await self.connection.cursor()

        await self.do("""CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY UNIQUE NOT NULL,
            name TEXT,
            is_admin INTEGER DEFAULT (0)
        );""")

        await self.do("""CREATE TABLE IF NOT EXISTS command (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            user_id INTEGER REFERENCES user (id),
            name TEXT,
            args TEXT
        );""")

        await self.do("""CREATE TABLE IF NOT EXISTS pc (
            ip TEXT PRIMARY KEY UNIQUE NOT NULL,
            active_command INTEGER REFERENCES command (id)
        );""")

    async def do(self, query: str, values=()) -> None:
        await self.cursor.execute(query, values)
        await self.connection.commit()

    async def read(self, query: str, values=(), one=False) -> tuple:
        await self.cursor.execute(query, values)
        if one:
            return await self.cursor.fetchone()
        else:
            return await self.cursor.fetchall()

    async def close(self):
        await self.cursor.close()
        await self.connection.close()
    # endregion
    # region user

    async def user_exists(self, user_id: str) -> bool:
        result = await self.read('SELECT id FROM user WHERE id = ?', (user_id,), one=True)
        return bool(result is None)

    async def new_user(self, user_id: int, username: str) -> None:
        await self.do('INSERT INTO user (id, name) VALUES (?, ?)', (user_id, username))

    async def is_admin(self, message: Message) -> bool:
        result = await self.read('SELECT is_admin FROM user WHERE id = ?', (message.from_user.id,), one=True)
        return not bool(result[0])
    # endregion
    # region command_bot

    async def add_command(self, user_id: int, command: str, command_name: str) -> None:
        await self.do('INSERT INTO command (user_id, name, args) VALUES (?, ?, ?)', (user_id, command_name, command))

    async def delete_command(self, command_id: int) -> None:
        await self.do('DELETE FROM command WHERE id = ?', (command_id,))

    async def activate_command(self, command_id: int, ip: str) -> None:
        if ip != 'all':
            await self.do('UPDATE pc SET active_command = ? WHERE ip = ?', (command_id, ip))
        else:
            await self.do('UPDATE pc SET active_command = ?', (command_id,))

    async def deactivate_command(self) -> None:
        await self.do('UPDATE pc SET active_command = NULL')

    async def read_for_bot(self, user_id: int) -> tuple:
        return await self.read('SELECT id, name FROM command WHERE user_id IS NULL OR user_id = ?', (user_id,))

    async def command_name_from_id(self, command_id: int) -> str:
        result = await self.read('SELECT name FROM command WHERE id = ?', (command_id,), one=True)
        return result[0]

    async def get_pc(self) -> tuple:
        result = await self.read('SELECT ip, ip FROM pc')
        return [('all', 'all')] + list(result)

    # endregion
    # region api
    async def pc_exists(self, ip):
        result = await self.read('SELECT ip FROM pc WHERE ip = ?', (ip,), one=True)
        return bool(result is None)

    async def add_pc(self, ip):
        await self.do('INSERT INTO pc (ip) VALUES (?)', (ip,))

    async def api_read(self, ip: str):
        result = await self.read('''SELECT c.args
            FROM command AS c
            JOIN pc AS p ON c.id = p.active_command
            WHERE p.ip = ?''', (ip,), one=True)

        if result is not None:
            result = result[0]

            if result.count(', ') != 0:
                result = result.split(', ')
            else:
                result = [result]

        return result

    # endregion
