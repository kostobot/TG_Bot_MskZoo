import os
import random
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Bold, as_list, as_section
from keyboards.inline import *
from database.orm_requests import *


async def get_get_main_menu(full_name):
    """
    Контент для стартовой страницы
    :param full_name: имя пользователя, который написал боту
    :return:
    """
    text = f"Здравствуйте, {full_name} 🤗!\n Рады вас видеть! 🙂\n" \
        "Предлагаем вам пройти викторину \"Какое у вас тотемное животное\".\n" \
        "А потом узнать кое-что интересное и важное😉.\n\n" \
        "Ждём вас на финише!❤️"

    kbds = get_user_main_btns()
    image = None
    image_start_path = os.path.join(os.getcwd(), "keyboards/image_start.png")
    if os.path.exists(image_start_path):
        with open(image_start_path, "rb") as image_from_buffer:
            image = BufferedInputFile(image_from_buffer.read(),
                                      filename="image_start.png")

    return text, kbds, image


async def questions_page(session: AsyncSession, question_id, state=None):
    """
    Модуль викторины.
    :param session:
    :param question_id: index из листа questions_id, который отображали в прошлый раз
    :param state:
    :return:
    """
    data = await state.get_data()
    questions_id = data.get('questions_id')

    if not questions_id:
        all_questions = await get_questions(session)
        if not all_questions:
            text = 'Модуль с викториной временно не работает. Ведуться работы по его улучшению. 🙂\n'
            kbds = get_not_quiz_btns()
            return text, kbds

        if all_questions.__len__() == int(os.getenv('COL_QUESTIONS')) or \
                all_questions.__len__() < int(os.getenv('COL_QUESTIONS')):
            questions = all_questions
        else:
            questions = random.sample(all_questions, int(os.getenv('COL_QUESTIONS')))

        questions_id = [q.id for q in questions]
        await state.set_data({'weights': {}, 'questions_id': questions_id})

    question = await get_question(session, questions_id[question_id])
    text = f'{question_id + 1}/{os.getenv("COL_QUESTIONS")} {question.question}'
    menu_main = None

    if question_id + 1 == int(os.getenv('COL_QUESTIONS')):
        menu_main = 'show_result'

    kbds = get_user_question_btns(question_id=question_id,
                                  question=question,
                                  menu_main=menu_main)

    return text, kbds


async def plus_points(state: FSMContext, session: AsyncSession, user_select: int, question_id: int = 0):
    """
    Метод запоминает баллы текущей викторины
    :param state:
    :param session:
    :param user_select: Какой вариант выбрал пользователь
    :param question_id: Текущий id вопроса из БД, который был выбран для викторины
    :return:
    """
    data = await state.get_data()
    questions_id = data.get('questions_id')
    if questions_id:
        question = await get_question(session, questions_id[question_id - 1])
        answer = list(json.loads(question.answer).values())[user_select]
        for v in answer:
            if not v in data['weights']:
                data['weights'][v] = 1
            else:
                data['weights'][v] += 1

        await state.update_data({'weights': data['weights']})


async def show_result(state: FSMContext):
    """
    Контент для страницы с отображением результата
    :param state:
    :return:
    """
    data = await state.get_data()
    max_value, result = 0, ''
    for k, v in data['weights'].items():
        if max_value < v:
            max_value, result = v, k

    path_file, image = None, None
    text = f'Твоё тотемное животное: "{result}"\nПосмотри какой хорошенький зверёк!😊'
    dir_foto = os.path.join(os.getcwd(), f"modul_quiz/foto")
    for _f in os.listdir(dir_foto):
        if _f.lower().strip().__contains__(result.lower().strip()):
            path_file = os.path.join(dir_foto, _f)
            break
    if path_file:
        with open(path_file, "rb") as image_from_buffer:
            image = BufferedInputFile(image_from_buffer.read(), filename=f"{result}")

    kbds = get_result_btns(result_quiz=text)

    return text, kbds, image


async def program():
    """
    О програме опеки
    :return:
    """
    text = as_list(
        as_section(Bold("Возьмите животное под опеку!")),
        as_section("Опека над животным из Московского зоопарка помогает сохранить биоразнообразия "
                   f"Земли и, конечно,", (Bold("это реальная помощь животным Московского зоопарка!")),
                   "\nБлагодаря вам мы можем улучшить условия содержания наших обитателей. 🦊"),
        as_section("Участвуйте в жизни Московского зоопарка, почувствуйте причастность к делу сохранения природы. 🌳",
                   "Станьте опекуном и поделитесь любовью и заботой со своим подопечным.\n"),
        as_section(f"Опекать – значит помогать любимым животным ❤️."))

    kbds = get_program_btns()

    return text, kbds


async def contacts():
    """
    Для страницы с контактной информацией о менеджере
    :return:
    """
    text = f'Чтобы узнать больше о программе опекунства, ' \
           'Вы можете связаться с нашим сотрудником: \n\n' \
           f'  👤  {os.getenv("MANAGER_NAME")}\n' \
           f'  📩  E-mail: {os.getenv("MANAGER_EMAIL")}\n' \
           f'  ☎  Телефон: {os.getenv("MANAGER_PHONE")}'

    kbds = get_contacts_btns()
    return text, kbds
