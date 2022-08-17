# from aiogram.utils.text_decorations import
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()


class UserStates(StatesGroup):
    """
    Состояния диалога

        city_name: запрос названия города
        city_id: запрос id локации
        hotels_quantity: запрос количества отелей для поиска и вывода
        arr_date_year: запрос даты заселения (ГОД)
        arr_date_month: запрос даты заселения (МЕСЯЦ)
        arr_date_day: запрос даты заселения (ДЕНЬ)
        dep_date_year: запрос даты отъезда (ГОД)
        dep_date_month: запрос даты отъезда (МЕСЯЦ)
        dep_date_day: запрос даты отъезда (ДЕНЬ)
        photo_actual: запрос выводить ли фото
        photo_quantity: запрос о количестве фото для вывода
        min_night_price: запрос минимальной цены за ночь
        max_night_price: запрос максимальной цены за ночь
        show_results: состояние, при котром выводим результаты
    """
    city_name = State()
    city_id = State()
    hotels_quantity = State()
    arr_date_year = State()
    arr_date_month = State()
    arr_date_day = State()
    dep_date_year = State()
    dep_date_month = State()
    dep_date_day = State()
    photo_actual = State()
    photo_quantity = State()
    min_night_price = State()
    max_night_price = State()
    show_results = State()
