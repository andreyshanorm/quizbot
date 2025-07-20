from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from db import get_quiz_index, update_quiz_index, save_user_result, show_user_statistics, create_user_name, get_top_rating
from quiz_data import get_question, new_quiz, quiz_data
from aiogram import F


dp = Dispatcher()  # Инициализация диспетчера для обработки входящих сообщений и событий

def create_buttons(builder):
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Показать статистику"))
    builder.add(types.KeyboardButton(text="Показать лидеров"))
    builder.add(types.KeyboardButton(text="Создать пользователя"))

def get_reply_keyboard() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    create_buttons(builder)  
    return builder.as_markup(resize_keyboard=True)

async def handle_answer(callback: types.CallbackQuery, is_correct: bool):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None 
    )
    
    current_question_index = await get_quiz_index(callback.from_user.id)
    if is_correct:
        await callback.message.answer("Верно!")
        await save_user_result(callback.from_user.id, current_question_index, correct=True)
    else:
        correct_option = quiz_data[current_question_index]['correct_option']
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
        await save_user_result(callback.from_user.id, current_question_index, correct=False)

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await finish_quiz(callback.message, callback.from_user.id)

@dp.callback_query(F.data == "right_answer") 
async def right_answer(callback: types.CallbackQuery):
    await handle_answer(callback, is_correct=True)

@dp.callback_query(F.data == "wrong_answer") 
async def wrong_answer(callback: types.CallbackQuery):
    await handle_answer(callback, is_correct=False) 

async def finish_quiz(message, user_id):
    await message.answer("Это был последний вопрос. Квиз завершен!", reply_markup=get_reply_keyboard())
    await show_user_statistics(user_id, message)

waiting_for_nickname = {} 

# Обработчик команды /create_user
@dp.message(F.text == "Создать пользователя") 
@dp.message(Command("create_user"))
async def cmd_create_user(message: types.Message):
    user_id = message.from_user.id
    waiting_for_nickname[user_id] = True
    await message.answer(
        "📝 Введите ваш никнейм:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.from_user.id in waiting_for_nickname)
async def process_nickname(message: types.Message):
    user_id = message.from_user.id
    nickname = message.text.strip()
    
    if len(nickname) < 3:
        await message.answer("❌ Никнейм слишком короткий (минимум 3 символа). Попробуйте снова:")
        return
    
    try:
        await create_user_name(user_id, nickname)
        await message.answer(f"✅ Пользователь {nickname} успешно создан!", reply_markup=get_reply_keyboard())
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
    finally:
        if user_id in waiting_for_nickname:
            del waiting_for_nickname[user_id]

@dp.message(F.text == "Начать игру") 
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@dp.message(Command("start")) 
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    create_buttons(builder)
    await message.answer(
        "Добро пожаловать в квиз!\n\n"
        "Перед началом игры вы должны создать пользователя:\n"
        "- /create_user — создать нового пользователя\n"
        "Вы можете:\n"
        "- Нажать «Начать игру», чтобы пройти викторину.\n"
        "- Нажать «Показать статистику», чтобы увидеть свои результаты.\n"
        "- Нажать «Показать лидеров», чтобы увидеть свои результаты.\n"
        "Также доступны команды:\n"
        "- /quiz — начать новую игру\n"
        "- /stats — показать статистику\n"
        "- /best - показать список лучших участников",
        reply_markup=builder.as_markup(resize_keyboard=True) 
    )

@dp.message(F.text == "Показать лидеров") 
@dp.message(Command("best"))
async def cmd_quiz(message: types.Message):
    best = await get_top_rating()
    if best == 0:
        await message.answer(f"В Квизе не поучаствовало еще ни одного игрока", reply_markup=get_reply_keyboard())
        return
    for index, item in enumerate(best):
        player_place = index + 1
        await message.answer(f"Место №{player_place} занимает {item[0]} со счетом {item[1]}", reply_markup=get_reply_keyboard())
        if index > 3:
            break
    
    

@dp.message(F.text == "Показать статистику")
@dp.message(Command("stats"))
async def cmd_show_stats(message: types.Message):
    user_id = message.from_user.id
    total, correct = await show_user_statistics(user_id, message)
    if total == 0:
        await message.answer("Вы еще не прошли ни одного вопроса викторины.", reply_markup=get_reply_keyboard())
    else:
        await message.answer(f"Вы ответили на {total} вопросов, из которых {correct} были правильными.", reply_markup=get_reply_keyboard())