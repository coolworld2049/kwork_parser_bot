from typing import Any

import stringcase
from sqlalchemy.orm import declared_attr
from sqlalchemy_mixins.serialize import SerializeMixin

from kwork_parser_bot.db.meta import meta


class Base(SerializeMixin):
    __abstract__ = True
    __name__: str
    id: Any
    metadata = meta

    @declared_attr
    def __tablename__(cls) -> str:
        return stringcase.snakecase(cls.__name__)
