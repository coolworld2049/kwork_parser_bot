import bcrypt
import sqlalchemy as sa

from kwork_parser_bot.db.base import Base


class KworkAccount(Base):
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    login = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    phone = sa.Column(sa.String, nullable=False)

    @staticmethod
    def get_hashed_password(plain_text_password):
        # Hash a password for the first time
        #   (Using bcrypt, the salt is saved into the hash itself)
        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    @staticmethod
    def check_password(plain_text_password, hashed_password):
        # Check hashed password. Using bcrypt, the salt is saved into the hash itself
        return bcrypt.checkpw(plain_text_password, hashed_password)
