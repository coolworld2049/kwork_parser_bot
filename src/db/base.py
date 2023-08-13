from typing import Any

import sqlalchemy as sa
import stringcase
from sqlalchemy.orm import DeclarativeBase, declared_attr

from db.meta import meta


class Base(DeclarativeBase):
    __abstract__ = True
    id: Any
    __name__: str
    metadata = meta

    @declared_attr
    def __tablename__(cls) -> str:
        return stringcase.snakecase(cls.__name__)


class TimestampsMixin:
    __abstract__ = True

    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"
    __datetime_func__ = sa.func.now()

    created_at = sa.Column(
        __created_at_name__,
        sa.TIMESTAMP(timezone=True),
        default=__datetime_func__,
        nullable=True,
    )

    updated_at = sa.Column(
        __updated_at_name__,
        sa.TIMESTAMP(timezone=True),
        default=__datetime_func__,
        onupdate=__datetime_func__,
        nullable=True,
    )
