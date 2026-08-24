import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models import User, Chat, ChatType, Message, BusinessConnection
from .session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def _update_user(db_user, first_name, last_name, username, bio):
    db_user.first_name = first_name
    db_user.last_name = last_name
    db_user.username = username
    db_user.bio = bio


async def get_or_save_user(session, user_id, first_name, last_name=None, username=None, bio=None, is_bot=False):
    try:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            db_user = User(
                telegram_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                bio=bio,
                is_bot=is_bot,
            )
            session.add(db_user)
            await session.flush()
        _update_user(db_user, first_name, last_name, username, bio)
        return db_user
    except Exception as e:
        logger.error(f"Error in get_or_save_user: {e}")
        return None


def _update_chat(db_chat, title, description, invite_link):
    db_chat.title = title
    db_chat.description = description
    db_chat.invite_link = invite_link


async def get_or_save_chat(session, chat_id, chat_type, title, description=None, invite_link=None, business_connection_id=None):
    try:
        result = await session.execute(
            select(Chat).where(
                Chat.telegram_chat_id == chat_id
            )
        )

        db_chat = result.scalar_one_or_none()

        if db_chat is None:
            db_chat = Chat(
                telegram_chat_id=chat_id,
                type=ChatType(chat_type),
                title=title,
                description=description,
                invite_link=invite_link,
                business_connection_id=business_connection_id,
            )

            session.add(db_chat)
            await session.flush()
        _update_chat(db_chat, title, description, invite_link)
        return db_chat
    except Exception as e:
        logger.error(f"Error in get_or_save_chat: {e}")
        return None


async def save_message(session, message_id, chat_id, user_id=None, text=None, reply_to_message_id=None, sent_by_bot=False, business_connection_id=None):
    try:
        db_message = Message(
            telegram_message_id=message_id,
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            sent_by_bot=sent_by_bot,
            business_connection_id=business_connection_id,
        )

        session.add(db_message)
        return db_message
    except Exception as e:
        logger.error(f"Error in save_message: {e}")
        return None


async def get_or_save_business_connection(session, connection_id, user_chat_id):
    try:
        result = await session.execute(
            select(BusinessConnection).where(
                BusinessConnection.connection_id == connection_id
            )
        )

        db_business_connection = result.scalar_one_or_none()
        if db_business_connection is None:
            db_business_connection = BusinessConnection(
                connection_id=connection_id,
                user_chat_id=user_chat_id
            )
            session.add(db_business_connection)
            await session.flush()
        return db_business_connection
    except Exception as e:
        logger.error(f"Error in get_or_save_business_connection: {e}")
        return None


async def get_chats():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Chat).options(selectinload(Chat.business_connection)).order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())


async def get_chat_messages(telegram_chat_id, limit=50):
    async with AsyncSessionLocal() as session:
        chat_result = await session.execute(
            select(Chat).where(Chat.telegram_chat_id == telegram_chat_id)
        )
        chat = chat_result.scalar_one_or_none()
        if chat is None:
            return []

        result = await session.execute(
            select(Message)
            .where(Message.chat_id == chat.id)
            .options(selectinload(Message.user), selectinload(Message.business_connection))
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
