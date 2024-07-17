from aiogram.types import InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_categories, get_category_item, select_alladmins, get_meetings_info, get_admins

from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton
class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы

class Pagination_Meeting(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы
    server: int
# Определение callback data для кнопки бана пользователя
class Admin_Stats(CallbackData, prefix='admin_stats'):
    users_id: int  # Поле для идентификатора пользователя

class Update_Level(CallbackData, prefix='upd_lvl'):
    users_id: int  # Поле для идентификатора пользователя
    level: int
class Set_Level(CallbackData, prefix='set_lvl'):
    level: int
class Set_Admin(CallbackData, prefix = 'set_admin'):
    users_id: int
    level: int

class Get_Meeting(CallbackData, prefix = 'get_meeting'):
    server: int
    datetime_meeting: str
    description: str
    from_adm: str
async def main():
    buttons = [
        [
            types.InlineKeyboardButton(text='📝 Заполнение анкеты', callback_data=f'forms')
        ],
        [types.InlineKeyboardButton(text='⭐ Функционал Admin Bot', callback_data=f'info_user')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def main_admins():

    admin_buttons = [
        [types.InlineKeyboardButton(text='🛠️ Админ-панель', callback_data=f'admin_panel')],
        [
            types.InlineKeyboardButton(text='📝 Заполнение анкеты', callback_data=f'forms')
        ],
        [
            types.InlineKeyboardButton(text='📖 Информация с собраний', callback_data=f'get_meetings_info')
        ],
        [types.InlineKeyboardButton(text='⭐ Функционал Admin Bot', callback_data=f'info_admin')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    return keyboard
async def admin_msg(tg_id):
    buttons = [
        [
            types.InlineKeyboardButton(text='📛 Заблокировать (спам)', callback_data=f'ban_{tg_id}')
        ],

    ]


    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=f'🔗 {category.name}', callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='◀️ На главную', callback_data=f'to_main'))
    return keyboard.adjust(2).as_markup()

async def admin_act():
    admin_buttons = [
        [types.InlineKeyboardButton(text='🌎 Расстояние между IP', callback_data=f'ip_dist')],
        [types.InlineKeyboardButton(text='🌐 Информация об одном IP', callback_data=f'get_ip')],
        [types.InlineKeyboardButton(text='⚡ Список администраторов', callback_data=f'get_admins')],
        [types.InlineKeyboardButton(text='🔊 Создать информацию с собрания', callback_data=f'set_meeting_info')],
        [types.InlineKeyboardButton(text='🟢 Выдать доступ администратора', callback_data=f'set_admin')],
        [
            types.InlineKeyboardButton(text='◀️ На главную', callback_data='to_main')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    return keyboard
async def admin_list_actions(tg_id):
    admin_buttons = [
        [types.InlineKeyboardButton(text='Данные об администраторе', callback_data=f'adminStatsAct_{tg_id}')],
        [types.InlineKeyboardButton(text='Обновить уровень доступа', callback_data=f'updateLevelAct_{tg_id}')],
        [types.InlineKeyboardButton(text='Удалить администратора', callback_data=f'delAdmin_{tg_id}')],
        [
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data=Pagination(action='cancel', page=0).pack())
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    return keyboard

async def admin_levels(tg_id):
    admin_buttons = [
        [types.InlineKeyboardButton(text='Администратор', callback_data=Update_Level(users_id = tg_id, level=1).pack())],
        [types.InlineKeyboardButton(text='Куратор Администрации', callback_data= Update_Level(users_id = tg_id, level = 2).pack())],
        [types.InlineKeyboardButton(text='Зам. Главного Администратора', callback_data=Update_Level(users_id = tg_id, level=3).pack())],
        [types.InlineKeyboardButton(text='Основной Зам. Главного Администратора', callback_data=Update_Level(users_id = tg_id, level = 4).pack())],
        [types.InlineKeyboardButton(text='Главный Администратор',
                                    callback_data=Update_Level(users_id=tg_id, level=5).pack())],
        [
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data=Admin_Stats(users_id=tg_id).pack())
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    return keyboard
async def admin_levels_act():
    admin_buttons = [
        [types.InlineKeyboardButton(text='Администратор', callback_data=Set_Level(level=1).pack())],
        [types.InlineKeyboardButton(text='Куратор Администрации', callback_data=Set_Level(level=2).pack())],
        [types.InlineKeyboardButton(text='Зам. Главного Администратора', callback_data=Set_Level(level=3).pack())],
        [types.InlineKeyboardButton(text='Основной Зам. Главного Администратора', callback_data=Set_Level(level=4).pack())],
        [types.InlineKeyboardButton(text='Главный Администратор', callback_data=Set_Level(level=5).pack())],
        [types.InlineKeyboardButton(text='⬅️ Назад', callback_data='set_admin')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    return keyboard

async def back():
    buttons = [
        [
            types.InlineKeyboardButton(text='◀️ На главную', callback_data='to_main')
            ]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# все админы

async def paginator(page: int = 0):
    users = await select_alladmins()

    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    for user in users[start_offset:end_offset]:  # Перебор пользователей для текущей страницы
        builder.row(InlineKeyboardButton(text=f'👤 {user.username} ┃ {user.level} ⭐', callback_data=Admin_Stats(users_id=user.tg_id).pack()))  # Добавление кнопки для каждого пользователя
    buttons_row = []  # Создание списка кнопок
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(users):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1).pack()))  # Добавление кнопки "вперед"
    builder.row(*buttons_row)  # Добавление кнопок навигации
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel'))  # Добавление кнопки "назад"
    return builder.as_markup()  # Возвращение клавиатуры в виде разметки

async def paginator_meeting(server, page: int = 0):
    all_meetings_info = await get_meetings_info(server)

    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    for meeting in all_meetings_info[start_offset:end_offset]:  # Перебор собраний для текущей страницы
        builder.row(InlineKeyboardButton(text=f'🕜 {meeting.datetime_meeting}', callback_data=f'meeting_{meeting.id}'))  # Добавление кнопки для каждого пользователя
    buttons_row = []  # Создание списка кнопок
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination_Meeting(action="prev", page=page - 1, server=server).pack()))  # Добавление кнопки "назад"
    if end_offset < len(all_meetings_info):  # Проверка, что ещё есть собрания для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_Meeting(action="next", page=page + 1, server=server).pack()))  # Добавление кнопки "вперед"
    builder.row(*buttons_row)  # Добавление кнопок навигации
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='to_main'))  # Добавление кнопки "назад"
    return builder.as_markup()  # Возвращение клавиатуры в виде разметки