from aiogram import Bot, Dispatcher
from config_data import config
from utils.misc.class_FSM import storage
from config_data import RAPID_API_KEY


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

headers = {
            "X-RapidAPI-Key": f"{RAPID_API_KEY}",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }
