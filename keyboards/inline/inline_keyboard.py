from typing import Any, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import emoji


def inline_button(text: str, callback_data: Any) -> InlineKeyboardButton:
    # макет создания кнопки
    the_button = InlineKeyboardButton(text=text, callback_data=callback_data)

    return the_button


def inline_button_2(text: str, url: str) -> InlineKeyboardButton:
    # макет создания кнопки-ссылки
    the_button = InlineKeyboardButton(text=text, url=url)

    return the_button


def cancel_button() -> InlineKeyboardButton:
    # кнопка отмены поиска
    cncl_btn = InlineKeyboardButton(text=emoji.emojize('Выйти из режима поиска :red_circle:'), callback_data='/cancel')

    return cncl_btn


def cities_keyboard(cities_dict: Dict) -> InlineKeyboardMarkup:
    # макет создания клавиатуры с названиями городов на основании макета создания кнопки
    kb = InlineKeyboardMarkup(row_width=1)
    for i_id, i_name in cities_dict.items():
        kb.insert(button=inline_button(text=i_name, callback_data=i_id))
    kb.add(cancel_button())
    return kb


def year_calendar_keyboard() -> InlineKeyboardMarkup:
    # клавиатура выбора года
    kb = InlineKeyboardMarkup(row_width=3)
    cur_year = time.strftime('%Y-%m-%d').split('-')
    for i_year in range(int(cur_year[0]), int(cur_year[0]) + 3):
        kb.insert(inline_button(f'{i_year}', callback_data=f'{str(i_year)}'))

    kb.add(cancel_button())
    return kb


def month_calendar_keyboard(cur_year: str) -> InlineKeyboardMarkup:
    # клавиатура выбора месяца
    months = {
        'Январь': '01', 'Февраль': '02', 'Март': '03', 'Апрель': '04',
        'Май': '05', 'Июнь': '06', 'Июль': '07', 'Август': '08',
        'Сентябрь': '09', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12',
        }
    kb = InlineKeyboardMarkup(row_width=4)
    if int(cur_year) > int(time.strftime('%Y-%m-%d').split('-')[0]):
        for i_month, i_value in months.items():
            kb.insert(inline_button(f'{i_month}', callback_data=f'{i_value}'))
    else:
        for i_month, i_value in months.items():
            if int(i_value) >= int(time.strftime('%Y-%m-%d').split('-')[1]):
                kb.insert(inline_button(f'{i_month}', callback_data=f'{i_value}'))
    kb.add(cancel_button())
    return kb


def day_calendar_keyboard(month: str, year: str) -> InlineKeyboardMarkup:
    # клавиатура выбора дня
    months_31 = ['01', '03', '05', '07', '08', '10', '12']
    months_30 = ['04', '06', '09', '11']

    kb = InlineKeyboardMarkup(row_width=7)
    if month in months_31:
        for i_day in range(1, 32):
            if i_day < 10:
                day = f'0{i_day}'
            else:
                day = i_day
            kb.insert(inline_button(f'{i_day}', callback_data=f'{day}'))
    elif month in months_30:
        for i_day in range(1, 31):
            if i_day < 10:
                day = f'0{i_day}'
            else:
                day = i_day
            kb.insert(inline_button(f'{i_day}', callback_data=f'{day}'))
    elif month == '02' and (int(year) % 4 == 0 and int(year) % 100 != 0 or int(year) % 400 == 0):
        for i_day in range(1, 30):
            if i_day < 10:
                day = f'0{i_day}'
            else:
                day = i_day
            kb.insert(inline_button(f'{i_day}', callback_data=f'{day}'))
    elif month == '02':
        for i_day in range(1, 29):
            if i_day < 10:
                day = f'0{i_day}'
            else:
                day = i_day
            kb.insert(inline_button(f'{i_day}', callback_data=f'{day}'))

    kb.add(cancel_button())
    return kb


def yes_or_no_keyboard() -> InlineKeyboardMarkup:
    # клавиатура "да" или "нет"
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(inline_button(text='Да', callback_data='photo_yes'), inline_button(text='Нет', callback_data='photo_no'))

    return kb


def set_photo_quantity_keyboard() -> InlineKeyboardMarkup:
    # клавиатура выбор количества фото - от 1 до 10
    kb = InlineKeyboardMarkup(row_width=5)
    for i_num in range(1, 11):
        kb.insert(inline_button(str(i_num), callback_data=f'{i_num}'))
    kb.add(cancel_button())

    return kb


def hotel_url(name: str, url: str, message: str = 'None', user_data: str = '') -> InlineKeyboardMarkup:
    # клавиатура с ссылкой на отель, а также для удаления текущего сообщения
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(inline_button_2(text=name, url=url))
    kb.add(inline_button(text=emoji.emojize('Добавить в :star:'), callback_data=f'OK+{user_data}'))
    kb.insert(inline_button(text=emoji.emojize('Скрыть отель :pile_of_poo:'), callback_data=f'delete-{message}'))

    return kb


def show_result() -> InlineKeyboardMarkup:
    # клавиатура для вывода результатов поиска
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(inline_button(text=emoji.emojize('Показать отели :hotel:'), callback_data='1'))

    return kb


def hide_last_message(hotel_name='None') -> InlineKeyboardMarkup:
    #
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(inline_button(text=emoji.emojize('Скрыть это сообщение :yawning_face:'), callback_data='hide'))
    if hotel_name != 'None':
        kb.add(inline_button(text=emoji.emojize('Удалить из избранного :pile_of_poo:'),
                             callback_data=f'hide_favorites+{hotel_name}'))
    return kb


def pag_calendar(cur_date: str) -> InlineKeyboardMarkup:
    real_date = time.strftime('%Y-%m-%d')  # 2022-08-23
    year = cur_date.split('-')[0]
    month = cur_date.split('-')[1]
    day = cur_date.split('-')[2]
    day_31 = {
        '01': 'Январь', '03': 'Март', '05': 'Май', '07': 'Июль',
        '08': 'Август', '10': 'Октябрь', '12': 'Декабрь',
            }
    day_30 = {'04': 'Апрель', '06': 'Июнь', '09': 'Сентябрь', '11': 'Ноябрь',}
    kb = InlineKeyboardMarkup(row_width=7)
    if month in day_31:
        data_year = year
        day_amount = 32
        data_month = day_31[month]
    elif month in day_30:
        data_year = year
        day_amount = 31
        data_month = day_30[month]
    elif month == '02':
        data_year = year
        data_month = 'Февраль'
        if int(year) % 4 == 0 and int(year) % 100 != 0 or int(year) % 400 == 0:
            day_amount = 30
        else:
            day_amount = 29
    else:  # Предположительно, никогда не сработает
        data_year = year
        day_amount = 31
        data_month = 'Январь'

    for i_day in range(1, day_amount):
        if i_day < 10:
            i_day = f'0{i_day}'
        if year == real_date[:4:] and month == real_date[5:7:] and int(i_day) <= int(real_date[8::]):
            kb.insert(InlineKeyboardButton(text=str(i_day), callback_data=f'nothing'))
        else:
            kb.insert(InlineKeyboardButton(text=str(i_day), callback_data=f'{data_year}-{month}-{i_day}'))
    prev_data = f'prev-{year}-{month}-{day}'
    if int(year) < int(real_date.split('-')[0]):
        prev_data = 'nothing'
    elif int(year) == int(real_date.split('-')[0]) and int(month) == int(real_date.split('-')[1]):
        prev_data = 'nothing'
    next_data = f'next-{year}-{month}-{day}'

    kb.add(InlineKeyboardButton(text='<<', callback_data=prev_data))
    kb.insert(InlineKeyboardButton(text=f'{data_month}, {data_year}', callback_data='nothing'))
    kb.insert(InlineKeyboardButton(text='>>', callback_data=next_data))

    return kb