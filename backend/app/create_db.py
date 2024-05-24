import os
import sqlite3


def cereate_select_table_sql(table_name: str) -> str:
    return f'SELECT count(name) FROM sqlite_master WHERE name = "{table_name}";'


def remove_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
        print("remove db")


def create_db(initialize=False):
    filepath = "chat.sqlite"

    if initialize:
        remove_db(filepath)

    conn = sqlite3.connect(filepath)
    cur = conn.cursor()

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
                mid INTEGER NOT NULL,
                role TEXT NOT NULL,
                model TEXT,
                create_date TEXT NOT NULL,
                foreign key (mid) references messages(id)
            );
        """
        )

    res = cur.execute(cereate_select_table_sql("contents"))

    if res.fetchone()[0] == 0:
        cur.execute(
            """
            CREATE TABLE contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mdid INTEGER NOT NULL,
                data_type TEXT NOT NULL,
                message TEXT,
                file_path TEXT,
                foreign key (mdid) references message_details(id)
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

    conn.commit()


def initialize_records():
    conn = sqlite3.connect("chat.sqlite")
    cur = conn.cursor()

    # OpenAI, Anthropic を初期値として登録
    cur.execute(
        """
        INSERT INTO model_providers (name) VALUES (1, "openai"), (1, "anthropic");
        """
    )

    conn.commit()


if __name__ == "__main__":
    create_db(initialize=True)
    print("create db")
