from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def set_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('/start'))

    return keyboard


def show_result_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Показать отели'))
    keyboard.add(KeyboardButton('/cancel'))

    return keyboard
