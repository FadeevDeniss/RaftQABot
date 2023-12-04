import asyncio

import numpy as np
import pandas as pd
import tiktoken
from openai.embeddings_utils import distances_from_embeddings

from api.openai_helper import OpenAIHelper
from api.telegram_api import TelegramAPI


class Consumer:
    def __init__(self, queue: asyncio.Queue, token: str, consumers_count: int = 1):
        self.task_queue = queue
        self.openai = OpenAIHelper()
        self._tasks = []
        self.consumers_count = consumers_count
        self.telegram_client = TelegramAPI(token)
        self.dataframe = None

    async def create_context(
            self, question, df, max_len=5000, size="ada"
    ):
        q_embeddings = self.openai.client.embeddings.create(
            input=question, model='text-embedding-ada-002'
        ).data[0].embedding

        df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')
        tokenizer = tiktoken.get_encoding("cl100k_base")
        df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

        returns = []
        cur_len = 0

        for i, row in df.sort_values('distances', ascending=True).iterrows():

            cur_len += row['n_tokens'] + 4

            if cur_len > max_len:
                break

            returns.append(row["text"])

        return "\n\n###\n\n".join(returns)

    async def answer_question(
            self,
            question,
            model="gpt-3.5-turbo",
            max_len=4000,
            size="ada",
            debug=False,
            max_tokens=150,
            stop_sequence=None
    ):
        """
        Answer a question based on the most similar context from the dataframe texts
        """

        df = pd.read_csv('text/embeddings.csv', index_col=0)
        df['embeddings'] = df.embeddings.apply(eval).apply(np.array)

        context = await self.create_context(
            question,
            df,
            max_len=max_len,
            size=size,
        )
        # If debug, print the raw model response
        if debug:
            print("Context:\n" + context)
            print("\n\n")

        try:
            # Create a chat completion using the question and context
            response = self.openai.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\n"},
                    {"role": "user", f"content": f"Context: {context}\n\n---\n\nQuestion: {question}\nAnswer:"}
                ],
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
            )
            return response.choices[0].message
        except Exception as e:
            print(e)
            return ""

    async def process_update(self, update):
        """Process telegram update"""

        chat_id = update['message']['chat']['id']
        message = update['message']['text']
        msg_entities = update['message'].get('entities', [])

        command = [en for en in msg_entities if en['type'] == 'bot_command']

        if command:
            if message == '/help':
                message = 'Available commands:\n'
            elif message == '/start':
                message = (f"Hello {update['message']['chat']['first_name']}, "
                           f"i'm QA bot, that provides a"
                           f" connection to ChatGPT 3.0. It's already have a"
                           f" learning base about OpenAI resource https://www.promptingguide.ai/ru"
                           f" loaded in it, and you can"
                           f" send your questions to me, i'm provide you an answer!")
            elif message.startswith('/ask'):
                question = message.split(' ', maxsplit=1)[1]
                await self.answer_question(question)

        await self.telegram_client.send_message(chat_id, message)

    async def consume(self):
        while True:
            update = await self.task_queue.get()
            try:
                await self.process_update(update)
            except Exception as e:
                raise e
            finally:
                self.task_queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self.consume())
                       for _ in range(self.consumers_count)]

    async def stop(self):
        await self.task_queue.join()
        for task in self._tasks:
            task.cancel()
