from utils.loader import *
from aiogram import executor
from handlers import message_handlers, callback_handlers


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


