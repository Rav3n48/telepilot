from telegram.ext import Application

from .messages import message_handler


def register_handlers(application: Application):
    application.add_handler(message_handler)
