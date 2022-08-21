import logging
from aiogram import Bot, Dispatcher
from config_data import config
from utils.misc.class_FSM import storage
from config_data import RAPID_API_KEY


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='errors_log.log',
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")

headers = {
            "X-RapidAPI-Key": f"{RAPID_API_KEY}",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }
