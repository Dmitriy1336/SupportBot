import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from config_reader import config
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import F
CHAT_ID = '-1002139283078'
form_thread = ''
class Check(StatesGroup):
    form = State()
    agree = State()


bot = Bot(token=config.bot_token.get_secret_value())

# Анкеты




# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Для новых администраторов")],
        [types.KeyboardButton(text="Проверка кандидатов")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
        input_field_placeholder="Выберите интересующий вас раздел..")
    await message.answer(f"Приветствую! Выбери раздел.", reply_markup=keyboard)


@dp.message(F.text.lower() == "для новых администраторов")
async def new_adm(message: types.Message, state: FSMContext):
    await state.set_state(Check.form)
    await message.reply(f"Отлично, необходимо заполнить форму ниже.\n\n"
                        f"1. Ваше имя:\n2. Ваш игровой NickName:\n3. Ваша электронная почта (gmail): \n4. Ваша ссылка на Форумный Аккаунт: \n5. Ваша ссылка на профиль VK (укажите оригинальный id цифрами, сайт в помощь - https://regvk.com/id/): \n6. Есть-ли доступ к ПК? (да или нет): \n7. Discord ID. Получить его можно включив режим разработчика в настройках. (пример: 947864954457956413):\n8. Ваш часовой пояс (от МСК): \n9. Ваш реальный возраст: \n10. Дата рождения (для ведения таблицы возрастов):\n11. Ссылка на телеграмм (пример: https://t.me/young_keef):")



@dp.message(F.text.lower() == "проверка кандидатов")
async def checking(message: types.Message, state: FSMContext):

    await state.set_state(Check.form)
    await message.reply(f"Отлично, необходимо заполнить форму ниже.\n\n"
                        f"1. Nick_Name:\n2. Ссылка на ВК (ID):\n3. Ссылка на ФА:\n4. Что нужно проверить:")

@dp.message(Check.form)
async def agree(message: types.Message, state: FSMContext):
    await state.update_data(form=message.text)
    await state.set_state(Check.agree)
    kb = [
        [types.KeyboardButton(text="Отправить")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Заполните анкету..")
    await message.answer('Перепроверьте введенные данные. \n\nЖелаете отправить анкету?', reply_markup=keyboard)



@dp.message(Check.agree)
async def send_form(message: types.Message, state: FSMContext):
    if message.text.lower() != 'отправить':
        await message.answer('Я вас не понял, начните заново.', reply_markup=types.ReplyKeyboardRemove())
    else:
        data = await state.get_data()
        if data['form'] != '':
            await bot.send_message(CHAT_ID, '@young_keef, новая форма!\n\n' + f'{data['form']}\n\n' + 'Связь с пользователем: ' + '@' + message.from_user.username)
        await message.answer(f'Форма была отправлена. Ваша анкета:\n\n{data['form']}', reply_markup=types.ReplyKeyboardRemove())
        await state.clear()



# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())