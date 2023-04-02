
import os
import json
from io import BytesIO

from aiogram import Bot, Dispatcher
from aiogram.types import InputFile


TOKEN = os.environ['TELEGRAM_TOKEN']

CHAT_ID = 'YOUR_CHAT_ID'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def send_message_to_group(string_of_articles):
    data = BytesIO(json.dumps(string_of_articles, indent=4).encode('utf-8'))
    data_file = InputFile(data, filename='articles.json')
    await bot.send_document(chat_id=CHAT_ID, document=data_file)
