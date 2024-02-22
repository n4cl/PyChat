from unittest.mock import MagicMock, patch

from chat import chat_request, generate_title
from fastapi import status


def test_generate_title():
    with patch('chat.chat_request') as mock_chat_request:
        mock_chat_request.return_value = ("title", status.HTTP_200_OK)
        message = "test message"
        title = generate_title(message)
        assert title == "title"

        mock_chat_request.return_value = ("", status.HTTP_500_INTERNAL_SERVER_ERROR)
        title = generate_title(message)
        assert title == "test message"


def test_chat_request():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="mocked response"))]

    with patch('chat.OpenAI') as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response

        # テスト対象の関数を呼び出し
        messages = [{"role": "user", "content": "Hello"}]
        model = "gpt-3.5-turbo"
        content, status_code = chat_request(messages, model)

        assert content == "mocked response"
        assert status_code == status.HTTP_200_OK

        mock_client.return_value.chat.completions.create.assert_called_once_with(
            model=model,
            temperature=0,
            messages=messages
        )
