from sqlalchemy import Integer, Column, String, SmallInteger
from sqlalchemy_mixins.serialize import SerializeMixin

from kwork_parser_bot.db import Base


class SubcategoryAction(Base, SerializeMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)
    description = Column(String)
    category_id = Column(SmallInteger)
    subcategory_id = Column(SmallInteger)
