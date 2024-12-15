import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.handlers import router
from config import API_TOKEN

from database import Base, engine

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

Base.metadata.create_all(engine)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
