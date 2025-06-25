import os
import sys
import json
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers.user_handlers import user_router
from handlers.admin_handlers import admin_router

load_dotenv()
from database.middleware import DataBaseSession
from database.engine import session_maker

bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.admin_user = json.loads(os.getenv('ADMIN_USER'))

dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(user_router)


async def main() -> None:
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
