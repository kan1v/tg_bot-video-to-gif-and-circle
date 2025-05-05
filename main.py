# Импортсы связанные с базовыми библиотеками 
import asyncio
import os 

# Импорты связанные с python-dotenv
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

# Импорты связанные с aiogram
from aiogram import Bot, Dispatcher

# Импорты связанные с фалами проекта 
from app.user_private import user_private_router
# Код файла 

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(user_private_router)


async def main():
    # Очистим вебхуки и установим команды бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бот
    await dp.start_polling(bot)


# Запуск бота 
if __name__ == "__main__":
    asyncio.run(main())