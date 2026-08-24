import asyncio
import readline  # noqa: importing this patches input() with arrow-key and history support

from telegram.ext import Application

from core.events import message_queue
from .base import Interface
from db.queries import get_chats, get_chat_messages


class CLIInterface(Interface):
    def __init__(self):
        self._display_task: asyncio.Task | None = None

    async def display_db_messages(self):
        chats = await get_chats()
        for chat in chats:
            if chat.business_connection_id:
                messages = await get_chat_messages(chat.telegram_chat_id, limit=10)
                for message in messages:
                    print(f"\n[Chat {chat.telegram_chat_id}] [Message {message.telegram_message_id}] [Business {chat.business_connection.connection_id}] {message.user.full_name}: {message.text}")
            else:
                messages = await get_chat_messages(chat.telegram_chat_id, limit=10)
                for message in messages:
                    print(f"\n[Chat {chat.telegram_chat_id}] [Message {message.telegram_message_id}] {message.user.full_name}: {message.text}")

    async def _display_messages(self):
        while True:
            name, chat_id, message_id, business_id, text = await message_queue.get()
            if not business_id:
                print(f"\n[Chat {chat_id}] [Message {message_id}] {name}: {text}")
            else:
                print(f"\n[Chat {chat_id}] [Message {message_id}] [Business {business_id}] {name}: {text}")
            print("> ", end="", flush=True)

    async def _send_command(self, application: Application, line):
        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            print("Usage: /send <chat_id> <message>")
            return
        _, chat_id_str, text = parts
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            print("Chat ID must be a number.")
            return
        try:
            await application.bot.send_message(chat_id=chat_id, text=text)
            print("Sent.")
        except Exception as e:
            print(f"Failed to send: {e}")

    async def _reply_command(self, application: Application, line):
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            print("Usage: /reply <chat_id> <message_id> <message>")
            return
        _, chat_id_str, message_id_str, text = parts
        try:
            chat_id = int(chat_id_str)
            message_id = int(message_id_str)
        except ValueError:
            print("Chat ID and Message ID must be a number.")
            return
        try:
            await application.bot.send_message(
                chat_id=chat_id, reply_to_message_id=message_id, text=text
            )
            print("Sent.")
        except Exception as e:
            print(f"Failed to send: {e}")

    async def _send_b_command(self, application: Application, line):
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            print("Usage: /send_b <chat_id> <business_id> <message>")
            return
        _, chat_id_str, business_id, text = parts
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            print("Chat ID must be a number.")
            return
        try:
            await application.bot.send_message(
                chat_id=chat_id, business_connection_id=business_id, text=text
            )
            print("Sent.")
        except Exception as e:
            print(f"Failed to send: {e}")

    async def _reply_b_command(self, application: Application, line):
        parts = line.split(maxsplit=4)
        if len(parts) < 5:
            print("Usage: /reply_b <chat_id> <message_id> <business_id> <message>")
            return
        _, chat_id_str, message_id_str, business_id, text = parts
        try:
            chat_id = int(chat_id_str)
            message_id = int(message_id_str)
        except ValueError:
            print("Chat ID and Message ID must be a number.")
            return
        try:
            await application.bot.send_message(
                chat_id=chat_id, reply_to_message_id=message_id, business_connection_id=business_id, text=text
            )
            print("Sent.")
        except Exception as e:
            print(f"Failed to send: {e}")

    async def run(self, application: Application):
        self._display_task = asyncio.create_task(self._display_messages())
        loop = asyncio.get_running_loop()

        print("Type '/send <chat_id> <message>' to send a message.")
        print("Type '/reply <chat_id> <message_id> <message>' to reply a message.")
        print("Type '/send_b <chat_id> <business_id> <message>' to send a business message.")
        print("Type '/reply_b <chat_id> <message_id> <business_id> <message>' to reply a business message.")
        print("Type '/quit' or '/exit' to stop.\n")
        await asyncio.sleep(0.1)
        await self.display_db_messages()

        try:
            while True:
                try:
                    line = await loop.run_in_executor(None, input, "> ")
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("/send "):
                        await self._send_command(application, line)

                    elif line.startswith("/reply "):
                        await self._reply_command(application, line)

                    elif line.startswith("/send_b "):
                        await self._send_b_command(application, line)

                    elif line.startswith("/reply_b "):
                        await self._reply_b_command(application, line)

                    elif line in ("/quit", "/exit"):
                        print("Shutting down console...")
                        break
                    else:
                        print("Unknown command.")

                except (KeyboardInterrupt, EOFError):
                    print("\nInterrupted.")
                    break
                except Exception as e:
                    print(f"Unexpected error: {e}")
        finally:
            self._display_task.cancel()
