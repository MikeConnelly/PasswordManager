from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Account(Base):
    """database model for account table"""
    __tablename__ = 'account_table'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    email = Column('email', String)
    password = Column('password', String)
    url = Column('url', String)
    expansion = Column('expansion', String)
    extras = Column('extras', String)
    user_id = Column(Integer, ForeignKey('user_table.id'))


class User(Base):
    """database model for user table"""
    __tablename__ = 'user_table'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String, unique=True)
    master_password = Column('password', String)
    accounts = relationship('Account')
    custom_cols = Column('custom_cols', String)
