from aiogram import F, Router, types
from aiogram.types import Message
import keyboards as kb
import database.requests as rq
from aiogram.filters import Command
import re
import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, InlineKeyboardButton


router = Router()


chat = ''
thread = ''
category_msg = int
isAns = False
chat_reply = ''









# КОМАНДЫ
@router.message(Command('start')) # start
async def cmd_start(message: Message):
    chats = await rq.get_chats()
    if message.chat.id in chats:
        return
    else:
        banned_users = await rq.get_banned_users()
        reason = await rq.get_reason(message.from_user.id)
        if message.from_user.id in banned_users:
            await message.answer(text=f'<b>⚠️ Вы были заблокированы администраторами Admin Bot!\n\n⛔ Причина: {reason}</b>', parse_mode='HTML')
        else:
            await rq.set_user(message.from_user.id)
            admin = await rq.get_admins()
            lead = await rq.get_leads()
            if message.from_user.id in admin or message.from_user.id in lead:
                await message.answer(f"<b>✌️Добро пожаловать, администратор {message.from_user.first_name}!</b>\n\n"
                                     f"<b>🛡️ Admin Bot является помощником для администрации.</b>\n\n"
                                     f"<b>📚 Воспользуйтесь меню для начала использования.</b>\n\n",
                                     reply_markup=await kb.main_admins(), parse_mode='HTML')
            else:
                await message.answer(f"<b>✌️Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
                                     f"<b>🛡️ Admin Bot является помощником для администрации.</b>\n\n"
                                     f"<b>📚 Воспользуйтесь меню для начала использования.</b>\n\n",
                                     reply_markup=await kb.main(), parse_mode='HTML')

@router.callback_query(F.data == 'to_main')
async def main(callback: CallbackQuery):
    admin = await rq.get_admins()
    lead = await rq.get_leads()
    if callback.from_user.id in admin or callback.from_user.id in lead:
        await callback.message.edit_text(f"<b>✌️Добро пожаловать, администратор {callback.from_user.first_name}!</b>\n\n"
                                     f"<b>🛡️ Admin Bot является помощником для администрации.</b>\n\n"
                                     f"<b>📚 Воспользуйтесь меню для начала использования.</b>\n\n",
                             reply_markup=await kb.main_admins(), parse_mode='HTML')
    else:
        await callback.message.edit_text(f"<b>✌️Добро пожаловать, {callback.from_user.first_name}!</b>\n\n"
                                     f"<b>🛡️ Admin Bot является помощником для администрации.</b>\n\n"
                                     f"<b>📚 Воспользуйтесь меню для начала использования.</b>\n\n",
                             reply_markup=await kb.main(), parse_mode='HTML')
    await callback.answer('Вы вернулись в меню')
@router.message(Command('ban'))
async def ban_user(message: Message):
    chats = await rq.get_chats()
    blacklist = await rq.get_banned_users()
    if message.chat.id in chats:
        command = message.text.split(' ', maxsplit=2)
        tg_id = command[1]
        reason = command[2]
        if tg_id not in blacklist:
            current_date = datetime.datetime.now()
            current_date_string = current_date.strftime('%d.%m.%y | %H:%M:%S')
            await rq.give_ban(tg_id, reason, current_date_string)
            await message.answer(
                f'<b>⚠️ Пользователь был заблокирован в Admin Bot.\n\n⛔ Причина: {reason}\n\n🕝 Дата блокировки: {current_date_string}</b>',
                parse_mode='HTML')
            file_path = "/root/bots/supportbot/ban_img.jpg"
            await message.bot.send_photo(chat_id=tg_id, photo=types.FSInputFile(path=file_path), caption=f'<b>⚠️ Вы были заблокированы администратором Admin Bot!\n\n⛔ Причина: {reason}\n\n🕝 Дата блокировки: {current_date_string}</b>', parse_mode='HTML')
        else:
            await message.answer(f'<b>⚠️ Пользователь уже заблокирован в Admin Bot.</b>',
                             parse_mode='HTML')
@router.message(Command('unban'))
async def unban_user(message: Message):
    chats = await rq.get_chats()
    blacklist = await rq.get_banned_users()
    if message.chat.id in chats:
        if message.from_user.id in blacklist:
            command = message.text.split(' ', maxsplit=2)
            tg_id = command[1]
            reason = command[2]
            await rq.delete_ban(tg_id)
            await message.answer(f'<b>✅ Пользователь был разблокирован в Admin Bot.\n\n🔓 Причина: {reason}</b>', parse_mode='HTML')
        else:
            await message.answer(f'<b>🛡️ Пользователь не находится в блокировке Admin Bot.</b>', parse_mode='HTML')

@router.message(Command('test'))
async def handle_test_command(message: Message):
    await message.reply_sticker('CAACAgIAAxkBAAEMUpVmbel9tT4d-LxSKAzFgOFBEWneyAACvAwAAocoMEntN5GZWCFoBDUE')


# РЕАГИРОВАНИЯ НА КНОПКИ

@router.callback_query(F.data == 'forms')
async def serv(callback: CallbackQuery):
    global category_msg
    if chat != '' or chat == 'None':
        admins = await rq.get_admins()
        if callback.from_user.id not in admins:
            item_data = await rq.get_category_item(category_msg, True)
        else:
            item_data = await rq.get_category_item(category_msg, False)

        kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
        kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='to_main'))  # Добавление кнопки "назад"
        await callback.message.edit_text(f'<b>{item_data.description}</b>', parse_mode='HTML',
                                         reply_markup=kb_back.as_markup())
        await callback.answer()
    else:
        await callback.message.edit_text('<b>📋 Выберите сервер:</b>', reply_markup=await kb.categories(), parse_mode='HTML')
        await callback.answer()
@router.callback_query(F.data == 'info_user')
async def settings(callback: CallbackQuery):
    await callback.message.edit_text('<b>🖥  Узнайте больше о возможностях Admin Bot!\n\n'
                                     
                                  '⭐️ Данный бот является помощником для администрации.\n\n'
                                     
                                  '🧠 Функционал с доступом пользователя:\n\n'
                                     
                                  '1. Создание и передача анкеты руководству сервера.\n'
                                  '2. Поддержка медиа-картинок в сообщении.\n'
                                  '3. Возможность получать ответное сообщение на вашу анкету от руководителей сервера.\n'
                                  '4. Выполнение роли бота "обратной связи": передача информации происходит между вами и администратором через диалог с Admin Bot!\n\n'
                                     
                                  '🥳 <u>Вы - новый администратор! Ваши действия по взаимодействию с Admin Bot описаны ниже:</u>\n\n'
                                
                                  '1️⃣ Вам необходимо нажать на кнопку "Заполнение анкеты";\n'
                                  '2️⃣ Выбрать сервер, на котором вы являетесь членом коллектива администрации;\n'
                                  '3️⃣ Заполнить форму, которую вам предоставит Admin Bot.\n\n'
                                
                                  '🚀 Просто и удобно вместе с Admin Bot!\n\n'
                                
                                   '🔗 Контакты разработчика - @young_keef</b>', parse_mode='HTML', reply_markup=await kb.back())

    await callback.answer()


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    global chat, thread, category_msg
    admins = await rq.get_admins()
    if callback.from_user.id not in admins:
        item_data = await rq.get_category_item(callback.data.split('_')[1], True)
    else:
        item_data = await rq.get_category_item(callback.data.split('_')[1], False)

    chat = item_data.chat
    thread = item_data.thread
    category_msg = item_data.category
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='to_main'))  # Добавление кнопки "назад"
    await callback.message.edit_text(f'<b>{item_data.description}</b>', parse_mode='HTML',
                                     reply_markup=kb_back.as_markup())
    await callback.answer('Вы выбрали сервер')


@router.message()
async def send(message: Message):
    global chat, thread, category_msg, chat_reply
    banned_users = await rq.get_banned_users()
    reason = await rq.get_reason(message.from_user.id)
    chats = await rq.get_chats()
    if message.from_user.id in banned_users:
        await message.answer(text=f'<b>⚠️ Вы были заблокированы администраторами Admin Bot!\n\n⛔ Причина: {reason}</b>', parse_mode='HTML')
    elif message.chat.id in chats:
        try:
            msg_form = re.search('анкета!(.*?)🧾 Данные о пользователе:', message.reply_to_message.text.strip().replace('\n', '')).group(1)
        except:
            msg_form = re.search('анкета!(.*?)🧾 Данные о пользователе:',
                                 message.reply_to_message.caption.strip().replace('\n', '')).group(1)

        message_reply = await rq.get_messages(msg_form)
        message_reply_id = await rq.get_messages_reply(msg_form)
        if str(msg_form) == str(message_reply):
            try:
                user_id = re.findall(r'\w+$', message.reply_to_message.text)
            except:
                user_id = re.findall(r'\w+$', message.reply_to_message.caption)
            if message.photo == None:
                await message.bot.send_message(reply_to_message_id=message_reply_id, chat_id=str(user_id[0]),
                                               text=f'<b>{message.text}</b>', parse_mode='HTML')
                await message.answer(text=f'<b>✅ Сообщение было отправлено пользователю.</b>',
                                     parse_mode='HTML')
            else:
                await message.bot.send_photo(reply_to_message_id=message_reply_id, chat_id=str(user_id[0]), photo=message.photo[-1].file_id, caption=f'<b>{message.caption}</b>', parse_mode='HTML')
                await message.answer(text=f'<b>✅ Сообщение было отправлено пользователю.</b>',
                                     parse_mode='HTML')
    elif chat != '':
        if message.photo == None:
            msg_to_db = message.text.strip().replace('\n', '')
            await rq.set_messages(tg_id=message.from_user.id, username=f'@{message.from_user.username}',
                                  message=msg_to_db,
                                  category=category_msg, msg_id=message.message_id)
            await message.bot.send_message(chat_id=chat, text=f'<b>🆕 Новая анкета!\n\n{message.text}\n\n🧾 Данные о пользователе: @{message.from_user.username}, ID: <code>{message.from_user.id}</code></b>', message_thread_id=int(thread), parse_mode='HTML', reply_markup=await kb.admin_msg(tg_id=message.from_user.id))
            await message.answer(text='<b>✅ Сообщение было отправлено администраторам Admin Bot.</b>', parse_mode='HTML', reply_markup=await kb.back())
        else:
            msg_to_db = message.caption.strip().replace('\n', '')
            await rq.set_messages(tg_id=message.from_user.id, username=f'@{message.from_user.username}',
                                  message=msg_to_db,
                                  category=category_msg, msg_id=message.message_id)
            await message.bot.send_photo(chat_id=chat, photo=message.photo[-1].file_id, caption=f'<b>🆕 Новая анкета!\n\n{message.caption}\n\n🧾 Данные о пользователе: @{message.from_user.username}, ID: <code>{message.from_user.id}</code></b>' ,message_thread_id=int(thread), parse_mode='HTML', reply_markup=await kb.admin_msg(tg_id=message.from_user.id))
            await message.answer(text='<b>✅ Сообщение было отправлено администраторам Admin Bot.</b>',
                                 parse_mode='HTML', reply_markup=await kb.back())



