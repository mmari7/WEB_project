import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Wish(SqlAlchemyBase):
    __tablename__ = 'wishes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    wishlist_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("wishlists.id"))

    wishlist = orm.relationship('Wishlist')


