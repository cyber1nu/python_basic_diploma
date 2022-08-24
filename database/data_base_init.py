import sqlite3
import os


path = 'C:\pyCharm projects\python_basic_diploma\favorites_db.db'
# создаем базу данных (файл), если не существует
if os.path.isfile(path):
    favorites_db = sqlite3.connect(path)
else:
    favorites_db = sqlite3.connect(path)
# создаем курсор для оперирования базой данных
new_cursor = favorites_db.cursor()

# через курсор создали базу данных с колонками: ЮЗЕР ИД (ключ) ФНЕЙМ, ЛНЕЙМ, ГЕНДЕР (текстовый формат)
new_cursor.execute("CREATE TABLE IF NOT EXISTS "
                   "'history'(id INT PRIMARY KEY, command TEXT, date TEXT, userid TEXT, "
                   "hotel_name TEXT, url_name TEXT, price TEXT);")

new_cursor.execute("CREATE TABLE IF NOT EXISTS "
                   "'favorites'(id INT PRIMARY KEY, command TEXT, date TEXT, userid TEXT, "
                   "hotel_name TEXT, url_name TEXT, price TEXT);")
favorites_db.commit()
new_cursor.close()
