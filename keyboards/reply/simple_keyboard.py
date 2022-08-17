from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def set_keyboard() -> ReplyKeyboardMarkup:
    # шаблон создания клавиатуры
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('/start'))

    return keyboard


def cancel_keyboard() -> ReplyKeyboardMarkup:
    # клавиатура отмены
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('/cancel'))

    return keyboard


def show_result_keyboard() -> ReplyKeyboardMarkup:
    # клавиатура для вывода результатов поиска
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Показать отели'))
    keyboard.add(KeyboardButton('/cancel'))

    return keyboard


def show_commands_keyboard() -> ReplyKeyboardMarkup:
    # клавиатура показа всех доступных команд
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.insert(KeyboardButton('/lowprice'))
    keyboard.insert(KeyboardButton('/highprice'))
    keyboard.insert(KeyboardButton('/bestdeal'))
    keyboard.add(KeyboardButton('/cancel'))

    return keyboard
