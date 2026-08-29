import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

import handlers.messages as messages_module
from db.models import Chat, User, Message


def make_update(text="hello", business_connection_id=None, reply_to=None,
                chat_id=1, chat_type="private", chat_title="Some Chat",
                user_id=1, first_name="Ada", last_name="Lovelace",
                username="ada", is_bot=False, message_id=10):
    update = MagicMock()

    message = MagicMock()
    message.text = text
    message.id = message_id
    message.business_connection_id = business_connection_id
    message.reply_to_message = reply_to

    user = MagicMock()
    user.id = user_id
    user.first_name = first_name
    user.last_name = last_name
    user.username = username
    user.is_bot = is_bot
    user.full_name = f"{first_name} {last_name}" if last_name else first_name

    chat = MagicMock()
    chat.id = chat_id
    chat.type = chat_type
    chat.title = chat_title

    update.effective_message = message
    update.effective_user = user
    update.effective_chat = chat
    return update


def make_context(bio=None, description=None, invite_link=None, get_chat_side_effect=None):
    context = MagicMock()
    if get_chat_side_effect is not None:
        context.bot.get_chat = AsyncMock(side_effect=get_chat_side_effect)
    else:
        chat_info = MagicMock(bio=bio, description=description, invite_link=invite_link)
        context.bot.get_chat = AsyncMock(return_value=chat_info)
    return context


@pytest.fixture
def local_queue(monkeypatch):
    queue = asyncio.Queue()
    monkeypatch.setattr(messages_module, "message_queue", queue)
    return queue


@pytest.fixture
def patched_handler_session(session_factory, monkeypatch):
    monkeypatch.setattr(messages_module, "AsyncSessionLocal", session_factory)
    return session_factory


@pytest.mark.asyncio
async def test_returns_early_when_message_is_none(local_queue, patched_handler_session):
    update = make_update()
    update.effective_message = None
    context = make_context()

    await messages_module.handle_messages(update, context)

    assert local_queue.empty()
    context.bot.get_chat.assert_not_awaited()


@pytest.mark.asyncio
async def test_returns_early_when_chat_is_none(local_queue, patched_handler_session):
    update = make_update()
    update.effective_chat = None
    context = make_context()

    await messages_module.handle_messages(update, context)

    assert local_queue.empty()


@pytest.mark.asyncio
async def test_returns_early_when_text_is_none(local_queue, patched_handler_session):
    update = make_update(text=None)
    context = make_context()

    await messages_module.handle_messages(update, context)

    assert local_queue.empty()


@pytest.mark.asyncio
async def test_puts_expected_tuple_on_queue_for_non_business_message(
        local_queue, patched_handler_session
):
    update = make_update(text="hi there", chat_id=42, message_id=7)
    context = make_context()

    await messages_module.handle_messages(update, context)

    item = local_queue.get_nowait()
    assert item == ("Ada Lovelace", 42, 7, None, "hi there")


@pytest.mark.asyncio
async def test_puts_expected_tuple_for_business_message_and_skips_get_chat(
        local_queue, patched_handler_session
):
    update = make_update(text="biz msg", business_connection_id="biz-1")
    context = make_context()

    await messages_module.handle_messages(update, context)

    item = local_queue.get_nowait()
    assert item[3] == "biz-1"
    context.bot.get_chat.assert_not_awaited()


@pytest.mark.asyncio
async def test_uses_unknown_when_no_effective_user(local_queue, patched_handler_session):
    update = make_update()
    update.effective_user = None
    context = make_context()

    with pytest.raises(AttributeError):
        await messages_module.handle_messages(update, context)

    item = local_queue.get_nowait()
    assert item[0] == "Unknown"


@pytest.mark.asyncio
async def test_fetches_chat_metadata_for_non_business_message(
        local_queue, patched_handler_session
):
    update = make_update()
    context = make_context(bio="a bio", description="a description", invite_link="t.me/x")

    await messages_module.handle_messages(update, context)

    context.bot.get_chat.assert_awaited_once_with(chat_id=update.effective_chat.id)

    async with patched_handler_session() as session:
        result = await session.execute(select(Chat).where(Chat.telegram_chat_id == 1))
        db_chat = result.scalar_one()
        assert db_chat.description == "a description"
        assert db_chat.invite_link == "t.me/x"


@pytest.mark.asyncio
async def test_get_chat_failure_is_swallowed(local_queue, patched_handler_session):
    update = make_update()
    context = make_context(get_chat_side_effect=RuntimeError("telegram is down"))

    await messages_module.handle_messages(update, context)

    async with patched_handler_session() as session:
        result = await session.execute(select(Chat).where(Chat.telegram_chat_id == 1))
        db_chat = result.scalar_one()
        assert db_chat.description is None


@pytest.mark.asyncio
async def test_persists_user_chat_and_message(local_queue, patched_handler_session):
    update = make_update(text="hello world", chat_id=5, message_id=99)
    context = make_context()

    await messages_module.handle_messages(update, context)

    async with patched_handler_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == 1))
        db_user = user_result.scalar_one()
        assert db_user.first_name == "Ada"

        chat_result = await session.execute(select(Chat).where(Chat.telegram_chat_id == 5))
        db_chat = chat_result.scalar_one()
        assert db_chat.title == "Some Chat"

        message_result = await session.execute(
            select(Message).where(Message.telegram_message_id == 99)
        )
        db_message = message_result.scalar_one()
        assert db_message.text == "hello world"
        assert db_message.user_id == db_user.id
        assert db_message.chat_id == db_chat.id
        assert db_message.sent_by_bot is False


@pytest.mark.asyncio
async def test_chat_title_falls_back_to_user_full_name_when_missing(
        local_queue, patched_handler_session
):
    update = make_update(chat_title=None, chat_id=6)
    context = make_context()

    await messages_module.handle_messages(update, context)

    async with patched_handler_session() as session:
        result = await session.execute(select(Chat).where(Chat.telegram_chat_id == 6))
        db_chat = result.scalar_one()
        assert db_chat.title == "Ada Lovelace"


@pytest.mark.asyncio
async def test_reply_to_message_id_is_persisted(local_queue, patched_handler_session):
    reply_target = MagicMock(id=123)
    update = make_update(reply_to=reply_target, message_id=200)
    context = make_context()

    await messages_module.handle_messages(update, context)

    async with patched_handler_session() as session:
        result = await session.execute(
            select(Message).where(Message.telegram_message_id == 200)
        )
        db_message = result.scalar_one()
        assert db_message.reply_to_message_id == 123


@pytest.mark.asyncio
async def test_business_message_creates_business_connection_and_links_chat(
        local_queue, patched_handler_session
):
    update = make_update(
        text="biz hello", business_connection_id="biz-conn-1", chat_id=7
    )
    context = make_context()

    await messages_module.handle_messages(update, context)

    context.bot.get_chat.assert_not_awaited()

    async with patched_handler_session() as session:
        from db.models import BusinessConnection

        conn_result = await session.execute(
            select(BusinessConnection).where(BusinessConnection.connection_id == "biz-conn-1")
        )
        db_conn = conn_result.scalar_one()
        assert db_conn.user_chat_id == 7

        chat_result = await session.execute(select(Chat).where(Chat.telegram_chat_id == 7))
        db_chat = chat_result.scalar_one()
        assert db_chat.business_connection_id == db_conn.id


def test_message_handler_is_wired_to_handle_messages():
    from telegram.ext import MessageHandler

    assert isinstance(messages_module.message_handler, MessageHandler)
    assert messages_module.message_handler.callback is messages_module.handle_messages
