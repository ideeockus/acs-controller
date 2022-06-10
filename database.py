import sqlite3
from typing import Optional, Tuple


class UsersAccessControl:
    conn = sqlite3.connect("users_access_control.db")
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
       uid INT PRIMARY KEY,
       fullname TEXT);
    """)
    conn.commit()

    @classmethod
    def add_user(cls, fullname: str, uid: int):
        """Добавить пользователя в БД"""
        cls.cur.execute("INSERT INTO users VALUES(?, ?);", (uid, fullname))
        cls.conn.commit()
        print(f"Добавлен пользователь {fullname} [{uid}]")

    @classmethod
    def get_user_by_uid(cls, uid: int) -> Optional[Tuple[int, str]]:
        """Получить пользователя из БД"""
        cls.cur.execute("SELECT * from users where uid = ?", (uid,))
        user = cls.cur.fetchone()
        print(f"Запрошен пользователь [{uid}]: {user}")
        return user



