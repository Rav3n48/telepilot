import pytest

from db.models import ChatType
from db import queries


@pytest.mark.asyncio
async def test_get_or_save_user_creates_new_user(db_session):
    user = await queries.get_or_save_user(
        db_session, user_id=1, first_name="Ada", last_name="Lovelace",
        username="ada", bio="math", is_bot=False,
    )
    await db_session.commit()

    assert user is not None
    assert user.telegram_id == 1
    assert user.first_name == "Ada"
    assert user.is_bot is False


@pytest.mark.asyncio
async def test_get_or_save_user_reuses_and_updates_existing_user(db_session):
    first = await queries.get_or_save_user(
        db_session, user_id=1, first_name="Ada", last_name="Lovelace", username="ada"
    )
    await db_session.commit()
    first_pk = first.id

    updated = await queries.get_or_save_user(
        db_session, user_id=1, first_name="Ada2", last_name="Byron", username="ada2"
    )
    await db_session.commit()

    assert updated.id == first_pk  # same row, not a new one
    assert updated.first_name == "Ada2"
    assert updated.last_name == "Byron"
    assert updated.username == "ada2"


@pytest.mark.asyncio
async def test_get_or_save_user_returns_none_on_error(db_session, monkeypatch):
    async def boom(*args, **kwargs):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(db_session, "execute", boom)

    result = await queries.get_or_save_user(db_session, user_id=1, first_name="Ada")
    assert result is None


@pytest.mark.asyncio
async def test_get_or_save_chat_creates_new_chat(db_session):
    chat = await queries.get_or_save_chat(
        db_session, chat_id=100, chat_type="private", title="DM"
    )
    await db_session.commit()

    assert chat is not None
    assert chat.telegram_chat_id == 100
    assert chat.type == ChatType.PRIVATE
    assert chat.title == "DM"


@pytest.mark.asyncio
async def test_get_or_save_chat_partial_update_keeps_existing_values(db_session):
    chat = await queries.get_or_save_chat(
        db_session, chat_id=100, chat_type="group", title="Group A",
        description="desc", invite_link="link1",
    )
    await db_session.commit()

    updated = await queries.get_or_save_chat(
        db_session, chat_id=100, chat_type="group", title=None,
        description=None, invite_link=None,
    )
    await db_session.commit()

    assert updated.id == chat.id
    assert updated.title == "Group A"
    assert updated.description == "desc"
    assert updated.invite_link == "link1"


@pytest.mark.asyncio
async def test_get_or_save_chat_distinguishes_business_vs_non_business_same_telegram_id(db_session):
    normal_chat = await queries.get_or_save_chat(
        db_session, chat_id=200, chat_type="private", title="Normal"
    )
    await db_session.commit()

    business_conn = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=200
    )
    await db_session.commit()

    business_chat = await queries.get_or_save_chat(
        db_session, chat_id=200, chat_type="private", title="Business",
        business_connection_id=business_conn.id,
    )
    await db_session.commit()

    assert normal_chat.id != business_chat.id
    assert normal_chat.business_connection_id is None
    assert business_chat.business_connection_id == business_conn.id


@pytest.mark.asyncio
async def test_get_or_save_chat_returns_none_on_error(db_session, monkeypatch):
    async def boom(*args, **kwargs):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(db_session, "execute", boom)

    result = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="X")
    assert result is None


@pytest.mark.asyncio
async def test_save_message_creates_message(db_session):
    chat = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="C")
    user = await queries.get_or_save_user(db_session, user_id=1, first_name="Ada")
    await db_session.commit()

    message = await queries.save_message(
        db_session, message_id=10, chat_id=chat.id, user_id=user.id, text="hello"
    )
    await db_session.commit()

    assert message is not None
    assert message.telegram_message_id == 10
    assert message.text == "hello"
    assert message.sent_by_bot is False


@pytest.mark.asyncio
async def test_save_message_returns_none_on_error(db_session, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(db_session, "add", boom)

    result = await queries.save_message(db_session, message_id=1, chat_id=1, text="x")
    assert result is None


@pytest.mark.asyncio
async def test_save_message_with_reply_link(db_session):
    chat = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="C")
    await db_session.commit()

    parent = await queries.save_message(db_session, message_id=1, chat_id=chat.id, text="parent")
    await db_session.commit()

    child = await queries.save_message(
        db_session, message_id=2, chat_id=chat.id, text="child",
        reply_to_message_id=parent.id,
    )
    await db_session.commit()

    assert child.reply_to_message_id == parent.id


@pytest.mark.asyncio
async def test_get_or_save_business_connection_creates_new(db_session):
    conn = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=42
    )
    await db_session.commit()

    assert conn is not None
    assert conn.connection_id == "biz-1"
    assert conn.user_chat_id == 42


@pytest.mark.asyncio
async def test_get_or_save_business_connection_reuses_existing(db_session):
    first = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=42
    )
    await db_session.commit()

    second = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=999
    )
    await db_session.commit()

    assert second.id == first.id


@pytest.mark.asyncio
async def test_get_or_save_business_connection_returns_none_on_error(db_session, monkeypatch):
    async def boom(*args, **kwargs):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(db_session, "execute", boom)

    result = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=1
    )
    assert result is None


@pytest.mark.asyncio
async def test_save_bot_message_saves_for_existing_non_business_chat(
        db_session, patched_session_local
):
    chat = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="C")
    await db_session.commit()

    ok = await queries.save_bot_message(
        chat_telegram_id=1, telegram_message_id=555, text="bot says hi"
    )

    assert ok is True

    stored = await queries.get_chat_messages(chat.id, limit=10)
    assert len(stored) == 1
    assert stored[0].telegram_message_id == 555
    assert stored[0].sent_by_bot is True


@pytest.mark.asyncio
async def test_save_bot_message_saves_for_existing_business_chat(
        db_session, patched_session_local
):
    business_conn = await queries.get_or_save_business_connection(
        db_session, connection_id="biz-1", user_chat_id=1
    )
    chat = await queries.get_or_save_chat(
        db_session, chat_id=1, chat_type="private", title="C",
        business_connection_id=business_conn.id,
    )
    await db_session.commit()

    ok = await queries.save_bot_message(
        chat_telegram_id=1,
        telegram_message_id=42,
        text="bot biz reply",
        business_connection_id="biz-1",
    )

    assert ok is True
    stored = await queries.get_chat_messages(chat.id, limit=10)
    assert stored[0].business_connection_id == business_conn.id


@pytest.mark.asyncio
async def test_save_bot_message_returns_none_on_unexpected_error(patched_session_local, monkeypatch):
    def boom():
        raise RuntimeError("session factory exploded")

    monkeypatch.setattr(queries, "AsyncSessionLocal", boom)

    result = await queries.save_bot_message(
        chat_telegram_id=1, telegram_message_id=1, text="hi"
    )
    assert result is None


@pytest.mark.asyncio
async def test_save_bot_message_returns_none_when_chat_not_found(patched_session_local):
    result = await queries.save_bot_message(
        chat_telegram_id=9999, telegram_message_id=1, text="hi"
    )
    assert result is None


@pytest.mark.asyncio
async def test_save_bot_message_returns_none_when_business_connection_not_found(
        db_session, patched_session_local
):
    await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="C")
    await db_session.commit()

    result = await queries.save_bot_message(
        chat_telegram_id=1,
        telegram_message_id=1,
        text="hi",
        business_connection_id="nonexistent-biz",
    )
    assert result is None


@pytest.mark.asyncio
async def test_save_bot_message_links_reply_to_existing_message(
        db_session, patched_session_local
):
    chat = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="C")
    parent = await queries.save_message(db_session, message_id=100, chat_id=chat.id, text="orig")
    await db_session.commit()

    ok = await queries.save_bot_message(
        chat_telegram_id=1,
        telegram_message_id=200,
        text="a reply",
        reply_to_telegram_message_id=100,
    )
    assert ok is True

    messages = await queries.get_chat_messages(chat.id, limit=10)
    reply = next(m for m in messages if m.telegram_message_id == 200)
    assert reply.reply_to_message_id == parent.id


@pytest.mark.asyncio
async def test_get_chats_returns_all_chats(db_session, patched_session_local):
    await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="A")
    await queries.get_or_save_chat(db_session, chat_id=2, chat_type="group", title="B")
    await db_session.commit()

    chats = await queries.get_chats()

    assert {c.telegram_chat_id for c in chats} == {1, 2}


@pytest.mark.asyncio
async def test_get_chat_messages_returns_ascending_order_and_respects_limit(
        db_session, patched_session_local
):
    from datetime import datetime, timedelta

    chat = await queries.get_or_save_chat(db_session, chat_id=1, chat_type="private", title="A")
    base_time = datetime(2024, 1, 1)
    for i in range(5):
        msg = await queries.save_message(db_session, message_id=i, chat_id=chat.id, text=f"msg{i}")
        msg.created_at = base_time + timedelta(seconds=i)
    await db_session.commit()

    messages = await queries.get_chat_messages(chat.id, limit=3)

    assert len(messages) == 3
    ids = [m.telegram_message_id for m in messages]
    assert ids == [2, 3, 4]
