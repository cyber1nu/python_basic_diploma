from utils.misc.class_User import UserProfile
from utils.misc.class_FSM import UserStates
from utils import cities_names
from utils.loader import dp, bot
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from keyboards.reply import simple_keyboard
from keyboards.inline import inline_keyboard


@dp.message_handler(commands=['start'])
async def command_start(message: Message) -> None:
    # Стартовая команда, добавляем нового пользователя (если новый) в хранилище (словарь) класса UserProfile
    new_user = UserProfile(message.chat.id, '0', 'start')
    await message.delete()
    await message.answer('Привет! Я бот по поиску отелей.'
                         '\n\nДоступные команды для начала работы:\n'
                         '/start - Команда приветствия\n'
                         '/lowprice - поиск отелей в указанном городе (сортировка от низкой цены)\n'
                         '/highprice - поиск отелей в указанном городе (сортировка от высокой цены)\n'
                         '/bestdeal - поиск отелей в заданном диапазоне цен, с мин-ным расстоянием от центра города\n'
                         '/history - показать историю (команда, дата/время, результаты поиска)\n'
                         '\nУдачи!',
                         reply_markup=simple_keyboard.show_commands_keyboard())


@dp.message_handler(commands=['cancel'], state="*")
async def command_cancel(message: Message, state: FSMContext) -> None:
    # команда отмены поиска
    await message.answer('Вы вышли из режима поиска.', reply_markup=simple_keyboard.show_commands_keyboard())
    UserProfile.all_users[message.from_user.id].set_status('0', '/start')
    if state is None:
        return
    else:
        await state.finish()


@dp.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
async def command_search(message: Message, state: FSMContext) -> None:
    # Ловим команды начала сценария (старт поиска) lowprice, highprice, bestdeal
    # Устанавливаем состояние пользователю - city_name
    UserProfile.all_users[message.from_user.id].message_to_delete = await message.answer(
        'Введите название города, где ищем отель.\n'
        '(небольшая сноска: в странах СНГ почему-то не ищет)')
    UserProfile.all_users[message.from_user.id].set_status('1', message.text)
    await UserStates.city_name.set()
    await message.delete()


@dp.message_handler(state=UserStates.city_name)
async def city_name_set(message: Message, state: FSMContext) -> None:
    # Принимает название города, возвращает клавиатуру со списком названий городов
    cur_user = UserProfile.all_users[message.from_user.id]
    await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
    await message.delete()
    locale = 'en_US'
    for i_letter in message.text.lower():
        if i_letter.lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            locale = 'ru_RU'
            break
    cities_to_keyboard = cities_names.get_id_locations(message.text.lower(), locale=locale)
    if cities_to_keyboard is not None and len(cities_to_keyboard) > 0:
        # если функция вернула не пустой словарь
        kb = inline_keyboard.cities_keyboard(cities_to_keyboard)
        UserProfile.all_users[message.from_user.id].message_to_delete = await message.answer(
            'Города иногда имеют похожее название.\nМожно уточнить пункт назначения в списке ниже:', reply_markup=kb)
        await UserStates.next()
    else:
        UserProfile.all_users[message.from_user.id].message_to_delete = await message.answer(
            'Похоже, таких городов не нашлось, совет:\nПопробуйте ещё разок.')


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserStates.hotels_quantity)
async def check_get_hotels_quantity(message: Message, state: FSMContext) -> None:
    # ловим количество отелей, если не цифры - не пускаем дальше
    cur_user = UserProfile.all_users[message.from_user.id]
    await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
    cur_user.message_to_delete = await message.answer('Не похоже на цифры.\nПожалуйста, введите цифры.'
                                                      '\n(от 1 до 10, например)')


@dp.message_handler(lambda message: message.text.isdigit(), state=UserStates.hotels_quantity)
async def get_hotels_quantity(message: Message, state: FSMContext) -> None:
    # если цифры, то сохраняем количество отелей, устанавливаем arr_date_year состояние
    cur_user = UserProfile.all_users[message.from_user.id]
    await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
    if message.text == '0' or int(message.text) < 0:
        cur_user.message_to_delete = await message.answer('Меня не проведешь. Ноль или отрицательное - нельзя.\n '
                                                          'Давайте ещё раз:')
        await message.delete()
    cur_user.cities_quantity = message.text
    cur_user.message_to_delete = await bot.send_message(message.from_user.id,
                                                        'Необходимо выбрать дату заезда.\nПожалуйста, укажите год:',
                                                        reply_markup=inline_keyboard.year_calendar_keyboard()
                                                        )
    await message.delete()
    await UserStates.next()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserStates.min_night_price)
async def check_set_min_price(message: Message, state: FSMContext) -> None:
    # проверка на цифры
    cur_user = UserProfile.all_users[message.from_user.id]
    await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
    await message.delete()
    cur_user.message_to_delete = await message.answer('Похоже, вы ввели не цифры.\nПожалуйста, используйте цифры.')


@dp.message_handler(lambda message: message.text.isdigit(), state=UserStates.min_night_price)
async def check_set_min_price(message: Message, state: FSMContext) -> None:
    # если режим /bestdeal, ловим мин цену за ночь
    cur_user = UserProfile.all_users[message.from_user.id]
    if int(message.text) < 0:
        await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
        await message.delete()
        cur_user.message_to_delete = await message.answer('Меня не обманешь.\n'
                                                          'Пожалуйста, используйте только не отрицательные цифры.')
    else:
        cur_user.low = message.text
        await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
        await message.delete()
        cur_user.message_to_delete = await message.answer('Пожалуйста, укажите максимальную цену за ночь:')
        await UserStates.next()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserStates.max_night_price)
async def check_set_min_price(message: Message, state: FSMContext) -> None:
    # проверка на цифры
    cur_user = UserProfile.all_users[message.from_user.id]
    await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
    await message.delete()
    cur_user.message_to_delete = await message.answer('Похоже, вы ввели не цифры.\nПожалуйста, используйте цифры.')


@dp.message_handler(lambda message: message.text.isdigit(), state=UserStates.max_night_price)
async def check_set_min_price(message: Message, state: FSMContext) -> None:
    # если режим /bestdeal, ловим макс цену за ночь, если она меньше low, меняем местами
    cur_user = UserProfile.all_users[message.from_user.id]
    if int(message.text) < 0:
        await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
        await message.delete()
        cur_user.message_to_delete = await message.answer('Меня не обманешь.\n'
                                                          'Пожалуйста, используйте только не отрицательные цифры.')
    else:
        if int(cur_user.low) > int(message.text):
            cur_user.low, cur_user.high = message.text, cur_user.low
            await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
            await message.delete()
            await UserStates.show_results.set()
            cur_user.message_to_delete = await bot.send_message(message.from_user.id,
                                                                'Немного перепутали min и max. Я поменяю.\n'
                                                                'Параметры сохранены.\nНажмите "показать".',
                                                                reply_markup=inline_keyboard.show_result()
                                                                )
        else:
            cur_user.high = message.text
            await bot.delete_message(chat_id=message.from_user.id, message_id=cur_user.message_to_delete.message_id)
            await message.delete()
            await UserStates.show_results.set()
            cur_user.message_to_delete = await bot.send_message(message.from_user.id,
                                                                'Параметры сохранены.\nНажмите "показать".',
                                                                reply_markup=inline_keyboard.show_result()
                                                                )


@dp.message_handler(content_types='text')
async def echo_answer(message: Message) -> None:
    # Если пользователь вне состояния, эхо ответ + добавление в словарь (если не добавлен)
    if message.from_user.id not in UserProfile.all_users:
        UserProfile.all_users[message.from_user.id] = UserProfile(message.from_user.id, '0', '/start')
        cur_user = UserProfile.all_users[message.from_user.id]
        cur_user.message_to_delete = await message.answer('Попробуйте команду /start')
    else:
        cur_user = UserProfile.all_users[message.from_user.id]
        cur_user.message_to_delete = await message.answer('Попробуйте команду /start')
