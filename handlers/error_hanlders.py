from utils.loader import dp
from aiogram.types import Update
import time


@dp.errors_handler()
async def errors_log(update: Update, exception: Exception) -> None:
    async with open('errors_log.log', 'a', encoding='UTF-8') as file:
        file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")} error: {exception} при действии: {update}\n')
