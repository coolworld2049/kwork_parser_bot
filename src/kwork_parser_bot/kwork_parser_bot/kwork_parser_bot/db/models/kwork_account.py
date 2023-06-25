import bcrypt
import sqlalchemy as sa

from kwork_parser_bot.db.base import Base, TimestampsMixin


class KworkAccount(Base, TimestampsMixin):
    id = sa.Column(
        sa.BigInteger, sa.Sequence("kwork_account_seq_id"), autoincrement=True
    )
    telegram_id = sa.Column(sa.ForeignKey("bot_user.id"), primary_key=True)
    login = sa.Column(sa.String, unique=True)
    password = sa.Column(sa.String)
    phone = sa.Column(sa.String)

    @staticmethod
    def get_hashed_password(plain_text_password):
        # Hash a password for the first time
        #   (Using bcrypt, the salt is saved into the hash itself)
        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    @staticmethod
    def check_password(plain_text_password, hashed_password):
        # Check hashed password. Using bcrypt, the salt is saved into the hash itself
        return bcrypt.checkpw(plain_text_password, hashed_password)
