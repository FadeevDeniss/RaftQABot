import asyncio
import os

from api.telegram_api import TelegramAPI


class Producer:

    def __init__(self, token: str, queue: asyncio.Queue):
        self.task_queue = queue
        self.telegram_client = TelegramAPI(token)
        self._tasks = []
        self._task = None

    async def produce(self):
        offset = 0

        while True:
            updates = await self.telegram_client.get_updates(
                offset=offset, timeout=60
            )
            for upd in updates['result']:
                offset = upd['update_id'] + 1
                self.task_queue.put_nowait(upd)

    async def start(self):
        self._task = asyncio.create_task(self.produce())

    async def stop(self):
        self._task.cancel()






