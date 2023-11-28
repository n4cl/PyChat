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

def insert_message(title: str) -> int:
    """Insert message and return lastrowid"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'INSERT INTO messages(title, create_date) VALUES (?, ?);'
    res = cur.execute(sql, (title, get_jst_now()))
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

def get_message():
    """Get message"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'SELECT id, title FROM messages WHERE is_deleted = 0 ORDER BY id DESC;'
    cur.execute(sql)
    return [{"message_id": row[0], "title": row[1]} for row in cur.fetchall()]

def select_message_details(mid: int) -> list[dict[str, str]]:
    """Select message_details"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'SELECT role, message FROM message_details WHERE mid = ? ORDER BY id;'
    cur.execute(sql, (mid, ))
    return [{"role": row[0], "content": row[1]} for row in cur.fetchall()]

def get_model_list() -> list:
    """Get model list"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'SELECT model FROM master_model WHERE enable = 1;'
    cur.execute(sql)
    return [row[0] for row in cur.fetchall()]

def update_model_enable(model: str, enable: int) -> None:
    """Update model enable"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'UPDATE master_model SET enable = ? WHERE model = ?;'
    cur.execute(sql, (enable, model))
    conn.commit()
    return None

def insert_images() -> int:
    """Insert message and return lastrowid"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'INSERT INTO images(create_date) VALUES (?);'
    res = cur.execute(sql, (get_jst_now(), ))
    conn.commit()
    return res.lastrowid
