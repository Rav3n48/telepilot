from unittest.mock import AsyncMock, MagicMock

import pytest

import core.actions as actions


def make_bot(sent_return):
    bot = MagicMock()
    bot.send_message = AsyncMock(return_value=sent_return)
    return bot


def make_sent(chat_id=123, message_id=999, text="ok", business_connection_id=None):
    sent = MagicMock()
    sent.chat = MagicMock()
    sent.chat.id = chat_id
    sent.message_id = message_id
    sent.text = text
    sent.business_connection_id = business_connection_id
    return sent


@pytest.mark.asyncio
async def test_send_message_calls_bot_without_business_id(monkeypatch):
    sent = make_sent()
    bot = make_bot(sent)
    save_mock = AsyncMock()
    monkeypatch.setattr(actions, "save_bot_message", save_mock)

    result = await actions.send_message(bot, chat_id=123, text="hi there")

    bot.send_message.assert_awaited_once_with(chat_id=123, text="hi there")
    assert result is sent


@pytest.mark.asyncio
async def test_send_message_includes_business_connection_id_when_given(monkeypatch):
    sent = make_sent(business_connection_id="biz-1")
    bot = make_bot(sent)
    monkeypatch.setattr(actions, "save_bot_message", AsyncMock())

    await actions.send_message(bot, chat_id=123, text="hi", business_connection_id="biz-1")

    bot.send_message.assert_awaited_once_with(
        chat_id=123, text="hi", business_connection_id="biz-1"
    )


@pytest.mark.asyncio
async def test_send_message_persists_sent_message(monkeypatch):
    sent = make_sent(chat_id=555, message_id=42, text="saved text")
    bot = make_bot(sent)
    save_mock = AsyncMock()
    monkeypatch.setattr(actions, "save_bot_message", save_mock)

    await actions.send_message(bot, chat_id=555, text="original text")

    save_mock.assert_awaited_once_with(
        chat_telegram_id=555,
        telegram_message_id=42,
        text="saved text",
        business_connection_id=None,
    )


@pytest.mark.asyncio
async def test_send_message_falls_back_to_input_text_when_sent_has_none(monkeypatch):
    sent = make_sent(text=None)
    sent.text = None
    bot = make_bot(sent)
    save_mock = AsyncMock()
    monkeypatch.setattr(actions, "save_bot_message", save_mock)

    await actions.send_message(bot, chat_id=123, text="fallback text")

    _, kwargs = save_mock.call_args
    assert kwargs["text"] == "fallback text"


@pytest.mark.asyncio
async def test_send_message_persist_failure_is_swallowed_and_message_still_returned(monkeypatch):
    sent = make_sent()
    bot = make_bot(sent)
    monkeypatch.setattr(
        actions, "save_bot_message", AsyncMock(side_effect=RuntimeError("db down"))
    )

    result = await actions.send_message(bot, chat_id=123, text="hi")

    assert result is sent  # exception during persistence must not propagate


@pytest.mark.asyncio
async def test_send_message_skips_persist_when_no_message_id(monkeypatch):
    sent = make_sent()
    sent.message_id = None
    sent.id = None
    bot = make_bot(sent)
    save_mock = AsyncMock()
    monkeypatch.setattr(actions, "save_bot_message", save_mock)

    await actions.send_message(bot, chat_id=123, text="hi")

    save_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_reply_message_calls_bot_with_reply_to_message_id(monkeypatch):
    sent = make_sent()
    bot = make_bot(sent)
    monkeypatch.setattr(actions, "save_bot_message", AsyncMock())

    await actions.reply_message(bot, chat_id=123, message_id=7, text="a reply")

    bot.send_message.assert_awaited_once_with(
        chat_id=123, reply_to_message_id=7, text="a reply"
    )


@pytest.mark.asyncio
async def test_reply_message_persists_with_reply_link(monkeypatch):
    sent = make_sent(chat_id=1, message_id=100, text="reply text")
    bot = make_bot(sent)
    save_mock = AsyncMock()
    monkeypatch.setattr(actions, "save_bot_message", save_mock)

    await actions.reply_message(bot, chat_id=1, message_id=7, text="reply text")

    save_mock.assert_awaited_once_with(
        chat_telegram_id=1,
        telegram_message_id=100,
        text="reply text",
        reply_to_telegram_message_id=7,
        business_connection_id=None,
    )


@pytest.mark.asyncio
async def test_reply_message_business_connection_id_passed_through(monkeypatch):
    sent = make_sent()
    bot = make_bot(sent)
    monkeypatch.setattr(actions, "save_bot_message", AsyncMock())

    await actions.reply_message(
        bot, chat_id=1, message_id=7, text="hi", business_connection_id="biz-9"
    )

    bot.send_message.assert_awaited_once_with(
        chat_id=1,
        reply_to_message_id=7,
        text="hi",
        business_connection_id="biz-9",
    )


@pytest.mark.asyncio
async def test_reply_message_persist_failure_is_swallowed(monkeypatch):
    sent = make_sent()
    bot = make_bot(sent)
    monkeypatch.setattr(
        actions, "save_bot_message", AsyncMock(side_effect=RuntimeError("boom"))
    )

    result = await actions.reply_message(bot, chat_id=1, message_id=7, text="hi")

    assert result is sent
