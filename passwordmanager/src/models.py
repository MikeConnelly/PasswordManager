from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Account(Base):
    __tablename__ = 'account_table'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    email = Column('email', String)
    password = Column('password', String)
    url = Column('url', String)
    user_id = Column(Integer, ForeignKey('user_table.id'))


class User(Base):
    __tablename__ = 'user_table'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String, unique=True)
    master_password = Column('password', String)
    accounts = relationship('Account')
