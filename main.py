from utils import loader
from aiogram import executor


if __name__ == '__main__':
    executor.start_polling(loader.dp, skip_updates=True)


