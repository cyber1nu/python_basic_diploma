from typing import Dict
from utils.misc.parsing import request_data
from utils.loader import headers
import re
import json
import time


def get_id_locations(query: str, locale: str = 'en_US') -> Dict:
    """
    Функция, которая парсит api по url GET запросом
    Возвращает словарь Ключ(id локации): Значение(наименование локации)
    пары ключ-значение дальше используем для создания Инлайн кнопок

    Params:
         query: str  #  Наименование города
         locale: str  #  Локейл
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    current_locations_dict = dict()
    pattern = r'(?:<).*?(?:>)'
    querystring = {"query": f"{query}", "locale": f"{locale}", "currency": "USD"}
    try:
        data = request_data(url, headers, querystring)
        if data != 'ERROR':
            result = json.loads(data.text)  # получаем словарь
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
            raise UserWarning
    except UserWarning as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")} error:{exc} - ошибка ответа сервера\n')
