import asyncio
import logging

from aiogram import Dispatcher, Bot
from database.models import async_main

from handlers import users, admins
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Запуск процесса поллинга новых апдейтов
async def main():
    await async_main()
    bot = Bot(token='6892025486:AAGahde6FhgYnBYFsh-ihGkjrZYRb3vRxTE')
    dp = Dispatcher()
    dp.include_routers(admins.router, users.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())