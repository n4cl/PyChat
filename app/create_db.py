import sqlite3

def create_db():
    filepath = "chat.sqlite"
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()

    res = cur.execute("""
        SELECT count(name) FROM sqlite_master WHERE name = "messages";
    """)

    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                create_date TEXT NOT NULL
            );
        """)

    res = cur.execute("""
        SELECT count(name) FROM sqlite_master WHERE name = "message_details";
    """)

    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE message_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid INTEGER NOT NULL,
                role TEXT NOT NULL,
                model TEXT,
                message TEXT NOT NULL,
                create_date TEXT NOT NULL,
                foreign key (mid) references messages(id)
            );
        """)
    else:
        return

    conn.commit()

create_db()
