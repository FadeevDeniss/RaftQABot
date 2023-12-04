import openai
from time import sleep

from openai import OpenAI

import os
import pandas as pd
import tiktoken


class OpenAIHelper:
    max_tokens = 1000

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get('API_KEY')
        )
        self.dataframe = None

    @staticmethod
    def remove_newlines(serie):
        serie = serie.str.replace('\n', ' ')
        serie = serie.str.replace('\\n', ' ')
        serie = serie.str.replace('  ', ' ')
        serie = serie.str.replace('  ', ' ')
        return serie

    def format_text(self):

        texts = []

        for file in os.listdir('text/'):
            with open(f'text/{file}', 'r', encoding="UTF-8") as f:
                text = f.read()

                texts.append(
                    (file[11:-4].replace('-', ' ')
                     .replace('_', ' ')
                     .replace('#update', ''), text)
                )

        df = pd.DataFrame(texts, columns=['fname', 'text'])
        df['text'] = df.fname + ". " + self.remove_newlines(df.text)

        df.to_csv('text/processed.csv')
        df.head()

    def tokenize(self):
        self.tokenizer = tiktoken.get_encoding('cl100k_base')
        df = pd.read_csv('text/processed.csv', index_col=0)
        df.columns = ['title', 'text']

        df['n_tokens'] = df.text.apply(lambda x: len(self.tokenizer.encode(x)))
        return df

    def split_into_many(self, text):
        sentences = text.split('. ')
        n_tokens = [len(self.tokenizer.encode(" " + sentence)) for sentence in sentences]

        chunks = []
        tokens_so_far = 0
        chunk = []

        for sentence, token in zip(sentences, n_tokens):

            if tokens_so_far + token > self.max_tokens:
                chunks.append(". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0

            if token > self.max_tokens:
                continue

            chunk.append(sentence)
            tokens_so_far += token + 1

        return chunks

    def process_dataframe(self, df):
        shortened = []
        for row in df.iterrows():
            if row[1]['text'] is None:
                continue
            if row[1]['n_tokens'] > self.max_tokens:
                shortened += self.split_into_many(row[1]['text'])

            else:
                shortened.append(row[1]['text'])

        df = pd.DataFrame(shortened, columns=['text'])
        df['embeddings'] = df.text.apply(self.create_embeddings)
        df.to_csv('text/embeddings.csv')
        df.head()
        return df

    def create_embeddings(self, row):
        delay = 20
        for _ in range(3):
            try:
                emb = self.client.embeddings.create(
                    input=row, model='text-embedding-ada-002'
                ).data[0].embedding
                break
            except openai.RateLimitError:
                sleep(delay)
        sleep(delay)
        return emb

