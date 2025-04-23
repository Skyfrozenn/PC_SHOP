from aiogram import Bot,Dispatcher
import os
import asyncio
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())

from admin.functional import admin_rt
from user.fuctional_user import user_rt
from info_help_comand import info_rt


ALOW=["message", "edited_message","callback_query"]

 
async def go():
    bot = Bot(os.getenv("TOKEN"))  # Создаем экземпляр Bot ЗДЕСЬ
    dp = Dispatcher() # Создаем dispatcher
    dp.include_router(admin_rt)
    dp.include_router(user_rt)
    dp.include_router(info_rt) # Регистрируем роутер ПОСЛЕ создания Bot и Dispatcher

    await dp.start_polling(bot, allowed_updates=ALOW)

 


asyncio.run(go())


