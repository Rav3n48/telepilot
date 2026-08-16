import asyncio

from telegram.ext import Application

from config import BOT_TOKEN, PROXY_URL
from db.session import init_db
from handlers import register_handlers


async def main():
    print(f"Starting Telepilot...")
    await init_db()

    application_builder = Application.builder().token(BOT_TOKEN)
    if PROXY_URL:
        application_builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
    application = application_builder.build()
    register_handlers(application)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        print("bot is running...")
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
