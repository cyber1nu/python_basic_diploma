from typing import List


class UserProfile:
    """ Класс Юзер. Хранение состояния диалога, id чата, всех инстансов класса, параметров, собранных из диалога

     params:
        chat_id: str  # айди пользователя
        status: list  # список состояний пользователя ['состояние сценария', 'команда, запустившая сценарий']
        city_id: str  # айди локации, где ищем отели
        cities_quantity: int  # количество результатов для выдачи
        actual_photo: str  # актуальность выдачи фотографий отеля
        arr_date: str  # дата заселения в отель
        dep_date: str  # дата выезда из отеля
        high: int  # максимальная цена за ночь
        low: int  # минимальная цена за ночь
        from_center_low: int  # расстояние от отеля до центра города МИНИМАЛЬНОЕ
        from_center_high: int  # расстояние от отеля до центра города МАКСИМАЛЬНОЕ
     """

    all_users = dict()

    def __init__(self, chat_id: str, condition: str, command: str) -> None:
        self.chat_id = chat_id
        self.status = [condition, command]
        self.city_id = ''
        self.cities_quantity = '5'  # количество отелей
        self.actual_photo = 'no'
        self.photo_quantity = '0'
        self.temporary_data = []
        self.arr_date = ''
        self.dep_date = ''
        self.high = '1000000'  # верхняя планка цены за ночь
        self.low = '0'         # нижняя планка цены за ночь
        self.from_center_low = '0'
        self.from_center_high = '100'
        self.message_to_delete = ''
        if self not in self.all_users:
            self.all_users[self.chat_id] = self
        else:
            self.all_users[self.chat_id] = self

    def __str__(self):
        return f'Юзер чат айди: {self.chat_id}\nстатус диалога: {self.status}'\
                f'Количество отелей: {self.cities_quantity}\n'\
                f'Даты пребывания от {self.arr_date} до {self.dep_date}'

    @property
    def show_all_users(self):
        return self.all_users

    def get_status(self) -> List:
        return [self.status[0], self.status[1]]

    def set_status(self, condition: str, command: str) -> None:
        self.status[0], self.status[1] = condition, command
