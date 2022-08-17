from typing import Dict
from utils.misc.parsing import request_data
from utils.loader import headers
import re
import json
import time


def get_hotels(user_id: str, city_id: str, command: str, check_in_date: str, check_out_date: str, locale: str = 'en_US',
               quantity: str = '5', low: str = '0', high: str = '1000000',) -> Dict:
    """
    Функция выдачи отелей по id локации
    Возвращает словарь с парами
    ключ - id отеля: значение - список[Имя, Рейтинг, Цена, Тотал цена, Адрес, Расстояние до центра, Ссылка]
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
    elif command == '/bestdeal':
        order = 'DISTANCE_FROM_LANDMARK'
    else:
        order = 'PRICE'

    pattern_to_del = r'\&nbsp;'
    url = "https://hotels4.p.rapidapi.com/properties/list"
    hot_url = 'https://www.hotels.com/ho'
    querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": f"{check_in_date}",
                   "checkOut": f"{check_out_date}", "adults1": "1", "priceMin": f"{low}", "priceMax": f"{high}",
                   "sortOrder": f"{order}", "locale": f"{locale}", "currency": "USD"}

    counter = 0
    all_hotels = dict()
    some_string = ''
    try:
        data = request_data(url, headers, querystring)
        if data.status_code == 200:
            result = json.loads(data.text)  # получаем словарь
            for i_elem in result['data']['body']['searchResults']['results']:
                counter += 1
                # Имя отеля
                all_hotels[i_elem['id']] = [i_elem['name']]
                # Рейтинг в звездах
                all_hotels[i_elem['id']].append(i_elem['starRating'])
                # цена за ночь
                all_hotels[i_elem['id']].append(i_elem['ratePlan']['price']['current'])
                # Цена за период, если это значение есть в словаре
                if 'fullyBundledPricePerStay' in i_elem['ratePlan']['price']:
                    all_hotels[i_elem['id']].append(
                        re.sub(pattern_to_del, ' ', i_elem['ratePlan']['price']['fullyBundledPricePerStay']))
                else:
                    all_hotels[i_elem['id']].append('нет расчетной стоимости')
                for j_elem in i_elem['address'].values():
                    if not isinstance(j_elem, bool):
                        some_string += f'{str(j_elem)}, '
                all_hotels[i_elem['id']].append(some_string)
                some_string = ''
                # Расстояние до центра (тоже список[расстояние, измерение])
                all_hotels[i_elem['id']].append(i_elem['landmarks'][0]['distance'].split())
                # Ссылка на отель
                all_hotels[i_elem['id']].append(hot_url + str(i_elem['id']))
                all_hotels[i_elem['id']].append(i_elem['id'])
                if counter >= int(quantity):
                    break

            return all_hotels
        else:
            raise Exception
    except Exception as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")}, error got:{exc}\n')
