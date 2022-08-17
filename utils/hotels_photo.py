from typing import List
from aiogram import types
from utils.misc.parsing import request_data
from utils.loader import headers
import json
import time


def get_hotels_photo(hotel_id: str, quan_photo: str, some_text: str) -> List:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": f"{hotel_id}"}

    some_list = list()
    counter = 1
    try:
        data = request_data(url, headers, querystring)
        if data.status_code == 200:
            result = json.loads(data.text)
            some_list.append(types.InputMediaPhoto(result['hotelImages'][0]['baseUrl'].replace('{size}', 'b'),
                                                   caption=some_text))
            for i_elem in result['hotelImages'][1::]:
                some_list.append(types.InputMediaPhoto(i_elem['baseUrl'].replace('{size}', 'b')))
                counter += 1
                if counter >= int(quan_photo):
                    break
        else:
            raise Exception
    except Exception as exc:
        with open('errors_log.log', 'a', encoding='UTF-8') as file:
            file.write(f'time:{time.strftime("%d %b %Y - %H:%M:%S")}, error got:{exc}\n')

    return some_list
