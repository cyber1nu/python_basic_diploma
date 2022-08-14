from typing import List, Dict
from config_data import RAPID_API_KEY
from aiogram import types
import requests
import re
import json
import time


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


def get_id_locations(query: str, locale: str = 'en_US') -> Dict:
    """
    Функция, которая парсит api по url GET запросом
    Возвращает словарь Ключ(id локации): Значение(наименование локации)
    пары ключ-значение дальше используем для создания Иноайн кнопок

    Params:
         query: str  #  Наименование города
         locale: str  #  Локейл
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    current_locations_dict = dict()
    pattern = r'(?:<).*?(?:>)'
    querystring = {"query":f"{query}","locale":f"{locale}","currency":"USD"}
    headers = {
    	"X-RapidAPI-Key": f"{RAPID_API_KEY}",
    	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        request_data = requests.request("GET", url, headers=headers, params=querystring)
        if request_data.status_code == 200:
            result = json.loads(request_data.text)  # получаем словарь
            if len(result['suggestions'][0]['entities']) > 0:
                for i_city in result['suggestions'][0]['entities']:
                    str_val = i_city['caption']
                    n_str = re.sub(pattern, '', str_val)
                    current_locations_dict[i_city['destinationId']] = n_str

                return current_locations_dict
            else:
                with open('errors_log.log', 'a', encoding='UTF-8') as file:
                    file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")} error: Не найдено городов по запросу\n')
        else:
            raise Exception
    except Exception as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")} error:{exc}\n')


# ссылка на отель формируется: url='https://www.hotels.com/ho' + hotl_id: str (example: 260158)

def get_hotels(
        user_id: str,
        city_id: str,
        command: str,
        check_in_date: str,
        check_out_date: str,
        locale: str = 'en_US',
        quantity: str = '5',
        low: str = '0',
        high: str = '1000000',
        from_center_low: str = '0',
        from_center_high: str = '100',) -> Dict:
    """ Функция выдачи отелей по id локации
    Возвращает словарь с парами ключ(цена): список[Название отеля, адрес, удаленность от центра]
    В дальнейшем, при улавливании команды (lowprice или highprice), сортируем по ключам и выдаем n результатов

    Params:
        id: str  # id города, где ищем отели
        n: int  # количество результатов выдачи
        check_in_date: str  # дата заселения
        check_out_date: str  # дата окончания

                    PRICE_HIGHEST_FIRST - в sortOrder - сперва высокие цены
                    DISTANCE_FROM_LANDMARK - sortOrder - сперва удаленность от центра

    """
    if command == '/highprice':
        order = 'PRICE_HIGHEST_FIRST'
    elif command == '/best_deal':
        order = 'DISTANCE_FROM_LANDMARK'
    else:
        order = 'PRICE'

    pattern_to_del = r'\&nbsp;'
    url = "https://hotels4.p.rapidapi.com/properties/list"
    hot_url = 'https://www.hotels.com/ho'
    querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": f"{check_in_date}",
                   "checkOut": f"{check_out_date}", "adults1": "1", "priceMin": f"{low}", "priceMax": f"{high}",
                   "sortOrder": f"{order}", "locale": f"{locale}", "currency": "USD"}
    headers = {
        "X-RapidAPI-Key": f"{RAPID_API_KEY}",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    counter = 0
    all_hotels = dict()
    some_string = ''
    try:
        request_data = requests.request("GET", url, headers=headers, params=querystring)
        if request_data.status_code == 200:
            result = json.loads(request_data.text)  # получаем словарь
            for i_elem in result['data']['body']['searchResults']['results']:
                counter += 1
                all_hotels[i_elem['id']] = [i_elem['name']]  # Имя отеля
                all_hotels[i_elem['id']].append(i_elem['starRating'])  # Рейтинг в звездах
                all_hotels[i_elem['id']].append(i_elem['ratePlan']['price']['current'])  # цена за ночь
                all_hotels[i_elem['id']].append(
                    re.sub(pattern_to_del, ' ', i_elem['ratePlan']['price']['fullyBundledPricePerStay']))  # Цена за период
                for j_elem in i_elem['address'].values():
                    if not isinstance(j_elem, bool):
                        some_string += f'{str(j_elem)}, '
                all_hotels[i_elem['id']].append(some_string)
                some_string = ''
                all_hotels[i_elem['id']].append(i_elem['landmarks'][0]['distance'].split())  # Расстояние до центра (тоже список[расстояние, измерение])
                all_hotels[i_elem['id']].append(hot_url + str(i_elem['id']))  # Ссылка на отель
                all_hotels[i_elem['id']].append(i_elem['id'])
                if counter >= int(quantity):
                    break

            return all_hotels
        else:
            raise Exception
    except Exception as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")}, error got:{exc}\n')


#
# url = "https://hotels4.p.rapidapi.com/properties/list"
# hot_url = 'https://www.hotels.com/ho'
# querystring = {"destinationId": "1506246", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-10-08",
#                    "checkOut": "2022-10-18", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US",
#                    "currency": "USD"}
# headers = {
#         "X-RapidAPI-Key": f"{RAPID_API_KEY}",
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#     }
#
# request_data = requests.request("GET", url, headers=headers, params=querystring)
# result = json.loads(request_data.text)
# all_hotels = dict()
# for i_elem in result['data']['body']['searchResults']['results']:
#     all_hotels[i_elem['ratePlan']['price']['exactCurrent']] = [
#         hot_url + str(i_elem['id']),
#         i_elem['ratePlan']['price']['current'],
#         i_elem['name'],
#         i_elem['starRating'],
#         i_elem['address']['streetAddress'],
#         i_elem['address']['region'],
#         i_elem['address']['countryName'],
#         i_elem['landmarks'][0]['distance'],
#         i_elem['ratePlan']['price']['fullyBundledPricePerStay'],
#     ]
# print(all_hotels)
#

# for i_k, i_v in get_hotels('888',
#                            "1506246",
#                            'lowprice',
#                            "2022-10-08",
#                            "2022-10-18",
#                            locale='en_US',
#                            quantity='5',
#                            low='100',
#                            high='200').items():
#     print(f'цена: {i_k},\t{i_v}')
#


def get_hotels_photo(hotel_id: str, quan_photo: str, some_text: str) -> List:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": f"{hotel_id}"}
    headers = {
        "X-RapidAPI-Key": f"{RAPID_API_KEY}",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    some_list = list()
    counter = 0
    response = requests.request("GET", url, headers=headers, params=querystring)
    try:
        if response.status_code == 200:
            result = json.loads(response.text)
            some_list.append(types.InputMediaPhoto(result['hotelImages'][0]['baseUrl'].replace('{size}', 'b'),
                                                   caption=some_text))
            for i_elem in result['hotelImages'][1::]:
                some_list.append(types.InputMediaPhoto(i_elem['baseUrl'].replace('{size}', 'b')))
                counter += 1
                if counter - 1 >= int(quan_photo):
                    break
        else:
            raise Exception
    except Exception as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")}, error got:{exc}\n')

    return some_list
