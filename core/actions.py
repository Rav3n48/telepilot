import logging

from db.queries import save_bot_message

logger = logging.getLogger(__name__)


async def send_message(bot, chat_id, text, business_connection_id=None):
    kwargs = {"chat_id": chat_id, "text": text}
    if business_connection_id:
        kwargs["business_connection_id"] = business_connection_id
    sent = await bot.send_message(**kwargs)
    try:
        chat = getattr(sent, "chat", None)
        chat_telegram_id = getattr(chat, "id", chat_id) if chat is not None else chat_id
        telegram_message_id = getattr(sent, "message_id", None) or getattr(sent, "id", None)
        text_to_save = getattr(sent, "text", None) or text
        business_id_to_save = business_connection_id or getattr(sent, "business_connection_id", None)
        if telegram_message_id is not None:
            await save_bot_message(
                chat_telegram_id=chat_telegram_id,
                telegram_message_id=telegram_message_id,
                text=text_to_save,
                business_connection_id=business_id_to_save,
            )
    except Exception as e:
        logger.warning(f"Failed to persist sent message: {e}", exc_info=True)
    return sent


async def reply_message(bot, chat_id, message_id, text, business_connection_id=None):
    kwargs = {
        "chat_id": chat_id,
        "reply_to_message_id": message_id,
        "text": text,
    }
    if business_connection_id:
        kwargs["business_connection_id"] = business_connection_id
    sent = await bot.send_message(**kwargs)
    try:
        chat = getattr(sent, "chat", None)
        chat_telegram_id = getattr(chat, "id", chat_id) if chat is not None else chat_id
        telegram_message_id = getattr(sent, "message_id", None) or getattr(sent, "id", None)
        text_to_save = getattr(sent, "text", None) or text
        business_id_to_save = business_connection_id or getattr(sent, "business_connection_id", None)
        if telegram_message_id is not None:
            await save_bot_message(
                chat_telegram_id=chat_telegram_id,
                telegram_message_id=telegram_message_id,
                text=text_to_save,
                reply_to_telegram_message_id=message_id,
                business_connection_id=business_id_to_save,
            )
    except Exception as e:
        logger.warning(f"Failed to persist reply message: {e}", exc_info=True)
    return sent
