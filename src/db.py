# -*- code: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('mysql://root:abc123456@192.168.192.122/aea?charset=utf8', echo=True)

db_session = scoped_session(sessionmaker(bind=engine)) 

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

