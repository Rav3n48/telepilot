from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from sqlalchemy import select

from db.models import User, Chat, ChatType, Message
from db.session import AsyncSessionLocal
from core.events import message_queue


def _update_user(db_user, user):
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.username = user.username


async def _get_or_create_user(user, session):
    if user:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            db_user = User(
                telegram_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                is_bot=user.is_bot,
            )
            session.add(db_user)
            await session.flush()
        _update_user(db_user, user)
        return db_user
    return None


def _update_chat(db_chat, chat):
    db_chat.title = chat.title


async def _get_or_create_chat(chat, session):
    result = await session.execute(
        select(Chat).where(
            Chat.telegram_chat_id == chat.id
        )
    )

    db_chat = result.scalar_one_or_none()

    if db_chat is None:
        db_chat = Chat(
            telegram_chat_id=chat.id,
            type=ChatType(chat.type),
            title=chat.title,
        )

        session.add(db_chat)
        await session.flush()
    _update_chat(db_chat, chat)
    return db_chat


async def _create_message(user, chat, message, session):
    db_message = Message(
        telegram_message_id=message.message_id,
        chat_id=chat.id,
        user_id=user.id if user else None,
        text=message.text,
        sent_by_bot=False,
    )

    session.add(db_message)


async def handle_messages(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if message is None or chat is None or message.text is None:
        return

    await message_queue.put(
        (user.full_name if user else "Unknown", chat.id, message.id, message.business_connection_id, message.text)
    )

    async with AsyncSessionLocal() as session:
        db_user = await _get_or_create_user(user, session)
        db_chat = await _get_or_create_chat(chat, session)
        await _create_message(db_user, db_chat, message, session)

        await session.commit()


message_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_messages
)
