from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from db import SQL_GET_MESSAGE, SQL_INSERT_MESSAGE, connect_db, get_jst_now, get_message, get_models, insert_message


def test_get_jst_now():
    t_delta = timedelta(hours=9)
    JST = timezone(t_delta, "JST")
    expected = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    assert get_jst_now() == expected


@patch("sqlite3.connect")
def test_connect_db(mock_connect):
    mock_connect.return_value = MagicMock()
    connect_db()
    mock_connect.assert_called_once_with("db/chat.sqlite")


@patch("sqlite3.connect")
def test_insert_message(mock_connect):
    mock_connect.return_value = MagicMock()
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.execute.return_value.lastrowid = 1

    title = "test title"
    result = insert_message(title)

    assert result == 1
    mock_cursor.execute.assert_called_once_with(SQL_INSERT_MESSAGE, (title, get_jst_now()))


@patch("sqlite3.connect")
def test_get_message(mock_connect):
    mock_connect.return_value = MagicMock()
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [(1, "test title")]

    message_id = "1"
    result = get_message(message_id)

    assert result == [{"message_id": 1, "title": "test title"}]
    mock_cursor.execute.assert_called_once_with(SQL_GET_MESSAGE, (message_id,))


@patch("sqlite3.connect")
def test_get_models(mock_connect):
    mock_connect.return_value = MagicMock()
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [[1, "name", 1]]
    result = get_models()
    assert result == [{"id": 1, "name": "name", "is_file_attached": 1}]
