import os
import sqlite3

DB_PATH = "/usr/local/app/backend/app/db/chat.sqlite"

def cereate_select_table_sql(table_name: str) -> str:
    return f'SELECT count(name) FROM sqlite_master WHERE name = "{table_name}";'


def exists_db(db_path):
    return os.path.exists(db_path)


def create_db(cur):

    res = cur.execute(cereate_select_table_sql("messages"))

    if res.fetchone()[0] == 0:
        cur.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                create_date TEXT NOT NULL,
                is_deleted INTEGER NOT NULL DEFAULT 0
            );
        """
        )

    res = cur.execute(cereate_select_table_sql("message_details"))

    if res.fetchone()[0] == 0:
        cur.execute(
            """
            CREATE TABLE message_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                model TEXT,
                message TEXT,
                create_date TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (message_id) REFERENCES messages(id)
            );
            """
        )

    res = cur.execute(cereate_select_table_sql("contents"))

    if res.fetchone()[0] == 0:
        cur.execute(
            """
            CREATE TABLE file_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_detail_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                upload_date TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (message_detail_id) REFERENCES message_details(id)
            );
        """
        )

    res = cur.execute(cereate_select_table_sql("model_providers"))
    if res.fetchone()[0] == 0:
        cur.execute(
            """
                CREATE TABLE model_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
            """
        )

    res = cur.execute(cereate_select_table_sql("models"))
    if res.fetchone()[0] == 0:
        cur.execute(
            """
                CREATE TABLE models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_providers_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_file_attached INTEGER NOT NULL,
                    enable INTEGER NOT NULL,
                    foreign key (model_providers_id) references model_providers(id)
                );
            """
        )

    res = cur.execute(cereate_select_table_sql("user_setting"))
    if res.fetchone()[0] == 0:
        cur.execute(
            """
                CREATE TABLE user_setting (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    unique(setting_name)
                );
            """
        )


def initialize_records(cur):


    # OpenAI, Anthropic を初期値として登録
    cur.execute(
        """
        INSERT INTO model_providers (id, name) VALUES (1, "openai"), (2, "anthropic"), (3, "google");
        """
    )
    cur.execute(
        """
        INSERT INTO "main"."models" ("id", "model_providers_id", "name", "is_file_attached", "enable")
        VALUES ('1', '1', 'gpt-4o-2024-08-06', '1', '1'),
               ('2', '2', 'claude-3-5-sonnet-20240620', '0', '1'),
               ('3', '1', 'gpt-4o-mini-2024-07-18', '0', '1'),
               ('4', '3', 'gemini-1.5-flash', '1', '1');
        """
    )


if __name__ == "__main__":
    if exists_db(DB_PATH):
        print("db already exists")
    else:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        create_db(cur)
        initialize_records(cur)
        conn.commit()
        print("create db")
