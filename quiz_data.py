
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from db import update_quiz_index, get_quiz_index, start_new_quiz

quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        "question": "Что такое Git?",
        "options": [
            "Язык разметки",
            "Система контроля версий",
            "Протокол шифрования",
            "Библиотека Python"
        ],
        "correct_option": 1
    },
    {
        "question": "Какой оператор проверяет равенство по значению в JavaScript?",
        "options": [
            "=",
            "===",
            "==",
            "!="
        ],
        "correct_option": 2
    },
    {
        "question": "Что такое HTML?",
        "options": [
            "Язык программирования",
            "Графический редактор",
            "Протокол передачи данных",
            "Язык разметки веб-страниц"
        ],
        "correct_option": 3
    },
    {
        "question": "Для чего используется ключевое слово 'let' в JavaScript?",
        "options": [
            "Объявление константы",
            "Создание циклов",
            "Объявление блочной переменной",
            "Импорт модулей"
        ],
        "correct_option": 2
    },
    {
        "question": "Что такое CSS?",
        "options": [
            "Система управления базами данных",
            "Язык стилизации веб-страниц",
            "Язык программирования",
            "Фреймворк JavaScript"
        ],
        "correct_option": 1
    },
    {
        "question": "Какой тип данных изменяем в Python?",
        "options": [
            "Кортеж (tuple)",
            "Строка (string)",
            "Число (int)",
            "Список (list)"
        ],
        "correct_option": 3
    },
    {
        "question": "Что такое API?",
        "options": [
            "Автоматическая проверка интерфейса",
            "Интерфейс для взаимодействия программ",
            "Язык описания данных",
            "Протокол асинхронной передачи"
        ],
        "correct_option": 1
    },
    {
        "question": "Какой принцип ООП позволяет одним методом обрабатывать разные типы данных?",
        "options": [
            "Инкапсуляция",
            "Полиморфизм",
            "Композиция",
            "Наследование"
        ],
        "correct_option": 1
    },
    {
        "question": "Что выводит console.log(1 + '1') в JavaScript?",
        "options": [
            "2",
            "11",
            "Ошибку типа",
            "NaN"
        ],
        "correct_option": 1
    },
    {
        "question": "Для чего используется метод .append() в Python?",
        "options": [
            "Добавление элемента в конец списка",
            "Объединение строк",
            "Удаление последнего элемента",
            "Добавление ключа в словарь"
        ],
        "correct_option": 0
    }
]

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder() 
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer"
        ))
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    if current_question_index >= len(quiz_data):
        await finish_quiz(message)
        return
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await start_new_quiz(user_id)
    await get_question(message, user_id)

async def finish_quiz(message):
    await message.answer("Это был последний вопрос. Квиз завершен!")