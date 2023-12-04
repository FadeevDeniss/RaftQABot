import asyncio
import os

from dotenv import load_dotenv

from api.openai_helper import OpenAIHelper
from parser.hyperlink_parser import HyperTextParser
from telegram_bot.bot import TelegramBot


def run():
    load_dotenv()

    parser = HyperTextParser()
    openai_helper = OpenAIHelper()
    parser.get_hyperlinks()
    parser.parse_url()

    openai_helper.format_text()
    df = openai_helper.tokenize()
    openai_helper.process_dataframe(df)

    token = os.getenv('TG_API_KEY')
    tg_bot = TelegramBot(asyncio.Queue(),
                         token=token,
                         consumers_count=3)
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.create_task(tg_bot.start())
        event_loop.run_forever()
    except KeyboardInterrupt:
        event_loop.run_until_complete(tg_bot.stop())


if __name__ == '__main__':
    run()
