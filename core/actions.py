async def send_message(bot, chat_id, text, business_connection_id=None):
    kwargs = {"chat_id": chat_id, "text": text}
    if business_connection_id:
        kwargs["business_connection_id"] = business_connection_id
    return await bot.send_message(**kwargs)


async def reply_message(bot, chat_id, message_id, text, business_connection_id=None):
    kwargs = {
        "chat_id": chat_id,
        "reply_to_message_id": message_id,
        "text": text,
    }
    if business_connection_id:
        kwargs["business_connection_id"] = business_connection_id
    return await bot.send_message(**kwargs)
