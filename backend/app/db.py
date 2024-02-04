import sqlite3
from datetime import datetime, timedelta, timezone

SQL_GET_MESSAGE = "SELECT id, title FROM messages WHERE id = ? AND is_deleted = 0;"
SQL_INSERT_MESSAGE = "INSERT INTO messages(title, create_date) VALUES (?, ?);"

t_delta = timedelta(hours=9)
JST = timezone(t_delta, 'JST')

class MessageRole:
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class MessageKey:
    ROLE = "role"
    CONTENT = "content"
    TYPE = "type"
    TEXT = "text"
    IMAGE_URL = "image_url"
    MODEL = "model"

class MessageType:
    TEXT = "text"
    IMAGE_URL = "image_url"

class DataType:
    TEXT = "text"
    FILE = "file"


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
    res = cur.execute(SQL_INSERT_MESSAGE, (title, get_jst_now()))
    conn.commit()
    return res.lastrowid

def insert_message_details(mid: int, role: str, model: str, contents: dict) -> None:
    """Insert message_details"""

    def insert_contents(mdid: int, data_type: str, message: str, file_path: str) -> None:
        """Insert contents"""
        sql = 'INSERT INTO contents(mdid, data_type, message, file_path) VALUES (?, ?, ?, ?);'
        cur.execute(sql, (mdid, data_type, message, file_path))
        return None

    conn = connect_db()
    cur = conn.cursor()
    sql = 'INSERT INTO message_details(mid, role, model, create_date) VALUES (?, ?, ?, ?);'
    res = cur.execute(sql, (mid, role, model, get_jst_now()))

    mdid = res.lastrowid

    for data_type, message in contents.items():
        if data_type == DataType.TEXT:
            insert_contents(mdid, MessageType.TEXT, message, None)
        elif data_type == DataType.FILE:
            insert_contents(mdid, MessageType.IMAGE_URL, None, message)

    conn.commit()
    return None

def get_message(message_id: str):
    """削除されていないメッセージを取得する"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(SQL_GET_MESSAGE, (message_id, ))
    return [{"message_id": row[0], "title": row[1]} for row in cur.fetchall()]

def get_messages(page: int):
    """複数のメッセージを取得する"""
    size_per_page = 20
    offset = (page - 1) * size_per_page
    conn = connect_db()
    cur = conn.cursor()
    sql = 'SELECT id, title FROM messages WHERE is_deleted = 0 ORDER BY id DESC LIMIT 20 OFFSET ?;'
    cur.execute(sql, (offset, ))
    messages = [{"message_id": row[0], "title": row[1]} for row in cur.fetchall()]

    sql = 'SELECT COUNT(*) FROM messages WHERE is_deleted = 0;'
    cur.execute(sql)
    count = cur.fetchone()[0]
    total_pages = count // size_per_page + 1
    next_page = page + 1 if page < total_pages else None

    return {"history": messages, "current_page": page, "next_page": next_page, "total_pages": total_pages}


def delete_message(message_id: int):
    """Delete message"""
    conn = connect_db()
    cur = conn.cursor()
    sql = 'UPDATE messages SET is_deleted = 1 WHERE id = ?;'
    cur.execute(sql, (message_id, ))
    conn.commit()


def select_message_details(mid: int,
                           is_multiple_input: bool=False,
                           required_column=None) -> list[dict[str, str]]:
    """Select message_details"""

    if required_column is None:
        required_column = {'role', 'message'}

    conn = connect_db()
    cur = conn.cursor()
    sql = ('SELECT md.id as mdid, '
                  'c.id as cid, '
                  'md.role, '
                  'c.data_type, '
                  'c.message, '
                  'c.file_path, '
                  'md.model '
           'FROM message_details as md '
           'INNER JOIN contents as c '
           'ON md.id = c.mdid '
           'WHERE mid = ? '
           'ORDER BY md.id ASC, c.id ASC;')
    cur.execute(sql, (mid, ))
    rows = cur.fetchall()

    if not is_multiple_input:
        results = []
        # 生のSQLだと綺麗に取得できないのでここで整形する
        for row in rows:
            result = {}
            if "role" in required_column:
                result[MessageKey.ROLE] = row[2]
            if "message" in required_column:
                result[MessageKey.CONTENT] = row[4]
            if "model" in required_column:
                result[MessageKey.MODEL] = row[6]
            results.append(result)
        return results


    temp_mdid = rows[0][0]
    messages = []
    message = {}
    for row in rows:
        if temp_mdid != row[0]:
            temp_mdid = row[0]
            messages.append(message)

        if MessageKey.ROLE not in message:
            message[MessageKey.ROLE] = row[2]
            message[MessageKey.CONTENT] = []

        file_type = row[3]
        if file_type == DataType.TEXT:
            message[MessageKey.CONTENT].append({MessageKey.TYPE: MessageType.TEXT, MessageKey.CONTENT: row[4]})
        elif file_type == DataType.FILE:
            message[MessageKey.CONTENT].append({MessageKey.TYPE: MessageType.IMAGE_URL , MessageKey.IMAGE_URL: row[5]})
    return messages

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
