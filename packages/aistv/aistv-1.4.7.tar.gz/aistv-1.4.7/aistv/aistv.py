from .core import STVBot

class aistv:
    def __init__(self, token=None):
        self.bot = STVBot(token)

    def chat(self, message):
        return self.bot.chat(message)

    