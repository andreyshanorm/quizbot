import asyncio
import logging
from aiogram import Bot
from db import create_table
import aiosqlite
from utils import dp
from db import DB_NAME

bot = Bot(token='7853455499:AAEe2DbZJpuEd8KKoBFMITW1TnXB23c4yS0')
dp.bot = bot

async def main():
    async with aiosqlite.connect(DB_NAME) as db:
        await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')