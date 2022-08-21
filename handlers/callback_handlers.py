from utils.misc.class_User import UserProfile, date_correction
from utils.misc.class_FSM import UserStates
from utils import hotels_photo, hotels_search
from utils.loader import dp, bot
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline import inline_keyboard
from aiogram.dispatcher.filters import Text
from database.base_inition.users_db import set_user_history, delete_from_history
import time
import emoji


@dp.callback_query_handler(Text('/cancel'), state='*')
async def command_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    # если поймали callback == '/cancel' - то сбрасываем статус сценария на "0"
    # полностью выходим из режима состояния диалога (поиска отеля)
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.message_to_delete = await callback.answer('Вы вышли из режима поиска', show_alert=True)
    UserProfile.all_users[callback.from_user.id].set_status('0', '/start')
    if state is not None:
        await state.finish()
    else:
        return


@dp.callback_query_handler(state=UserStates.city_id)
async def cities_to_choose(callback: CallbackQuery, state: FSMContext) -> None:
    # ловим callback с клавиатуры названий городов, сохраняем id локации
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.city_id = callback.data
    cur_user.message_to_delete = await bot.send_message(callback.from_user.id, 'Какое количество отелей будем искать?')
    await UserStates.next()


@dp.callback_query_handler(state=UserStates.arr_date_year)
async def get_arr_year(callback: CallbackQuery, state=FSMContext) -> None:
    # получаем строкой год, запрашиваем месяц
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    await bot.send_message(callback.from_user.id,
                           'Укажите, пожалуйста, месяц:',
                           reply_markup=inline_keyboard.month_calendar_keyboard(cur_user.temporary_data[0])
                           )
    await UserStates.next()


@dp.callback_query_handler(state=UserStates.arr_date_month)
async def get_arr_month(callback: CallbackQuery, state: FSMContext) -> None:
    # получаем строкой месяц, запрашиваем день
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    await bot.send_message(callback.from_user.id,
                           'Укажите, пожалуйста, день:',
                           reply_markup=inline_keyboard.day_calendar_keyboard(
                               cur_user.temporary_data[1], cur_user.temporary_data[0])
                           )
    await UserStates.next()


@dp.callback_query_handler(state=UserStates.arr_date_day)
async def get_arr_day(callback: CallbackQuery, state: FSMContext) -> None:
    # получаем строкой день, temporary_data склеиваем с "-" и сохраняем в arr_date класса, запрашиваем год
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    cur_user.arr_date = '-'.join(cur_user.temporary_data)
    cur_user.temporary_data = []
    await UserStates.next()
    await bot.send_message(callback.from_user.id,
                           'До какого дня планируете отдых?.\nПожалуйста, укажите год:',
                           reply_markup=inline_keyboard.year_calendar_keyboard()
                           )


@dp.callback_query_handler(state=UserStates.dep_date_year)
async def get_depp_year(callback: CallbackQuery, state=FSMContext) -> None:
    # получаем строкой год, запрашиваем месяц
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    await bot.send_message(callback.from_user.id,
                           'Укажите, пожалуйста, месяц:',
                           reply_markup=inline_keyboard.month_calendar_keyboard(cur_user.temporary_data[0])
                           )
    await UserStates.next()


@dp.callback_query_handler(state=UserStates.dep_date_month)
async def get_dep_month(callback: CallbackQuery, state: FSMContext) -> None:
    # получаем строкой месяц, запрашиваем день
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    await bot.send_message(callback.from_user.id,
                           'Укажите, пожалуйста, день:',
                           reply_markup=inline_keyboard.day_calendar_keyboard(
                               cur_user.temporary_data[1], cur_user.temporary_data[0]))
    await UserStates.next()


@dp.callback_query_handler(state=UserStates.dep_date_day)
async def get_dep_day(callback: CallbackQuery, state: FSMContext) -> None:
    # получаем строкой день, temporary_data склеиваем с "-" и сохраняем в dep_date класса, запрашиваем год
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    cur_user.temporary_data.append(callback.data)
    cur_user.dep_date = '-'.join(cur_user.temporary_data)
    # проверяем дату на корректность
    correct_date = date_correction(cur_user.arr_date, cur_user.dep_date)
    cur_user.arr_date, cur_user.dep_date = correct_date[0], correct_date[1]
    cur_user.temporary_data = []
    await UserStates.next()
    cur_user.message_to_delete = await bot.send_message(callback.from_user.id,
                                                        'Учтите: более ранняя дата будет считаться днём заселения.\n'
                                                        'Вам понадобятся фотографии?',
                                                        reply_markup=inline_keyboard.yes_or_no_keyboard()
                                                        )


@dp.callback_query_handler(state=UserStates.photo_actual)
async def get_photo_quantity(callback: CallbackQuery, state: FSMContext) -> None:
    # ловим "да" или "нет", если "да" запрашиваем кол-во фото
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    if callback.data == 'photo_yes':
        cur_user.actual_photo = callback.data
        await bot.send_message(callback.from_user.id,
                               'Укажите количество фотографий для вывода:',
                               reply_markup=inline_keyboard.set_photo_quantity_keyboard()
                               )
        await UserStates.next()
    else:
        await UserStates.show_results.set()
        cur_user.actual_photo = callback.data
        await bot.send_message(callback.from_user.id,
                               'Параметры сохранены.\nНажмите "показать".',
                               reply_markup=inline_keyboard.show_result())


@dp.callback_query_handler(state=UserStates.photo_quantity)
async def set_photo_quantity(callback: CallbackQuery, state: FSMContext) -> None:
    # сохраняем кол-во фотографий
    cur_user = UserProfile.all_users[callback.from_user.id]
    cur_user.photo_quantity = callback.data
    await callback.message.delete()
    await UserStates.show_results.set()
    await bot.send_message(callback.from_user.id,
                           'Параметры сохранены.\nНажмите "показать".',
                           reply_markup=inline_keyboard.show_result())


@dp.callback_query_handler(state=UserStates.show_results)
async def show_hotels(callback: CallbackQuery, state: FSMContext) -> None:
    # показываем отели
    cur_user = UserProfile.all_users[callback.from_user.id]
    await callback.message.delete()
    total_result = hotels_search.get_hotels(callback.from_user.id,
                                            cur_user.city_id,
                                            cur_user.status[1],
                                            cur_user.arr_date,
                                            cur_user.dep_date,
                                            locale='en_US',
                                            quantity=cur_user.cities_quantity,
                                            low=cur_user.low,
                                            high=cur_user.high,)

    if total_result is not None and len(total_result) > 0:
        if len(total_result) < int(cur_user.cities_quantity):
            await bot.send_message(callback.from_user.id, f'К сожалению нашлось всего {len(total_result)} отель(ей)')
        for i_elem in total_result.values():
            text_answer = emoji.emojize(
                          f'Сам отель: {i_elem[0]}\n' 
                          f'Цена за ночь: {i_elem[2]}\n' 
                          f'Кол-во звезд: {int(i_elem[1]) * ":star:"}\n' 
                          f'Адрес: {i_elem[4][:-6:]}\n' 
                          f'Расстояние до центра: {round(float(i_elem[5][0]) / 1.609, 1)} километра(ов)\n' 
                          f'Итоговая стоимость за период: {i_elem[3]}\n')

            cur_time = time.strftime('%d %B %Y %H:%M')
            tuple_to_history = (cur_user.status[1], cur_time, callback.from_user.id, i_elem[0], i_elem[6], i_elem[2])
            set_user_history('history', tuple_to_history)

            if cur_user.actual_photo == 'photo_yes':
                cur_message = await bot.send_media_group(callback.from_user.id,
                                                         hotels_photo.get_hotels_photo(i_elem[7],
                                                                                       cur_user.photo_quantity,
                                                                                       text_answer),
                                                         )
                string = ''
                for j_elem in cur_message:
                    string += f'{j_elem.message_id}-'

                under_text = emoji.emojize('Если отель не понравился, можно его просто удалить. :shushing_face:')
                cur_user.message_to_delete = await bot.send_message(callback.from_user.id, under_text,
                                                                    reply_markup=inline_keyboard.hotel_url(
                                                                        i_elem[0],
                                                                        i_elem[6],
                                                                        message=string,
                                                                        user_data=str(
                                                                            cur_user.message_to_delete.message_id)))
                async with state.proxy() as data:
                    data[cur_user.message_to_delete.message_id] = f'{i_elem[0]}+{i_elem[6]}+{i_elem[2]}'
            else:
                cur_user.message_to_delete = await bot.send_message(callback.from_user.id, text_answer,
                                                                    reply_markup=inline_keyboard.hotel_url(
                                                                        i_elem[0],
                                                                        i_elem[6],
                                                                        user_data=str(
                                                                            cur_user.message_to_delete.message_id)))
                async with state.proxy() as data:
                    data[callback.message.message_id] = f'{i_elem[0]}+{i_elem[6]}+{i_elem[2]}'

        cur_user.status[0], cur_user.status[1] = '0', '/start'
        await state.reset_state(with_data=False)


@dp.callback_query_handler(Text(startswith='hide'))
async def get_favorite_delete(callback: CallbackQuery) -> None:
    await callback.message.delete()
    if callback.data.startswith('hide_favorites'):
        delete_from_history('favorites', callback.from_user.id, callback.data[15::])


@dp.callback_query_handler(Text(startswith='OK'))
async def get_favorite_add(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    favorites_tuple = (UserProfile.all_users[callback.from_user.id].status[1],
                       time.strftime('%d %B %Y %H:%M'), callback.from_user.id, )
    async with state.proxy() as data:
        s_key = int(callback.data[3::])
        temporary = data[s_key].split('+')
    favorites_tuple += tuple(temporary)
    print(favorites_tuple)
    set_user_history('favorites', favorites_tuple)


@dp.callback_query_handler(Text(startswith='delete'))
async def get_hotel_delete(callback: CallbackQuery) -> None:
    # удаление сообщения(отеля), к которому прикреплена клавиатура
    await callback.message.delete()
    if not callback.data.endswith('None'):
        for i_elem in callback.data.split('-'):
            if i_elem != '' and i_elem != 'delete':
                await bot.delete_message(chat_id=callback.from_user.id, message_id=i_elem)
