from keyboards.reply import simple_keyboard
from keyboards.inline import inline_keyboard
from aiogram import Bot, Dispatcher, types
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import Text
from config_data import config
from utils.misc.parsing import *
from typing import Any


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message) -> None:
    # Стартовая команда, добавляем нового пользователя (если новый) в хранилище (словарь) класса UserProfile
    new_user = UserProfile(message.chat.id, '0', 'start')
    await message.delete()
    await message.answer('Привет! Я бот по поиску отелей.'
                         '\n\nДоступные команды для начала работы:\n'
                         '/start - Команда приветствия\n'
                         '/lowprice - поиск отелей в указанном городе (сортировка от низкой цены)\n'
                         '/highprice - поиск отелей в указанном городе (сортировка от высокой цены)\n'
                         '/bestdeal - поиск отелей в заданном диапазоне цен, с заданным расстоянием от центра города\n'
                         '/history - показать историю (команда, дата/время, результаты поиска)\n'
                         '\nУдачи!',
                         reply_markup=simple_keyboard.set_keyboard())


@dp.message_handler(commands=['user'])
async def command_start(message: types.Message) -> None:
    # скрытая команда для получения всех текущих пользователей и их состояний
    await message.answer('вот юзеры из базы:\n')
    for user in UserProfile.all_users:
        await message.answer(f'Юзер №: {str(user)},\tЕго статусы: {str(UserProfile.all_users[user])}')


@dp.message_handler(commands=['cancel'])
async def command_start(message: types.Message) -> None:
    await message.answer('Вы вышли из режима поиска.')
    UserProfile.all_users[message.from_user.id].set_status('0', '/start')


@dp.callback_query_handler(Text('/cancel'))
async def command_cancel(callback: types.CallbackQuery) -> None:
    # если поймали callback == '/cancel' - то сбрасываем статус сценария на "0"
    # полностью выходим из режима диалога (поиска отеля)
    await callback.message.delete()
    await callback.answer('Вы вышли из режима поиска', show_alert=True)
    UserProfile.all_users[callback.from_user.id].set_status('0', callback.data)


@dp.callback_query_handler(Text('delete'))
async def command_cancel(callback: types.CallbackQuery) -> None:
    # если поймали callback == 'DELETE' - то удаляем сообщение (отель не понравился)
    await callback.message.delete()


@dp.callback_query_handler(Text(startswith='photo_'))
async def get_callback_from_keyboard(callback: CallbackQuery) -> Any:
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.actual_photo = callback.data[6::]
    await bot.send_message(callback.from_user.id, 'Тогда подбираю отели. Готовы?\n(введите любой текст)',
                           reply_markup=simple_keyboard.show_result_keyboard())
    cur_user.status[0] = '7'
    if callback.data[6::] == 'yes':
        await bot.send_message(callback.from_user.id, 'Сколько фотографий понадобится?',
                               reply_markup=inline_keyboard.set_photo_quantity_keyboard())
        cur_user.status[0] = '6'


@dp.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
async def command_start(message: types.Message) -> None:
    # Ловим команды начала сценария (старт поиска) lowprice, highprice, bestdeal
    # Устанавливаем состояние пользователю - '1'
    await message.answer('Введите название города, где ищем отель.\n'
                         '(небольшая сноска: в странах СНГ почему-то не ищет)')
    UserProfile.all_users[message.from_user.id].set_status('1', message.text)


@dp.message_handler(content_types=['text'])
async def command_start(message: types.Message) -> None:
    # если нет состояния диалога и не нажата кнопка /start - всё равно добавляем инстанс пользователя в базу
    if message.from_user.id not in UserProfile.all_users:
        await message.answer('Попробуйте команду /start\n:)')
        new_user = UserProfile(message.chat.id, '0', 'start')
    cur_user = UserProfile.all_users[message.from_user.id]
    # Принимаем входящий текст и сохраняем в параметрах класса (параметры см. в parsing.py -> class UserProfile)
    # В зависимости от состояния пользователя идем далее по сценарию сбора данных для поиска
    code_step = cur_user.get_status()[0]
    status_command = cur_user.get_status()[1]
    if code_step == '1':
        # передаем название города в функцию поиска локаций
        # возвращаем инлайн клавиатуру с похожими названиями
        await message.delete()
        locale = 'en_US'
        for i_letter in message.text.lower():
            if i_letter.lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                locale = 'ru_RU'
                break
        cities_to_keyboard = get_id_locations(message.text.lower(), locale=locale)
        if cities_to_keyboard is not None and len(cities_to_keyboard) > 0:
            # если функция вернула не пустой словарь
            kb = inline_keyboard.cities_keyboard(cities_to_keyboard)
            await message.answer('Выберите из списка городов:', reply_markup=kb)
        else:
            await message.answer('Похоже, таких городов не нашлось, совет:\nПопробуйте ещё разок.')
    elif code_step == '2':
        await message.delete()
        # статус, полученный после отлавливания callback'a
        # переводим состояние пользователя в следующее
        if message.text.isdigit():
            cur_user.cities_quantity = message.text
            cur_user.status[0] = '3'
            await message.answer('теперь выберите, пожалуйста, дату.\n',
                                 reply_markup=inline_keyboard.year_calendar_keyboard())
        else:
            # если пользователь ввел не цифру на вопрос о количестве отелей
            await message.answer('что-то пошло не так...кажется это не цифры. ещё разок? :)')
            cur_user.status[0] = '2'
    # далее идем циклом по значениям собранного словаря и выводим форматированную инфу о найденных отелях
    elif code_step == '7':
        # при статусе режима диалога пользователя равном '7' и если он ввёл для поиска НЕ команду bestdeal, то
        # запускаем парсинг API Hotels с собранными параметрами
        await message.delete()
        if status_command != '/bestdeal':
            await message.answer('Вот и всё. Подбираю отели по Вашему запросу...')
            total_result = get_hotels(
                message.from_user.id,
                cur_user.city_id,
                cur_user.status[1],
                cur_user.arr_date,
                cur_user.dep_date,
                locale='en_US',
                quantity=cur_user.cities_quantity,
                low=cur_user.low,
                high=cur_user.high,
                from_center_low=cur_user.from_center_low,
                from_center_high=cur_user.from_center_high,)
            if total_result is not None and len(total_result) > 0:
                for i_elem in total_result.values():
                    text_answer = f'Сам отель: {i_elem[0]}\n' \
                                  f'Цена за ночь: {i_elem[2]}\n' \
                                  f'Кол-во звезд: {int(i_elem[1])*"*"}\n' \
                                  f'Адрес: {i_elem[4][:-6:]}\n' \
                                  f'Расстояние до центра: {round(float(i_elem[5][0])/1.609, 1)}, километра(ов)\n' \
                                  f'Итоговая стоимость за период: {i_elem[3]}\n'
                    if cur_user.actual_photo == 'yes':
                        await bot.send_media_group(
                                            message.from_user.id,
                                            get_hotels_photo(i_elem[7], cur_user.photo_quantity, text_answer))
                        await bot.send_message(message.from_user.id, "Оставить или удалить",
                                               reply_markup=inline_keyboard.hotel_url(i_elem[0], i_elem[6]))
                    else:
                        await message.answer(text_answer, reply_markup=inline_keyboard.hotel_url(i_elem[0], i_elem[6]))
                    cur_user.status[0], cur_user.status[1] = '0', '/start'
            else:
                await message.answer('Простите, кажется ничего не нашлось.\n'
                                     'Выйдите из поиска командой /cancel и попробуйте снова')
        else:
            await message.answer('Почти всё. Осталось выбрать минимальную цену за ночь:')
            cur_user.status[0] = '8'
    elif code_step == '8':
        # Первый пункт режима установки min и max цены за ночь
        await message.delete()
        if message.text.isdigit():
            cur_user.low = message.text
            cur_user.status[0] = '9'
            await message.answer('И максимальную цену за ночь:')
        else:
            await message.answer('что-то пошло не так...кажется это не цифры. ещё разок? :)')
            cur_user.status[0] = '8'
    elif code_step == '9':
        await message.delete()
        # Второй пункт режима установки min и max цены за ночь (по завершению устанавливаем режим состояния '7'
        # и сбрасываем команду, чтобы сработал вызов функции при статусе '7'
        if message.text.isdigit():
            # если цена low больше, чем high - меняем местами
            if int(cur_user.low) < int(message.text):
                cur_user.high = message.text
            else:
                await bot.send_message(message.from_user.id, 'Похоже, перепутали Мин и Макс цены.\nНичего, я поменяю.')
                cur_user.low, cur_user.high = message.text, cur_user.low
            cur_user.status[0] = '7'
            cur_user.status[1] = '/best_deal'
            await message.answer('Подбираю отели. Готовы?\n', reply_markup=simple_keyboard.show_result_keyboard())
        else:
            await message.answer('что-то пошло не так...кажется это не цифры. ещё разок? :)')
            cur_user.status[0] = '9'


@dp.callback_query_handler()
async def get_callback_from_keyboard(callback: CallbackQuery) -> Any:
    cur_user = UserProfile.all_users[callback.from_user.id]
    # если юзер на этапе выбора название города по инлайн кнопкам
    if cur_user.status[0] == '1':
        # вернувшийся callback сохраняем в параметрах класса (параметры см. в parsing.py class UserProfile)
        # двигаем сценарий сбора данных далее
        await callback.message.delete()
        cur_user.city_id = callback.data
        cur_user.status[0] = '2'
        await bot.send_message(callback.from_user.id, 'Какое количество отелей будем искать?')

    # если юзер на этапе выбора даты заселения по инлайн кнопкам
    elif cur_user.status[0] == '3':
        # ожидаем в callback получить год, запрашиваем месяц въезда
        await callback.message.delete()
        # TODO проверка даты нужна
        await bot.send_message(callback.from_user.id,
                            'А теперь месяц', reply_markup=inline_keyboard.month_calendar_keyboard(int(callback.data)))
        cur_user.temporary_data.append(callback.data)
        cur_user.status[0] = '3.1'

    # если юзер на этапе выбора даты заселения по инлайн кнопкам
    elif cur_user.status[0] == '3.1':
        # ожидаем в callback получить месяц, запрашиваем день въезда
        await callback.message.delete()
        # TODO проверка даты нужна
        cur_user.temporary_data.append(callback.data)
        await bot.send_message(callback.from_user.id,
                               'А теперь день', reply_markup=inline_keyboard.day_calendar_keyboard(
                                            cur_user.temporary_data[1], cur_user.temporary_data[0]))
        cur_user.status[0] = '4'

    # если юзер на этапе выбора даты выезда по инлайн кнопкам
    elif cur_user.status[0] == '4':
        # ожидаем получить в callback день въезда, далее обнуляем список
        # temporary_data и по новой собираем инфу о дате выезда
        await callback.message.delete()
        # TODO проверка даты нужна
        cur_user.temporary_data.append(callback.data)
        cur_user.arr_date = f'{"-".join(cur_user.temporary_data)}'
        cur_user.temporary_data = []
        cur_user.status[0] = '4.1'
        await bot.send_message(callback.from_user.id,
                               'Теперь, пожалуйста, выберите дату окончания пребывания в отеле',
                               reply_markup=inline_keyboard.year_calendar_keyboard())

    # если юзер на этапе выбора даты заселения по инлайн кнопкам
    elif cur_user.status[0] == '4.1':
        # ожидаем в callback получить год, запрашиваем месяц
        await callback.message.delete()
        # TODO проверка даты нужна
        await bot.send_message(callback.from_user.id,
                            'А теперь месяц', reply_markup=inline_keyboard.month_calendar_keyboard(int(callback.data)))
        cur_user.temporary_data.append(callback.data)
        cur_user.status[0] = '4.2'

    # если юзер на этапе выбора даты заселения по инлайн кнопкам
    elif cur_user.status[0] == '4.2':
        # ожидаем в callback получить месяц, запрашиваем день
        await callback.message.delete()
        # TODO проверка даты нужна
        cur_user.temporary_data.append(callback.data)
        await bot.send_message(callback.from_user.id,
                               'А теперь день', reply_markup=inline_keyboard.day_calendar_keyboard(
                                cur_user.temporary_data[1], cur_user.temporary_data[0]))
        cur_user.status[0] = '5'

    elif cur_user.status[0] == '5':
        # ожидаем получить в callback день выезда, далее обнуляем список
        # temporary_data и заполняем графу выезда dep_date
        await callback.message.delete()
        cur_user.temporary_data.append(callback.data)
        cur_user.dep_date = f'{"-".join(cur_user.temporary_data)}'
        cur_user.temporary_data = []
        await bot.send_message(callback.from_user.id, 'Вам понадобятся фото отеля?',
                               reply_markup=inline_keyboard.yes_or_no_keyboard())
        cur_user.status[0] = '6'

    elif cur_user.status[0] == '6':
        # ловим количество фото для вывода
        await callback.message.delete()
        cur_user.photo_quantity = callback.data
        cur_user.status[0] = '7'
        await bot.send_message(callback.from_user.id, 'Подбираю отели. Готовы?\n(Введите любой текст)',
                               reply_markup=simple_keyboard.show_result_keyboard())

