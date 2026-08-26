from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from db.queries import get_or_save_chat, get_or_save_user, save_message, get_or_save_business_connection
from db.session import AsyncSessionLocal
from core.events import message_queue


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if message is None or chat is None or message.text is None:
        return

    business_id = message.business_connection_id

    await message_queue.put(
        (user.full_name if user else "Unknown", chat.id, message.id, business_id, message.text)
    )

    bio = None
    description = None
    invite_link = None
    if not business_id:
        try:
            chat_info = await context.bot.get_chat(chat_id=chat.id)
            bio = getattr(chat_info, "bio", None)
            description = getattr(chat_info, "description", None)
            invite_link = getattr(chat_info, "invite_link", None)
        except Exception:
            pass

    async with AsyncSessionLocal() as session:
        db_business = None
        if business_id:
            db_business = await get_or_save_business_connection(
                session=session,
                connection_id=business_id,
                user_chat_id=chat.id,
            )

        db_user = await get_or_save_user(
            session=session,
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            bio=bio,
            is_bot=user.is_bot)

        db_chat = await get_or_save_chat(
            session=session,
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title if chat.title else user.full_name,
            description=description,
            invite_link=invite_link,
            business_connection_id=db_business.id if db_business else None,
        )

        await save_message(
            session=session,
            message_id=message.id,
            chat_id=db_chat.id,
            user_id=db_user.id,
            text=message.text,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None,
            sent_by_bot=user.is_bot,
            business_connection_id=db_business.id if db_business else None
        )

        await session.commit()


message_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_messages
)
