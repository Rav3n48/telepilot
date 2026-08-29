import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

import interface.cli as cli_module
from interface.cli import CLIInterface


@pytest.fixture
def fake_application():
    app = MagicMock()
    app.bot = MagicMock()
    return app


@pytest.mark.asyncio
async def test_send_command_success(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_command(fake_application, "/send 123 hello world")

    send_mock.assert_awaited_once_with(fake_application.bot, chat_id=123, text="hello world")
    assert "Sent." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_command_missing_args_prints_usage(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_command(fake_application, "/send 123")

    send_mock.assert_not_awaited()
    assert "Usage: /send" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_command_non_numeric_chat_id(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_command(fake_application, "/send abc hello")

    send_mock.assert_not_awaited()
    assert "must be a number" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_command_handles_send_exception(monkeypatch, fake_application, capsys):
    monkeypatch.setattr(
        cli_module, "send_message", AsyncMock(side_effect=RuntimeError("network down"))
    )
    interface = CLIInterface()

    await interface._send_command(fake_application, "/send 123 hello")

    assert "Failed to send: network down" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_command_success(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_command(fake_application, "/reply 123 5 hello there")

    reply_mock.assert_awaited_once_with(
        fake_application.bot, chat_id=123, message_id=5, text="hello there"
    )
    assert "Sent." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_command_missing_args_prints_usage(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_command(fake_application, "/reply 123 5")

    reply_mock.assert_not_awaited()
    assert "Usage: /reply" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_command_non_numeric_ids(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_command(fake_application, "/reply abc def hello")

    reply_mock.assert_not_awaited()
    assert "must be a number" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_b_command_success(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_b_command(fake_application, "/send_b 123 biz-1 hello world")

    send_mock.assert_awaited_once_with(
        fake_application.bot, chat_id=123, text="hello world", business_connection_id="biz-1"
    )
    assert "Sent." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_b_command_missing_args(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_b_command(fake_application, "/send_b 123 biz-1")

    send_mock.assert_not_awaited()
    assert "Usage: /send_b" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_b_command_non_numeric_chat_id(monkeypatch, fake_application, capsys):
    send_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_mock)
    interface = CLIInterface()

    await interface._send_b_command(fake_application, "/send_b abc biz-1 hello")

    send_mock.assert_not_awaited()
    assert "must be a number" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_send_b_command_handles_exception(monkeypatch, fake_application, capsys):
    monkeypatch.setattr(
        cli_module, "send_message", AsyncMock(side_effect=RuntimeError("nope"))
    )
    interface = CLIInterface()

    await interface._send_b_command(fake_application, "/send_b 1 biz-1 hi")

    assert "Failed to send: nope" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_b_command_success(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_b_command(fake_application, "/reply_b 123 5 biz-1 hello there")

    reply_mock.assert_awaited_once_with(
        fake_application.bot,
        chat_id=123,
        message_id=5,
        text="hello there",
        business_connection_id="biz-1",
    )
    assert "Sent." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_b_command_missing_args(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_b_command(fake_application, "/reply_b 123 5 biz-1")

    reply_mock.assert_not_awaited()
    assert "Usage: /reply_b" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_b_command_non_numeric_ids(monkeypatch, fake_application, capsys):
    reply_mock = AsyncMock()
    monkeypatch.setattr(cli_module, "reply_message", reply_mock)
    interface = CLIInterface()

    await interface._reply_b_command(fake_application, "/reply_b abc def biz-1 hi")

    reply_mock.assert_not_awaited()
    assert "must be a number" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_reply_b_command_handles_exception(monkeypatch, fake_application, capsys):
    monkeypatch.setattr(
        cli_module, "reply_message", AsyncMock(side_effect=RuntimeError("nope"))
    )
    interface = CLIInterface()

    await interface._reply_b_command(fake_application, "/reply_b 1 2 biz-1 hi")

    assert "Failed to send: nope" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_display_db_messages_formats_business_and_non_business(monkeypatch, capsys):
    normal_chat = MagicMock(id=1, telegram_chat_id=1, business_connection_id=None)
    business_chat = MagicMock(id=2, telegram_chat_id=2, business_connection_id=5)
    business_chat.business_connection.connection_id = "biz-conn"

    normal_message = MagicMock(telegram_message_id=10, text="hi")
    normal_message.user.full_name = "Alice"
    business_message = MagicMock(telegram_message_id=20, text="yo")
    business_message.user.full_name = "Bob"

    async def fake_get_chats():
        return [normal_chat, business_chat]

    async def fake_get_chat_messages(chat_id, limit=10):
        return [normal_message] if chat_id == 1 else [business_message]

    monkeypatch.setattr(cli_module, "get_chats", fake_get_chats)
    monkeypatch.setattr(cli_module, "get_chat_messages", fake_get_chat_messages)

    interface = CLIInterface()
    await interface.display_db_messages()

    out = capsys.readouterr().out
    assert "[Chat 1]" in out and "Alice: hi" in out
    assert "[Business biz-conn]" in out and "Bob: yo" in out


@pytest.mark.asyncio
async def test_display_messages_prints_queued_item_then_prompt(monkeypatch, capsys):
    queue = asyncio.Queue()
    monkeypatch.setattr(cli_module, "message_queue", queue)

    await queue.put(("Alice", 1, 10, None, "hi"))

    interface = CLIInterface()
    task = asyncio.create_task(interface._display_messages())
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    out = capsys.readouterr().out
    assert "[Chat 1] [Message 10] Alice: hi" in out
    assert "> " in out


@pytest.mark.asyncio
async def test_display_messages_formats_business_message(monkeypatch, capsys):
    queue = asyncio.Queue()
    monkeypatch.setattr(cli_module, "message_queue", queue)
    await queue.put(("Bob", 2, 20, "biz-9", "yo"))

    interface = CLIInterface()
    task = asyncio.create_task(interface._display_messages())
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    out = capsys.readouterr().out
    assert "[Business biz-9]" in out and "Bob: yo" in out


@pytest.mark.asyncio
async def test_run_dispatches_send_command_and_quits(monkeypatch, fake_application):
    monkeypatch.setattr(
        CLIInterface, "display_db_messages", AsyncMock()
    )
    send_spy = AsyncMock()
    monkeypatch.setattr(cli_module, "send_message", send_spy)

    lines = iter(["/send 1 hello", "/quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))

    interface = CLIInterface()
    await interface.run(fake_application)

    send_spy.assert_awaited_once_with(fake_application.bot, chat_id=1, text="hello")


@pytest.mark.asyncio
async def test_run_prints_unknown_command(monkeypatch, fake_application, capsys):
    monkeypatch.setattr(CLIInterface, "display_db_messages", AsyncMock())

    lines = iter(["/bogus", "/quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))

    interface = CLIInterface()
    await interface.run(fake_application)

    assert "Unknown command." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_run_stops_on_keyboard_interrupt(monkeypatch, fake_application, capsys):
    monkeypatch.setattr(CLIInterface, "display_db_messages", AsyncMock())

    def raise_interrupt(prompt=""):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_interrupt)

    interface = CLIInterface()
    await interface.run(fake_application)

    assert "Interrupted." in capsys.readouterr().out


@pytest.mark.asyncio
async def test_run_cancels_display_task_on_exit(monkeypatch, fake_application):
    monkeypatch.setattr(CLIInterface, "display_db_messages", AsyncMock())
    monkeypatch.setattr("builtins.input", lambda prompt="": "/quit")

    interface = CLIInterface()
    await interface.run(fake_application)

    assert interface._display_task.cancelled() or interface._display_task.done()
