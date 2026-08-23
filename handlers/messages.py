from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from db.queries import get_or_save_chat, get_or_save_user, save_message
from db.session import AsyncSessionLocal
from core.events import message_queue


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if message is None or chat is None or message.text is None:
        return

    await message_queue.put(
        (user.full_name if user else "Unknown", chat.id, message.id, message.business_connection_id, message.text)
    )

    async with AsyncSessionLocal() as session:
        chat_info = await context.bot.get_chat(chat_id=user.id)

        await get_or_save_user(session=session,
                               user_id=user.id,
                               first_name=user.first_name,
                               last_name=user.last_name,
                               username=user.username,
                               bio=chat_info.bio,
                               is_bot=user.is_bot)

        await get_or_save_chat(session=session,
                               chat_id=chat.id,
                               chat_type=chat.type,
                               title=chat.title if chat.title else user.full_name,
                               description=chat_info.description,
                               invite_link=chat_info.invite_link)

        await save_message(session=session,
                           message_id=message.id,
                           chat_id=chat.id,
                           user_id=user.id,
                           text=message.text,
                           reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None,
                           sent_by_bot=user.is_bot)

        await session.commit()


message_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_messages
)
