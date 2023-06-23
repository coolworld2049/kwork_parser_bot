from typing import Any

import stringcase
from sqlalchemy.orm import DeclarativeBase, declared_attr

from kwork_parser_bot.db.meta import meta


class Base(DeclarativeBase):
    __abstract__ = True
    id: Any
    __name__: str
    metadata = meta

    @declared_attr
    def __tablename__(cls) -> str:
        return stringcase.snakecase(cls.__name__)
