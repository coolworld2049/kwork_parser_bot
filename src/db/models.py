from sqlalchemy import Column, Integer, String, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from db import Base
from db.base import TimestampsMixin


class BotUser(Base, TimestampsMixin):
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    language_code = Column(String)


class Blacklist(Base):
    telegram_user_id = Column(Integer, primary_key=True)
    usernames = Column(JSON, nullable=True, default=[])


class KworkActor(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    kwork_account_id = Column(Integer, ForeignKey("kwork_account.id"))
    kwork_account = relationship("KworkAccount", back_populates="actor")


class KworkAccount(Base):
    telegram_user_id = Column(Integer, primary_key=True)
    login = Column(String, index=True, nullable=True)
    password = Column(String, index=True, nullable=True)
    phone = Column(String, index=True, nullable=True)
    actor = relationship("KworkActor", uselist=False, back_populates="kwork_account")
