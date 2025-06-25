from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class QuestionsORM(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False, comment='Наименование вопроса')
    answer: Mapped[str] = mapped_column(Text,
                                        nullable=False,
                                        comment='Сопостовление вариантов с животными (кому начисляем баллы')


class ReviewORM(Base):
    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(Text, nullable=False, comment='Имя пользователя')
    review: Mapped[str] = mapped_column(Text, nullable=False, comment='Отзыв пользователя')
