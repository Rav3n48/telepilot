# Telepilot

**Terminal client for your Telegram bot.**

Telepilot lets you run a Telegram bot and interact with its conversations directly from your terminal. see incoming messages in real time and reply to them. Every message and chat is also persisted to a local SQLite database, so you keep a full history outside of Telegram itself.

## Features

- **Live message stream** — incoming messages from any chat your bot is in are printed to your terminal as they arrive.
- **Reply from the terminal** — send messages or replies to any chat without touching your phone.
- **Persistent history** — users, chats, and messages are stored in SQLite via SQLAlchemy, so nothing is lost when the bot restarts.

## Requirements

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Installation

```bash
git clone https://github.com/Rav3n48/telepilot.git
cd telepilot
pip install -r requirements.txt
```

## Setup

Copy the example environment file and fill in your bot token:

```bash
cp example.env .env
```

```dotenv
# .env
BOT_TOKEN="your-telegram-bot-token"
PROXY_URL="http://your-proxy-url" # optional, only needed if you access Telegram through a proxy
```

## Usage

Start the bot:

```bash
python main.py
```

This launches Telepilot with the default interface and begins polling for updates. On first run, it also creates a local `db.sqlite3` file to store users, chats, and messages.

### Commands

Once running, use these commands from the terminal:

| Command                                   | Description                           |
|-------------------------------------------|---------------------------------------|
| `/send <chat_id> <message>`               | Send a message to a chat              |
| `/reply <chat_id> <message_id> <message>` | Reply to a specific message in a chat |
| `/quit` or `/exit`                        | Stop the bot and exit                 |

Incoming messages are printed automatically as `[Chat <chat_id>] [Message <message_id>] <name>: <text>` — use the `chat_id` and `message_id` shown there with `/send` and `/reply`.

## License

See [LICENSE](LICENSE).