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
    if title:
        db_chat.title = title
    if description is not None:
        db_chat.description = description
    if invite_link is not None:
        db_chat.invite_link = invite_link


async def get_or_save_chat(session, chat_id, chat_type, title, description=None, invite_link=None, business_connection_id=None):
    try:
        query = select(Chat).where(Chat.telegram_chat_id == chat_id)
        if business_connection_id is None:
            query = query.where(Chat.business_connection_id.is_(None))
        else:
            query = query.where(Chat.business_connection_id == business_connection_id)

        result = await session.execute(query)

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


async def save_bot_message(chat_telegram_id, telegram_message_id, text, reply_to_telegram_message_id=None, business_connection_id=None):
    try:
        async with AsyncSessionLocal() as session:
            business_pk = None
            if business_connection_id:
                result = await session.execute(
                    select(BusinessConnection).where(
                        BusinessConnection.connection_id == business_connection_id
                    )
                )
                db_business = result.scalar_one_or_none()
                if db_business is not None:
                    business_pk = db_business.id

            query = select(Chat).where(Chat.telegram_chat_id == chat_telegram_id)
            if business_pk is None and not business_connection_id:
                query = query.where(Chat.business_connection_id.is_(None))
            elif business_pk is not None:
                query = query.where(Chat.business_connection_id == business_pk)
            else:
                logger.warning(
                    f"save_bot_message: business_connection_id {business_connection_id} not found, skipping save"
                )
                return None

            result = await session.execute(query)
            db_chat = result.scalar_one_or_none()
            if db_chat is None:
                logger.warning(
                    f"save_bot_message: chat {chat_telegram_id} (business {business_connection_id}) not found, skipping save"
                )
                return None

            reply_db_id = None
            if reply_to_telegram_message_id is not None:
                result = await session.execute(
                    select(Message).where(
                        Message.telegram_message_id == reply_to_telegram_message_id,
                        Message.chat_id == db_chat.id,
                    )
                )
                parent = result.scalar_one_or_none()
                if parent is not None:
                    reply_db_id = parent.id

            await save_message(
                session,
                message_id=telegram_message_id,
                chat_id=db_chat.id,
                user_id=None,
                text=text,
                reply_to_message_id=reply_db_id,
                sent_by_bot=True,
                business_connection_id=business_pk,
            )
            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Error in save_bot_message: {e}")
        return None


async def get_chats():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Chat).options(selectinload(Chat.business_connection)).order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())


async def get_chat_messages(chat_id, limit=50):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .where(Message.sent_by_bot == False)
            .options(selectinload(Message.user), selectinload(Message.business_connection))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))
