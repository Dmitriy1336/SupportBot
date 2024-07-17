
from aiogram import F, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from keyboards import Pagination, Set_Level, Pagination_Meeting

import keyboards as kb
import database.requests as rq

from aiogram.fsm.context import FSMContext

import requests
from math import *

from keyboards import Admin_Stats, Update_Level
import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, InlineKeyboardButton


router = Router()

class Admin(StatesGroup):
    Set_Admin_Tg = State()
    Set_Admin_Nick = State()
    Set_Admin_Serv = State()
    Set_Admin_Lvl = State()
    Del_Admin = State()
    Ip_dist = State()
    Ip_info = State()
    Set_Meeting = State()

@router.callback_query(F.data == 'admin_panel')
async def panel(callback: CallbackQuery):
    await callback.message.edit_text('<b>📋 Выберите необходимый инструмент:</b>', reply_markup=await kb.admin_act(), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data == 'ip_dist')
async def ip_dist(callback: CallbackQuery, state: FSMContext):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel')) # Добавление кнопки "назад"
    await state.set_state(Admin.Ip_dist)
    await callback.message.edit_text('<b>🔍 Введите 2 IP-адреса через пробел для получения информации.\n\n<u>Пример</u>: 208.80.152.201 91.198.174.192</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
    await callback.answer()

@router.callback_query(F.data == 'get_ip')
async def get_ip(callback: CallbackQuery, state: FSMContext):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel')) # Добавление кнопки "назад"
    await state.set_state(Admin.Ip_info)
    await callback.message.edit_text('<b>🔍 Введите IP адрес для получения информации.\n\n<u>Пример</u>: 208.80.152.201</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
    await callback.answer()
@router.message(Admin.Ip_info)
async def info_ip(message: Message):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
    ip = message.text
    r = requests.get(f"http://ip-api.com/json/{ip}?lang=ru")
    data = r.json()
    country = data['country']
    city = data['city']
    isp = data['isp']
    org = data['org']
    await message.answer(f'<b>Информация по IP: {ip}\n\n'
                         f'Страна: {country}\n'
                         f'Город: {city}\n'
                         f'Интернет-провайдер: {isp}\n'
                         f'Название организации провайдера: {org}</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())

@router.callback_query(F.data == 'set_meeting_info')
async def set_info(callback: CallbackQuery, state: FSMContext):
    chief_admin = await rq.get_admin_lvl(callback.from_user.id)
    if chief_admin >= 5:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel')) # Добавление кнопки "назад"
        await callback.message.edit_text(f'<b>✎ Введите информацию с собрания, которую хотите записать для своих администраторов.\n\n'
                                         f'📁 Пишите текст тезисно (по пунктам), чтобы администрация могла четко и быстро понять суть передаваемой информации.\n\n'
                                         f'⚙️ Попытайтесь сжать текст, имеется ограничение в размере до 2.000 символов.</b>', reply_markup=kb_back.as_markup(),
                                         parse_mode='HTML')
        await state.set_state(Admin.Set_Meeting)
    else:
        await callback.answer(show_alert=True, text='❌ Доступ закрыт.\n\nЗаполнять информацию с собраний могут только руководители сервера.')
@router.callback_query(F.data == 'set_admin')
async def set_admin(callback: CallbackQuery, state: FSMContext):
    leads = await rq.get_leads()
    admin_level = await rq.get_admin_lvl(tg_id=callback.from_user.id)
    if admin_level < 5:
        await callback.answer('Доступ закрыт')
    else:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
        await callback.message.edit_text('<b>🆔 Введите Telegram ID пользователя:</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
        await state.set_state(Admin.Set_Admin_Tg.state)
        await callback.answer()
@router.callback_query(Set_Level.filter())
async def rq_set_admin_serv(callback: CallbackQuery, callback_data: Set_Level, state: FSMContext):
    chief_admin = await rq.get_admin_lvl(callback.from_user.id)
    if callback_data.level < chief_admin:
        await state.update_data(chosen_lvl=callback_data.level)
        get_server = await rq.get_admin_serv(callback.from_user.id)
        await state.update_data(chosen_serv=get_server)
        admins = await rq.get_admins()
        admins_nick = await rq.get_admins_nick()
        user_data = await state.get_data()
        pos = ['Администратор', 'Куратор администрации', 'Зам. Главного Администратора', 'Основной Зам. Главного Администратора', 'Главный администратор', 'Разработчик Admin Bot | Главный администратор']
        if int(user_data['chosen_tg']) not in admins and (user_data['chosen_nick']) not in admins_nick:
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Список администрации',
                                             callback_data=Pagination(action='cancel', page=0).pack()))  # Добавление кнопки "назад"
            await rq.set_admin(user_data['chosen_tg'], user_data['chosen_nick'], user_data['chosen_serv'], user_data['chosen_lvl'], pos[user_data['chosen_lvl']-1])
            await callback.message.edit_text(text=f'<b>🎉 Пользователь {user_data["chosen_nick"]} был добавлен в реестр администраторов!</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
            try:
                file_path = "/root/bots/supportbot/grace.png"
                await callback.message.bot.send_photo(chat_id=user_data["chosen_tg"], photo=types.FSInputFile(file_path), caption=f'<b>🥳 {user_data["chosen_nick"]}, вы были назначены на должность администратора {user_data["chosen_lvl"]} уровня в Admin Bot!\n\n🎉 Желаем приятного использования!\n\nНажмите /start для начала.</b>', parse_mode='HTML')
            except:
               return
            await callback.answer()
        else:
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Список администрации',
                                             callback_data=Pagination(action='cancel',
                                                                      page=0).pack()))  # Добавление кнопки "назад"
            await callback.message.edit_text(f'<b>❌ Пользователь уже находится в рестре администраторов!\n\n🔒 Nick_Name или Telegram ID пользователя уже заняты.</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
            await callback.answer()
        await state.clear()
    else:
        await callback.answer(show_alert=True, text='Доступ закрыт.\n\nВы не можете выдавать доступ, равный вашему или превышающего ваш уровень администратора.')


@router.callback_query(F.data.startswith('get_admins'))
async def category(callback: CallbackQuery):
    await callback.message.edit_text(text=f'<b>Список администрации</b>:', reply_markup=await kb.paginator(page=0), parse_mode='HTML')
    await callback.answer()


@router.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination):
    page = callback_data.page  # Получение номера страницы из callback data
    await call.message.edit_text(f'<b>Список администрации:</b>', reply_markup=await kb.paginator(page=page), parse_mode='HTML')

@router.callback_query(Pagination_Meeting.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_Meeting):
    page = callback_data.page  # Получение номера страницы из callback data
    await call.message.edit_text(f'<b>Информация с собраний:</b>', reply_markup=await kb.paginator_meeting(server=callback_data.server, page=page), parse_mode='HTML')

@router.callback_query(Admin_Stats.filter())
async def get_actions(callback: CallbackQuery, callback_data: Admin_Stats):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data=Pagination(action='cancel', page=0).pack())) # Добавление кнопки "назад"
    await callback.message.edit_text(f'<b>Выберите нужное действие:</b>', reply_markup=await kb.admin_list_actions(tg_id=callback_data.users_id), parse_mode='HTML')
    await callback.answer()

@router.callback_query(Update_Level.filter())
async def get_actions(callback: CallbackQuery, callback_data: Update_Level):
    chief_admin_lvl = await rq.get_admin_lvl(callback.from_user.id)
    if (chief_admin_lvl >= 5 and callback_data.level != 5) or (chief_admin_lvl == 6):
        if callback_data.users_id == callback.from_user.id:
            await callback.answer(show_alert=True, text='⛔ Доступ закрыт.\n\n⚠️ Вы не можете сами себе изменять доступ.')
            await callback.message.edit_text(f'<b>Выберите нужное действие:</b>',
                                             reply_markup=await kb.admin_list_actions(tg_id=callback_data.users_id),
                                             parse_mode='HTML')
        else:
            pos = ['Администратор', 'Куратор Администрации', 'Зам. Главного Администратора', 'Основной Зам. Главного Администратора', 'Главный Администратор']

            await rq.update_level(callback_data.users_id, callback_data.level, pos[callback_data.level-1])
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data=Pagination(action='cancel', page=0).pack())) # Добавление кнопки "назад"
            await callback.message.edit_text(f'<b>Уровень был изменен.</b>', reply_markup=await kb.admin_list_actions(tg_id=callback_data.users_id), parse_mode='HTML')
            await callback.answer()
    else:
        await callback.answer(show_alert=True, text='⛔ Доступ закрыт!\n\n⚠️ Ваш уровень не позволяет обновить уровень доступа администратора.')
        await callback.message.edit_text(f'<b>Выберите нужное действие:</b>',
                                         reply_markup=await kb.admin_list_actions(tg_id=callback_data.users_id),
                                         parse_mode='HTML')


@router.callback_query(F.data.startswith('adminStatsAct_'))
async def admin_stats(callback: CallbackQuery):
    item_data = callback.data.split('_')
    tg_id = item_data[1]
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data=Admin_Stats(users_id=tg_id).pack()))  # Добавление кнопки "назад"
    admin_state = await rq.get_admins_state(tg_id)
    await callback.message.edit_text(f'<b>⭐ Данные администратора:\n\nNick_Name: {admin_state.username}\nДолжность: {admin_state.position}\nУровень доступа: {admin_state.level}\nСервер: {admin_state.server}\nTelegram ID: {admin_state.tg_id}</b>', reply_markup=kb_back.as_markup(), parse_mode='HTML')  # Отправка сообщения об успешном бане пользователя

@router.callback_query(F.data.startswith('updateLevelAct_'))
async def update_level_act(callback: CallbackQuery):
    item_data = callback.data.split('_')
    tg_id = item_data[1]
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад',
                                     callback_data=Admin_Stats(users_id=tg_id).pack()))  # Добавление кнопки "назад"
    await callback.message.edit_text(f'<b>Выберите уровень доступа:</b>', reply_markup=await kb.admin_levels(tg_id), parse_mode='HTML')


@router.callback_query(F.data.startswith('delAdmin_'))
async def del_admin_act(callback: CallbackQuery):
    item_data = callback.data.split('_')
    tg_id = item_data[1]
    chief_admin_lvl = await rq.get_admin_lvl(callback.from_user.id)
    delete_admin_lvl = await rq.get_admin_lvl(tg_id)
    if chief_admin_lvl > delete_admin_lvl:
        chief_admin_serv = await rq.get_admin_serv(callback.from_user.id)
        delete_admin_serv = await rq.get_admin_serv(tg_id)
        if chief_admin_serv == delete_admin_serv or chief_admin_lvl == 6:
            await rq.del_admin(tg_id=tg_id)
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Назад',
                                             callback_data=Admin_Stats(users_id=tg_id).pack()))  # Добавление кнопки "назад"
            await callback.message.edit_text(f'<b>📉 Администратор был удален.</b>', reply_markup=await kb.paginator(page=0), parse_mode='HTML')
            await callback.message.bot.send_message(chat_id=tg_id,
                                     text='<b>🤖 Уровень доступа изменился!\n\n📉 Вам был выдан доступ пользователя.</b>',
                                     parse_mode='HTML')
        else:
            await callback.answer(show_alert=True, text='⛔ Доступ закрыт.\n\n⚠️ Вы не можете удалить администратора с другого сервера.')

    else:
        await callback.answer(show_alert=True, text=f'⛔ Доступ закрыт.\n\n⚠️ Вы не можете удалить администратора с доступом выше вашего. Также, вы не можете удалить сами себя.')

@router.callback_query(F.data.startswith('ban_'))
async def category(callback: CallbackQuery):
    item_data = callback.data.split('_', 1)
    user_id = item_data[1]
    blacklist = await rq.get_banned_users()
    current_date = datetime.datetime.now()
    current_date_string = current_date.strftime('%d.%m.%y | %H:%M:%S')
    if int(user_id) not in blacklist:
        await rq.give_ban(int(user_id), 'спам', current_date_string)
        await callback.message.answer(f'<b>⚠️ Пользователь был заблокирован в Admin Bot.\n\n⛔ Причина: спам\n\n🕝 Дата блокировки: {current_date_string}</b>',
                             parse_mode='HTML')
        file_path = "/root/bots/supportbot/ban_img.jpg"
        await callback.message.bot.send_photo(chat_id=user_id, photo=types.FSInputFile(path=file_path), caption=f'<b>⚠️ Вы были заблокированы администратором Admin Bot!\n\n⛔ Причина: спам\n\n🕝 Дата блокировки: {current_date_string}</b>',  parse_mode='HTML')
        await callback.answer()
    else:
        await callback.message.answer(f'<b>⚠️ Пользователь уже заблокирован в Admin Bot.</b>',
                             parse_mode='HTML')
        await callback.answer()


@router.callback_query(F.data == 'get_meetings_info')
async def get_info(callback: CallbackQuery):
    server = await rq.get_admin_serv(callback.from_user.id)
    await callback.message.edit_text(
        f'<b>Информация с собраний:</b>',
        reply_markup=await kb.paginator_meeting(server, page=0),
        parse_mode='HTML')

@router.callback_query(F.data.startswith('meeting_'))
async def set_message(callback: CallbackQuery):
    meeting_id = callback.data.split('_')[1]
    meeting = await rq.get_meeting_id(meeting_id)
    chief_admin_lvl = await rq.get_admin_lvl(callback.from_user.id)
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='get_meetings_info'))  # Добавление кнопки "назад"
    if chief_admin_lvl >= 5:
        kb_back.row(InlineKeyboardButton(text='🗑 Удалить информацию с собрания', callback_data=f'delMeeting_{meeting.id}'))  # Добавление кнопки "назад"
    await callback.message.edit_text(
        f'<b>💁 Информация за {meeting.datetime_meeting} получена.\n\n'
        f'➕ Добавлено администратором {meeting.level} уровня - {meeting.username}.\n\n'
        f'{meeting.description}</b>',
        reply_markup=kb_back.as_markup(),
        parse_mode='HTML')

@router.message(Admin.Set_Admin_Tg)
async def rq_set_admin(message: Message, state: FSMContext):
    if message.text.isdigit() == True:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='set_admin'))  # Добавление кнопки "назад"
        await state.update_data(chosen_tg=message.text)
        await message.answer('<b>🔴 Введите Nick_Name пользователя в игре:\n\n<u>Пример</u>: Jaden_Young</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
        await state.set_state(Admin.Set_Admin_Nick)
    else:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
        await message.answer('<b>🆔 Введите корректный Telegram ID пользователя:</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
        await state.set_state(Admin.Set_Admin_Tg.state)

@router.message(Admin.Set_Meeting)
async def set_meet(message: Message, state: FSMContext):
    if len(message.text) <= 2000:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(
            InlineKeyboardButton(text='⬅️ В админ-панель', callback_data='admin_panel'))  # Добавление кнопки "назад"
        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime('%d.%m.%y')
        admin = await rq.get_admin(message.from_user.id)
        await rq.set_meetings_info(message.from_user.id, admin.username, admin.server, admin.level, current_date_string, message.text)
        await message.answer(
            f'<b>📩 Информация была записана и отправлена!\n\n'
            f'🕜 Дата отправки данной информации - {current_date_string}</b>',
            reply_markup=kb_back.as_markup(),
            parse_mode='HTML')
        await state.clear()
    else:
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
        await message.answer(
            f'<b>✎ Вы ввели информацию на более чем 2.000 символов.\n\n'
            f'⚙️ Попытайтесь сжать текст и исключить ненужные предложения.</b>',
            reply_markup=kb_back.as_markup(),
            parse_mode='HTML')
        await state.set_state(Admin.Set_Meeting)


@router.message(Admin.Ip_dist)
async def ip_dist(message: Message):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
    item_data = message.text.split(' ', 1)
    ip1 = item_data[0]
    ip2 = item_data[1]
    def distance(Lat1, Lat2, Lon1, Lon2):
        Lon1 = radians(Lon1)
        Lon2 = radians(Lon2)
        Lat1 = radians(Lat1)
        Lat2 = radians(Lat2)

        DLon = Lon2 - Lon1  # магия тригонометрии
        DLat = Lat2 - Lat1  # магия тригонометрии
        P = sin(DLat / 2) ** 2 + cos(Lat1) * cos(Lat2) * sin(DLon / 2) ** 2  # магия тригонометрии
        Q = 2 * asin(sqrt(P))  # магия тригонометрии
        R = 6371  # радиус земли

        return (Q * R)

    r = requests.get(f"http://ip-api.com/json/{ip1}?lang=ru")
    data = r.json()
    Lat1 = data['lat']
    Lon1 = data['lon']
    country1 = data['country']
    city1 = data['city']
    isp1 = data['isp']
    org1 = data['org']
    r2 = requests.get(f"http://ip-api.com/json/{ip2}?lang=ru")
    data2 = r2.json()
    Lat2 = data2['lat']
    Lon2 = data2['lon']
    country2 = data2['country']
    city2 = data2['city']
    isp2 = data2['isp']
    org2 = data2['org']

    result = round(distance(Lat1, Lat2, Lon1, Lon2))
    await message.answer(f'<b>Информация по IP 1: {ip1}\n\n'
                         f'Страна: {country1}\n'
                         f'Город: {city1}\n'
                         f'Интернет-провайдер: {isp1}\n'
                         f'Название организации провайдера: {org1}\n\n'
                         f'Информация по IP 2: {ip2}\n\n'
                         f'Страна: {country2}\n'
                         f'Город: {city2}\n'
                         f'Интернет-провайдер: {isp2}\n'
                         f'Название организации провайдера: {org2}\n\n'
                         f'<u>Расстояние между IP: {result} километров</u></b>', parse_mode='HTML',
                         reply_markup=kb_back.as_markup())  # результат

@router.message(Admin.Set_Admin_Nick)
async def rq_set_admin(message: Message, state: FSMContext):
    flag = True
    for i in range(len(message.text)):
        if 65 <= ord(message.text[i]) <= 90 or 97 <= ord(message.text[i]) <= 122 or ord(message.text[i]) == 95:
            continue
        else:
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='set_admin'))  # Добавление кнопки "назад"
            await message.answer('<b>🔴 Введите корректный Nick_Name (английскийми буквами с нижним подчеркиванием):\n\n<u>Пример</u>: Jaden_Young</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
            await state.set_state(Admin.Set_Admin_Nick)
            flag = False
            break
    if flag:
        await state.update_data(chosen_nick=message.text.title())
        await state.set_state(Admin.Set_Admin_Lvl)
        await message.answer('<b>Выберите должность:</b>', parse_mode='HTML', reply_markup=await kb.admin_levels_act())

@router.callback_query(F.data.startswith('delMeeting_'))
async def del_meeting(callback: CallbackQuery):
    item_data = callback.data.split('_')
    meeting_id = item_data[1]
    server = await rq.get_admin_serv(callback.from_user.id)
    chief_admin_lvl = await rq.get_admin_lvl(callback.from_user.id)
    if chief_admin_lvl >= 5:
        await rq.del_meeting(meeting_id)
        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='get_meetings_info')) # Добавление кнопки "назад"
        await callback.message.edit_text(f'<b>Информация о собрании была удалена.</b>', reply_markup=await kb.paginator_meeting(server, page=0), parse_mode='HTML')
    else:
        await callback.answer(show_alert=True, text='⛔ Доступ закрыт.')


@router.callback_query(F.data == 'info_admin')
async def settings(callback: CallbackQuery):
    await callback.message.edit_text('<b>🖥  Узнайте больше о возможностях Admin Bot!\n\n'

                                     '⭐️ Данный бот является помощником для администрации.\n\n'

                                     '🧠 Функционал с доступом администратора:\n\n'
                                     '1️⃣ Админ-панель:\n\n'
                                     '1. Возможность узнать расстояние между двумя IP.\n'
                                     '2. Возможность узнать информацию об определенном IP.\n'
                                     '3. Список администрации - возможность просмотра данных, изменения, удаления администраторов.\n'
                                     '4. Удобная пагинация кнопок по страницам в списке администрации (на каждой странице по 10 администраторов).\n'
                                     '5. Создание информации с собрания для администрации своего сервера, а также удаление, если это необходимо.\n'
                                     '6. Выдача доступов администратора.\n\n'
                                     '2️⃣ Заполнение анкеты:\n\n'
                                     '1. Создание и передача анкеты руководству сервера (анкеты на проверку кандидатов на должность лидера или Агента поддержки).\n'
                                     '2. Поддержка медиа-картинок в сообщении.\n'
                                     '3. Возможность получать ответное сообщение на вашу анкету от руководителей сервера.\n'
                                     '4. Выполнение роли бота "обратной связи": передача информации происходит между вами и администратором через диалог с Admin Bot!\n\n'
                                     '3️⃣ Информация с собраний:\n\n'
                                     '1. Возможность просматривать информацию с собраний, которые создали руководители сервера.\n'
                                     '2. Удобная пагинация кнопок по страницам (на каждой по 10 кнопок).\n\n'

                                     '🚀 Просто и удобно вместе с Admin Bot!\n\n'

                                     '🔗 Контакты разработчика - @young_keef</b>', parse_mode='HTML',
                                     reply_markup=await kb.back())

    await callback.answer()