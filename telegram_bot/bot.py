import asyncio

from telegram_bot.consumer import Consumer
from telegram_bot.producer import Producer


class TelegramBot:

    def __init__(self, queue: asyncio.Queue, consumers_count: int, token: str = None):
        self.tasks_queue = queue
        self.producer = Producer(token=token,
                                 queue=self.tasks_queue)
        self.consumer = Consumer(token=token,
                                 consumers_count=consumers_count,
                                 queue=self.tasks_queue)

    # async def prepare(self):
    #     await self.producer.prepare()
    #     await self.consumer.prepare()

    async def start(self):
        await self.producer.start()
        await self.consumer.start()

    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()

