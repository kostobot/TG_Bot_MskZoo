import json
import logging
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import F, Bot
from aiogram import Router, types
from database.orm_requests import *
from database.models import QuestionsORM

admin_router = Router()


class Requests(StatesGroup):
    delete_question = State()
    get_name_question = State()
    get_answer_question = State()
    add_question = State()
    get_id_question = State()


@admin_router.message(Command("admin"))
async def command_admin_handler(message: Message, bot: Bot):
    """
    Обработчик команды /admin
    :param message:
    :param command:
    :param state:
    :return:
    """
    if not str(message.chat.id) in bot.admin_user:
        return

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Получить список всех вопросов'))
    builder.add(types.KeyboardButton(text='Удалить вопрос'))
    builder.add(types.KeyboardButton(text='Добавить вопрос'))
    builder.add(types.KeyboardButton(text='Показать отзывы'))
    builder.add(types.KeyboardButton(text='Получить информацию о вопросе'))
    builder.adjust(1)

    await message.answer(f"Что вы хотите сделать?", reply_markup=builder.as_markup(resize_keyboard=True))


@admin_router.message(F.text.lower() == "получить список всех вопросов")
async def text_questions(message: types.Message, bot: Bot, session: AsyncSession):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    questions = await get_questions(session)
    text = 'id - question\n-----------------\n'
    text += '\n'.join([f'{question.id} - {question.question}' for question in questions])
    await message.answer(text)


@admin_router.message(F.text.lower() == "удалить вопрос")
async def get_id_question_for_delete(message: types.Message, state: FSMContext, bot: Bot):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        await state.clear()
        return

    await message.answer(f'Введите id вопроса, который хотите удалить:')
    await state.set_state(Requests.delete_question.state)


@admin_router.message(Requests.delete_question)
async def delete_info_question(message: types.Message, session: AsyncSession, state: FSMContext):
    id_question = message.text.lower().strip()
    try:
        await delete_question(session=session, id_question=id_question)
    except Exception as e:
        logging.exception(e)
        await message.answer(f'Ошибка: Вопрос не удален.\nНе существует записи в базе с id = "{id_question}"')
    else:
        await message.answer(f'Вопрос id = "{id_question}" удален из БД')
        await state.clear()


@admin_router.message(F.text.lower() == "добавить вопрос")
async def get_name_question_for_add(message: types.Message, bot: Bot, state: FSMContext):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    await message.answer('Введите наименование вопроса:')
    await state.set_state(Requests.get_name_question.state)


@admin_router.message(Requests.get_name_question)
async def get_button_question_for_add(message: types.Message, state: FSMContext):
    await state.set_data({'name_question': message.text})
    await message.answer('Введите варианты ответов через запятую.\n'
                         'Например:')
    await message.answer('Красный, Синий, Зеленый')
    await state.set_state(Requests.get_answer_question.state)


@admin_router.message(Requests.get_answer_question)
async def get_answer_question_for_add(message: types.Message, state: FSMContext):
    await state.update_data({'list_answer': message.text})
    await message.answer('Введите варианты ответов через запятую. Сохраните порядок ответов '
                         'с ранее введенными вариантами ответов\n'
                         'Пример:')
    await message.answer('["Енот", "Мохноногий сыч"], ["Песец", "Питон тигровый"], ["Песец", "Фенек"]')
    await state.set_state(Requests.add_question.state)


@admin_router.message(Requests.add_question)
async def add_question(message: types.Message, session: AsyncSession, state: FSMContext):
    """
    Добавление вопроса в базу
    Пример формата:
     {
      "question": "Какой из этих цветов ты предпочитаешь?",
      "answer": {
        "Красный": ["Нильский крылан", "Питон тигровый"],
        "Синий": ["Квакша дальневосточная"],
        "Зеленый": ["Белогрудый ёж", "Попугай благородный", "Фенек"],
        "Желтый": ["Енот", "Мохноногий сыч", "Песец", "Попугай благородный"]
      }
    }
    :param session:
    :return:
    """
    data = await state.get_data()
    question = data['name_question']

    try:
        name_button = data['list_answer'].strip().split(',')
        value_button = json.loads(f'[{message.text.strip()}]')
        answer = {b: v for b, v in zip(name_button, value_button)}
    except Exception as e:
        logging.exception(e)
        logging.warning(f'Введено некорректное значение: "{message.text}"')
        await message.answer(f'Ошибка: Вопрос в базу не добавлен. Введены некорректные значения.')
    else:
        await insert_one(session=session,
                         data=QuestionsORM(question=question,
                                           answer=json.dumps(answer, ensure_ascii=False)))
        await message.answer(f'Вопрос "{question}" добавлен в базу данных')

    await state.clear()


@admin_router.message(F.text.lower() == "показать отзывы")
async def show_reviews(message: types.Message, session: AsyncSession, bot: Bot):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    user_reviews = await get_review(session)
    if user_reviews:
        text = '\n'.join([f'Пользователь: "{review.user}"\nОтзыв: {review.review}' for review in user_reviews])
        await message.answer(f'Последние 10 отзывов:\n{text}')
    else:
        await message.answer(f'Отзывов пока нет')


@admin_router.message(F.text.lower() == "получить информацию о вопросе")
async def details_question(message: types.Message, bot: Bot, state: FSMContext):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    await message.answer(f'Введите id вопроса:')
    await state.set_state(Requests.get_id_question.state)


@admin_router.message(Requests.get_id_question)
async def show_question_by_id(message: types.Message, session: AsyncSession, state: FSMContext):
    id_question = message.text.strip()
    try:
        question = await get_question(session=session, id_question=id_question)
    except Exception as e:
        logging.exception(e)
        await message.answer(f'Ошибка: Вопрос викторины с id "{id_question}" не найден. Пожалуйста, укажите верный id.')
    else:
        answer = '\n'.join([f'"{k}" - {",".join(v)}' for k, v in json.loads(question.answer).items()])
        await message.answer(f'Информация о вопросе с id "{id_question}":\n'
                             f'Наименование:\n{question.question}\n'
                             f'Варианты ответов:\n'
                             f'{answer}')
        await state.clear()
