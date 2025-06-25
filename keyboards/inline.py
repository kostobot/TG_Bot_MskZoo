import json
from typing import Optional
from pydantic import Field
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import QuestionsORM


class MenuCallBack(CallbackData, prefix="menu"):
    menu_name: str = 'start_page'
    user_select: Optional[int] = Field(default=0)
    question_id: Optional[int] = 0


def get_user_main_btns():
    """
    Это кнопки для самой стартовой страницы
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Начать викторину 🦁": "quiz",
        "Узнать сразу 🐥": "program"
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()


def get_not_quiz_btns():
    """
    Кнопки, когда база была некорректно развернута и нет вопросов
    для викторины (модуль с викториной не работает)
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "В начало 🙂": "restart",
        "Узнать сразу 🐥": "program"
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()


def get_user_question_btns(question_id: int, question: QuestionsORM, menu_main: Optional[str] = None):
    """
    Кнопки - варианты ответов на вопрос (для викторины)
    :param question: вопрос из БД, которы нужно отобразить сейчас
    :param question_id: номер вопроса из спика, который нужно показать в следующий раз.
    Это index из листа в котором лежат id случайно выбранных вопросов
    :param menu_main: для навигации. Параметр, по которому определяется на какую страницу нужно перейти
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for i, k in enumerate(list(json.loads(question.answer).keys())):
        keyboard.add(InlineKeyboardButton(text=k,
                                          callback_data=MenuCallBack(user_select=i,
                                                                     menu_name=menu_main if menu_main else 'quiz',
                                                                     question_id=question_id + 1).pack()))

    return keyboard.adjust(1).as_markup()


def get_result_btns(result_quiz):
    """
    Кнопки - когда пользователю отображается результат пройденной викторины
    :param result_quiz: результат прохождения викторины
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Попробовать ещё раз? 🙂": "quiz",
        "Программа опеки 🦋": "program",
        "Оставить отзыв": "feedback",
        "Поделиться результатом": "send_result",
        "Связаться с сотрудником ☎": "manager_contact"
    }
    for text, menu_name in btns.items():
        if menu_name == 'send_result':
            keyboard.add(InlineKeyboardButton(text=text,
                                              switch_inline_query=f'\n{result_quiz}'))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(menu_name=menu_name).pack()))
    return keyboard.adjust(1).as_markup()


def get_program_btns():
    """
    Кнопки - когда пользователю отображается информация об опеки
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "В начало 🙂": "restart",
        "Оставить отзыв": "feedback",
        "Связаться с сотрудником ☎️": "manager_contact",
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()


def get_contacts_btns():
    """
    Кнопки - когда пользовать нажал "Связь с сотрудником"
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "В начало 🙂": "restart",
        "Оставить отзыв": "feedback",
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()
