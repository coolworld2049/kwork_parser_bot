import sqlalchemy as sa

from kwork_parser_bot.db.base import Base, TimestampsMixin


class BotUser(Base, TimestampsMixin):
    id = sa.Column(sa.BigInteger, primary_key=True)
    is_bot = sa.Column(sa.Boolean, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String)
    username = sa.Column(sa.String)
    language_code = sa.Column(sa.String)
    is_premium = sa.Column(sa.Boolean, default=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
