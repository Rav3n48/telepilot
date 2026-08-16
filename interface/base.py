from abc import ABC, abstractmethod

from telegram.ext import Application


class Interface(ABC):

    @abstractmethod
    async def run(self, application: Application):
        pass
