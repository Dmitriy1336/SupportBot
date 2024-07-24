import asyncio
import logging
from aiogram import Dispatcher, Bot
from handlers.chat_gpt import on_startup
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
# Включаем логирование
logging.basicConfig(level=logging.INFO)


async def main():
    print("Инициализация бота...")
    bot = Bot(token=TELEGRAM_API_TOKEN)
    dp = Dispatcher()
    print("Регистрация маршрутизаторов...")
    try:
        from handlers import admins, users, chat_gpt
        dp.include_router(chat_gpt.router)
        dp.include_router(admins.router)
        dp.include_router(users.router)
        print("Маршрутизаторы зарегистрированы успешно.")
    except Exception as e:
        print(f"Ошибка при регистрации маршрутизаторов: {e}")
        return
    # запуск GPT
    await on_startup()
    # Запуск поллинга
    print("Запуск поллинга...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"Ошибка при запуске поллинга: {e}")


if __name__ == "__main__":
    print("Запуск main...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка в __main__: {e}")
