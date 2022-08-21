from typing import Dict
from requests import Response
import requests
import time


def request_data(url: str, headers: Dict, querystring: Dict) -> Response:
    """
    Функция запроса к API, возвращает ответ

        :param url: str
        :param headers: Dict
        :param querystring: Dict
        :return: Response
    """
    response_data = requests.request("GET", url, headers=headers, params=querystring)
    if response_data.status_code == 200:
        return response_data
    else:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")} '
                       f'статус код ответ от сервера: {response_data.status_code}\n')
        return 'ERROR'


