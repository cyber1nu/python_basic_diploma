from typing import Dict
from requests import Response
import requests


def request_data(url: str, headers: Dict, querystring: Dict) -> Response:
    """
    Функция запроса к API, возвращает ответ

        :param url: str
        :param headers: Dict
        :param querystring: Dict
        :return: Response
    """
    response_data = requests.request("GET", url, headers=headers, params=querystring)

    return response_data


