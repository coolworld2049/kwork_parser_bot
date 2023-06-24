from typing import Any

import stringcase
from sqlalchemy import func, Column, TIMESTAMP
from sqlalchemy.orm import declared_attr, DeclarativeBase

from kwork_parser_bot.db.meta import meta


class TimestampsMixin:
    __abstract__ = True

    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"
    __datetime_func__ = func.now()

    created_at = Column(
        __created_at_name__,
        TIMESTAMP(timezone=True),
        default=__datetime_func__,
        nullable=True,
    )

    updated_at = Column(
        __updated_at_name__,
        TIMESTAMP(timezone=True),
        default=__datetime_func__,
        onupdate=__datetime_func__,
        nullable=True,
    )


class Base(DeclarativeBase):
    __abstract__ = True
    __name__: str
    id: Any
    metadata = meta

    @declared_attr
    def __tablename__(cls) -> str:
        return stringcase.snakecase(cls.__name__)
