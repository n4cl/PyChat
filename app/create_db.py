import sqlite3

def cereate_select_table_sql(table_name: str) -> str:
    return f"SELECT count(name) FROM sqlite_master WHERE name = \"{table_name}\";"

def create_db():
    filepath = "chat.sqlite"
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()

    res = cur.execute(cereate_select_table_sql("messages"))

    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                create_date TEXT NOT NULL,
                is_deleted INTEGER NOT NULL DEFAULT 0
            );
        """)

    res = cur.execute(cereate_select_table_sql("message_details"))

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

    res = cur.execute(cereate_select_table_sql("master_model"))
    if res.fetchone()[0] == 0:
        cur.execute("""
                CREATE TABLE master_model (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    enable INTEGER NOT NULL
                );
            """)

    res = cur.execute(cereate_select_table_sql("user_setting"))
    if res.fetchone()[0] == 0:
        cur.execute("""
                CREATE TABLE user_setting (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    unique(setting_name)
                );
            """)

    res = cur.execute(cereate_select_table_sql("images"))
    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                create_date TEXT NOT NULL
            );
        """)
    res = cur.execute(cereate_select_table_sql("image_details"))
    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE image_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                images_id INTEGER NOT NULL,
                model TEXT,
                prompt TEXT NOT NULL,
                size TEXT NOT NULL,
                quality TEXT NOT NULL,
                create_date TEXT NOT NULL,
                foreign key (images_id) references images(id)
            );
        """)
    res = cur.execute(cereate_select_table_sql("image_entities"))
    if res.fetchone()[0] == 0:
        cur.execute("""
            CREATE TABLE image_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_details_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                file TEXT NOT NULL,
                foreign key (image_details_id) references images(id)
            );
        """)

    conn.commit()

create_db()
