import sqlite3
from datetime import datetime, timedelta, timezone

t_delta = timedelta(hours=9)
JST = timezone(t_delta, 'JST')

class MessageRole:
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


def get_jst_now() -> str:
    """Return JST now as string"""
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

def connect_db() -> sqlite3.Connection:
    """Return sqlite3 connection"""
    filepath = "chat.sqlite"
    conn = sqlite3.connect(filepath)
    return conn

def insert_message() -> int:
    """Insert message and return lastrowid"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'INSERT INTO messages(create_date) VALUES (?);'
    res = cur.execute(sql, (get_jst_now(), ))
    conn.commit()
    return res.lastrowid

def insert_message_details(mid: int, role: str, model: str, message: str) -> None:
    """Insert message_details"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'INSERT INTO message_details(mid, role, model, message, create_date) VALUES (?, ?, ?, ?, ?);'
    cur.execute(sql, (mid, role, model, message, get_jst_now()))
    conn.commit()
    return None
