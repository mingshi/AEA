# -*- code: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://root@192.168.1.59/oauth2', echo=False)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(30), nullable=False)
    email = Column('email', String(50), nullable=False)
    created_at = Column('created_at', DateTime, nullable=False)

    def __repr__(self):
        return "<User ('%s')>" % (self.name)

user_table = User.__table__

metadata = Base.metadata

def create_all():
    metadata.create_all(engine)


__all__ = ['engine', 'create_all', 'User']
