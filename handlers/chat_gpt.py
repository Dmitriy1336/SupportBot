import string
import numpy as np
import spacy
from aiogram import Router, F
from sentence_transformers import SentenceTransformer, util
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, InlineKeyboardButton
# Инициализация логирования
logging.basicConfig(level=logging.INFO)

router = Router()

class ChatGPT(StatesGroup):
    Set_Chat_GPT = State()

# Глобальные переменные для хранения ответов и эмбеддингов
original_answers = []
answer_embeddings = []

MAX_MESSAGE_LENGTH = 4096


# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

# Создание пула потоков для выполнения синхронных функций асинхронно
executor = ThreadPoolExecutor()

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def count_word_matches(query, response):
    query_words = set(query.split())
    response_words = set(response.split())
    return len(query_words.intersection(response_words))

def split_message(message):
    """Разбивает длинное сообщение на части, не превышающие максимальную длину"""
    return [message[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]

def preprocess_text_spacy(text):
    try:
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        doc = nlp(text)
        words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        processed_text = ' '.join(words)
        return processed_text
    except Exception as e:
        logging.error(f"Ошибка при предобработке текста: {e}")
        return text  # Возвращаем исходный текст в случае ошибки

async def preprocess_text_spacy_async(text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, preprocess_text_spacy, text)

def read_data_with_embeddings(file_path, model, batch_size=10):
    try:
        if not os.path.exists(file_path):
            logging.error(f"Файл не найден: {file_path}")
            return [], np.array([])

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        logging.info(f"Количество строк в файле: {len(lines)}")

        original_answers = []
        all_embeddings = []

        for i in range(0, len(lines), batch_size):
            batch_lines = lines[i:i + batch_size]
            batch_answers = [line.strip() for line in batch_lines]
            logging.info(f"Количество ответов в текущей партии: {len(batch_answers)}")

            if len(batch_answers) > 0:
                batch_embeddings = model.encode(batch_answers, convert_to_tensor=False)
                logging.info(f"Размеры эмбеддингов текущей партии: {len(batch_embeddings)}")

                original_answers.extend(batch_answers)
                all_embeddings.append(batch_embeddings)
            else:
                logging.warning(f"Пустая партия при индексах {i} - {i + batch_size}")

        if all_embeddings:
            all_embeddings = np.vstack(all_embeddings)
            logging.info(f"Общее количество ответов: {len(original_answers)}")
            logging.info(f"Размеры всех эмбеддингов: {all_embeddings.shape}")
        else:
            logging.error("Ошибка: не удалось создать эмбеддинги.")

        return original_answers, all_embeddings
    except Exception as e:
        logging.error(f"Ошибка при чтении данных или вычислении эмбеддингов: {e}")
        return [], np.array([])

async def read_data_with_embeddings_async(file_path, model, batch_size=10):
    loop = asyncio.get_event_loop()
    original_answers, all_embeddings = await loop.run_in_executor(executor, read_data_with_embeddings, file_path, model, batch_size)

    if len(original_answers) == 0 or all_embeddings.size == 0:
        logging.error("Ошибка: эмбеддинги не загружены или пусты. В read_data_with_embeddings_async")
    else:
        logging.info(f"Успешно загружено {len(original_answers)} ответов и эмбеддингов размером {all_embeddings.shape}.")

    return original_answers, all_embeddings

async def on_startup():
    global original_answers, answer_embeddings
    logging.info("on_startup вызывается...")
    try:
        original_answers, answer_embeddings = await read_data_with_embeddings_async('data.txt', model)
        if len(original_answers) == 0 or answer_embeddings.size == 0:
            logging.error("Ошибка при загрузке данных и эмбеддингов на старте.")
        else:
            logging.info(f"Загружено {len(original_answers)} ответов и эмбеддингов размером {answer_embeddings.shape}.")
        return original_answers, answer_embeddings
    except Exception as e:
        logging.error(f"Ошибка в on_startup: {e}")
        return [], np.array([])

async def get_bot_response(user_input, response_history, original_answers, answer_embeddings):
    processed_input = await preprocess_text_spacy_async(user_input)
    if not processed_input.strip():
        return "Извините, я не понимаю ваш запрос."

    try:
        user_embedding = model.encode(processed_input, convert_to_tensor=False)

        if isinstance(answer_embeddings, list):
            answer_embeddings = np.array(answer_embeddings)

        if answer_embeddings.size == 0:
            logging.error("Ошибка: эмбеддинги не загружены или пусты.")
            return "Ошибка: эмбеддинги не загружены или пусты."

        if user_embedding.shape[0] != answer_embeddings.shape[1]:
            logging.error(f"Ошибка: размеры эмбеддингов не совпадают. user_embedding.shape: {user_embedding.shape}, answer_embeddings.shape: {answer_embeddings.shape}")
            return "Ошибка: размеры эмбеддингов не совпадают."

        similarities = util.cos_sim(user_embedding, answer_embeddings)[0]

        sorted_indices = np.argsort(-similarities)

        best_match_score = -1
        best_match_response = None

        for idx in sorted_indices:
            response = original_answers[idx]
            if not response_history or response != response_history[-1]:
                word_matches = count_word_matches(processed_input, await preprocess_text_spacy_async(response))
                if word_matches > 0:
                    current_score = similarities[idx] + word_matches * 0.1
                    if current_score > best_match_score:
                        best_match_score = current_score
                        best_match_response = response

        if best_match_response:
            if len(best_match_response) > MAX_MESSAGE_LENGTH:
                logging.info(f"Сообщение слишком длинное, длина: {len(best_match_response)}")
                return split_message(best_match_response)
            return best_match_response

        return "Извините, я не нашел подходящего ответа. Можете попробовать переформулировать ваш запрос."
    except Exception as e:
        logging.error(f"Ошибка при вычислении похожести или выборе ответа: {e}")
        return "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз."

@router.callback_query(F.data == 'chat_gpt')
async def get_chat_gpt(callback: CallbackQuery, state: FSMContext):
    kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='to_main')) # Добавление кнопки "назад"
    await state.set_state(ChatGPT.Set_Chat_GPT)
    await callback.message.edit_text(text='<b>🌟 Добро пожаловать! Здесь вы можете пообщаться с AI-помощником Максимом.\n\n'
                                          '📚 На данный момент Максим знает все о регламенте проекта и может дать точный ответ на ваш вопрос!\n\n'
                                          '❗️ Максим дает точную информацию только тогда, когда вы ясно изложили свою мысль!\n\n'
                                          '🏓 Для выхода из диалога напишите в чат слово "exit".\n\n'
                                          '⚡️ Будущее уже здесь - на BLACK RUSSIA!</b>', parse_mode='HTML', reply_markup=kb_back.as_markup())
    await callback.answer()

@router.message(ChatGPT.Set_Chat_GPT)
async def start_gpt(message: Message, state: FSMContext):
    try:
        if message.text.lower() == 'exit':
            kb_back = InlineKeyboardBuilder()  # Создание клавиатуры
            kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='to_main'))  # Добавление кнопки "назад"
            await message.reply("<b>Было приятно с вами пообщаться. До новых встреч!</b>", parse_mode='HTML', reply_markup=kb_back.as_markup())
            await state.clear()
            return

        response_history = []

        try:
            global original_answers, answer_embeddings
            response = await get_bot_response(message.text, response_history, original_answers, answer_embeddings)
            response_history.append(response)
            for part in split_message(response):
                await message.reply(f'<b>{part}</b>', parse_mode='HTML')
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}")
    except Exception as e:
        logging.error(f'Ошибка в обработчике сообщений: {e}')