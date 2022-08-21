from database.data_base_init import favorites_db


def set_user_history(db_name, some_tuple) -> None:
    """
    Функция, записывающая результаты поиска в базу данных
    привязка по id пользователя
    :param some_tuple: tuple - кортеж из user id, название отеля, ссылка, стоимость
    :param db_name: str - имя базы данных

    """
    new_cursor = favorites_db.cursor()
    new_cursor.execute(f"INSERT INTO '{db_name}'(command, date, userid, hotel_name, url_name, price) "
                       f"VALUES(?, ?, ?, ?, ?, ?);", some_tuple,)

    favorites_db.commit()
    new_cursor.close()


def get_user_history(db_name, some_user_id) -> str:
    """
    Функция-генератор
    Если по запрашиваемому id пользователя есть записи в базе данных,
    генерирует f строки: имя, ссылка, цена

    Если записи нет, возвращаем ответ "NOT OK"

        :param some_user_id: str - айди пользователя в строке
        :param db_name: str - имя базы данных
        :return: str - строку "NOT OK" либо f строку имя, ссылка, цена отеля
    """
    new_cursor = favorites_db.cursor()
    if db_name == 'history':
        new_cursor.execute(f"SELECT command, date, hotel_name, url_name, price FROM '{db_name}' "
                           f"WHERE userid=?;", (some_user_id,))
    else:
        new_cursor.execute(f"SELECT hotel_name, url_name, price FROM '{db_name}' WHERE userid=?;", (some_user_id,))
    result = new_cursor.fetchall()
    favorites_db.commit()
    new_cursor.close()
    string = 'NOT OK'
    if (result is None) or (result == []):
        yield string
    else:
        for i_r in range(len(result)):
            if db_name == 'history':
                string = f'Команда: {result[i_r][0]}\nДата: {result[i_r][1]}\nИмя: {result[i_r][2]}\n' \
                         f'Сайт: {result[i_r][3]}\nЦена :{result[i_r][4]}'
            else:
                string = f'Имя: {result[i_r][0]}\nСайт: {result[i_r][1]}\nЦена :{result[i_r][2]}'
            yield string


def delete_from_history(db_name, some_user_id, some_hotel_name) -> None:
    """
    Функция, удаляющая из базы данных записи по выбору пользователя

        :param db_name: str - имя базы данных
        :param some_user_id: str - айди пользователя
        :param some_hotel_name: str - имя отеля, который надо удалить из бд

    """
    new_cursor = favorites_db.cursor()
    new_cursor.execute(f"DELETE FROM '{db_name}' WHERE userid=? AND hotel_name=?;",
                       (some_user_id, some_hotel_name,))
    favorites_db.commit()
    new_cursor.close()



