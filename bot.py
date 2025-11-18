import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.core import create_tables

from handlers import common, game_creation, game_management, game_joining, draw_logic

async def main():
    logging.basicConfig(level=logging.INFO)
    create_tables()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(common.router)
    dp.include_router(game_creation.router)
    dp.include_router(game_joining.router)
    dp.include_router(game_management.router)
    dp.include_router(draw_logic.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass