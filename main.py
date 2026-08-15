import asyncio

from config import BOT_TOKEN
from db.session import init_db


async def main():
    print(f"Starting Telepilot with token: {BOT_TOKEN[:8]}...")
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
