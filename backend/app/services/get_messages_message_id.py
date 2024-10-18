from db import select_message_details


def get_message_from_db(message_id: int) -> dict:
    """Get message from db"""
    message_details = select_message_details(message_id)
    result = []
    for message in message_details:
        result.append(
            {
                "role": message.role,
                "content": message.message,
                "model": message.model,
                "create_date": message.create_date,
            }
        )

    return result
