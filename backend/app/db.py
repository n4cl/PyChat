import sqlite3
from datetime import datetime, timedelta, timezone

from models.app_coordinator import AppMessage
from models.db_model import MessageModel

SQL_GET_MESSAGE = "SELECT id, title FROM messages WHERE id = ? AND is_deleted = 0;"
SQL_INSERT_MESSAGE = "INSERT INTO messages(title, create_date) VALUES (?, ?);"

t_delta = timedelta(hours=9)
JST = timezone(t_delta, "JST")

class MessageDetailsModel:
    ROLE = "role"
    MESSAGE = "message"


class MessageRole:
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class MessageType:
    TEXT = "text"
    IMAGE_URL = "image_url"


def get_jst_now() -> str:
    """Return JST now as string"""
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")


def connect_db() -> sqlite3.Connection:
    """Return sqlite3 connection"""
    filepath = "db/chat.sqlite"
    conn = sqlite3.connect(filepath)
    return conn


def insert_message(title: str) -> int:
    """Insert message and return lastrowid"""
    conn = connect_db()
    cur = conn.cursor()
    res = cur.execute(SQL_INSERT_MESSAGE, (title, get_jst_now()))
    conn.commit()
    return res.lastrowid


def update_message(message_id: int, title: str) -> None:
    """Update message"""
    conn = connect_db()
    cur = conn.cursor()
    sql = "UPDATE messages SET title = ? WHERE id = ?;"
    cur.execute(sql, (title, message_id))
    conn.commit()


def insert_message_details(mid: int, role: str, model: str, contents: AppMessage) -> None:
    """Insert message_details"""

    def insert_message(cur, mid: int, role: str, model: str, message: str) -> None:
        """Insert message"""
        sql = "INSERT INTO message_details(message_id, role, model, message, create_date) VALUES (?, ?, ?, ?, ?);"
        res = cur.execute(sql, (mid, role, model, message, get_jst_now()))
        return res.lastrowid

    def insert_file(cur, message_detail_id: int, file_name: str, file_type: str, file_path: str) -> None:
        """Insert file"""
        sql = "INSERT INTO file_attachments(message_detail_id, file_name, file_type, file_path) VALUES (?, ?, ?, ?);"
        cur.execute(sql, (message_detail_id, file_name, file_type, file_path))
        return None

    conn = connect_db()
    cur = conn.cursor()
    _message_detail_id = None

    _message_detail_id = insert_message(cur, mid, role, model, contents.message)

    if contents.file:
        insert_file(cur, _message_detail_id, contents.file_name, contents.file_name.split(".")[-1], contents.file)

    conn.commit()
    return None


def get_message(message_id: str):
    """削除されていないメッセージを取得する"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(SQL_GET_MESSAGE, (message_id,))
    return [{"message_id": row[0], "title": row[1]} for row in cur.fetchall()]


def get_messages(page: int, page_size: int):
    """複数のメッセージを取得する"""
    size_per_page = page_size
    offset = (page - 1) * size_per_page
    conn = connect_db()
    cur = conn.cursor()
    sql = "SELECT id, title FROM messages WHERE is_deleted = 0 ORDER BY id DESC LIMIT ? OFFSET ?;"
    cur.execute(
        sql,
        (
            page_size,
            offset,
        ),
    )
    messages = [{"message_id": row[0], "title": row[1]} for row in cur.fetchall()]

    sql = "SELECT COUNT(*) FROM messages WHERE is_deleted = 0;"
    cur.execute(sql)
    count = cur.fetchone()[0]
    total_pages = count // size_per_page + 1
    next_page = page + 1 if page < total_pages else None

    return {"history": messages, "current_page": page, "next_page": next_page, "total_pages": total_pages}


def delete_message(message_id: int):
    """Delete message"""
    conn = connect_db()
    cur = conn.cursor()
    sql = "UPDATE messages SET is_deleted = 1 WHERE id = ?;"
    cur.execute(sql, (message_id,))
    conn.commit()


def select_message_details(mid: int) -> list[MessageModel]:
    """Select message_details"""

    conn = connect_db()
    cur = conn.cursor()
    sql = (
        "SELECT md.id, "
        "c.id as cid, "
        "md.role, "
        "c.file_type, "
        "md.message, "
        "c.file_path, "
        "md.model, "
        "md.create_date, "
        "c.file_name "
        "FROM message_details as md "
        "LEFT OUTER JOIN file_attachments as c "
        "ON md.id = c.message_detail_id "
        "WHERE message_id = ? "
        "ORDER BY md.id ASC, c.id ASC;"
    )
    cur.execute(sql, (mid,))
    rows = cur.fetchall()

    if len(rows) == 0:
        return []
    result = []
    for row in rows:
        _message_model = MessageModel(message_id=row[0],
                                      role=row[2],
                                      model=row[6],
                                      message=row[4],
                                      file_id=row[1],
                                      file_path=row[5],
                                      file_name=row[8],
                                      create_date=row[7])
        result.append(_message_model)
    return result



def get_model(_id) -> tuple[str, int] | tuple[None, None]:
    conn = connect_db()
    cur = conn.cursor()
    sql = "SELECT name, model_providers_id FROM models WHERE id = ?;"
    cur.execute(sql, (_id,))
    row = cur.fetchone()
    if row is None:
        return None, None
    return row[0], row[1]


def get_models() -> list:
    """Get model list"""
    conn = connect_db()
    cur = conn.cursor()
    sql = "SELECT id, name, is_file_attached FROM models WHERE enable = 1 ORDER BY id ASC;"
    cur.execute(sql)
    return [{"id": row[0], "name": row[1], "is_file_attached": bool(row[2])} for row in cur.fetchall()]


def update_model_enable(model: str, enable: int) -> None:
    """Update model enable"""
    conn = connect_db()
    cur = conn.cursor()
    sql = "UPDATE master_model SET enable = ? WHERE model = ?;"
    cur.execute(sql, (enable, model))
    conn.commit()
    return None


def insert_images() -> int:
    """Insert message and return lastrowid"""
    conn = connect_db()
    cur = conn.cursor()
    sql = "INSERT INTO images(create_date) VALUES (?);"
    res = cur.execute(sql, (get_jst_now(),))
    conn.commit()
    return res.lastrowid
