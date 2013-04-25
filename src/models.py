# -*- code: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, FLOAT, TEXT, TIMESTAMP
from sqlalchemy.dialects.mysql import TINYINT
from db import Base
    
class Reimbursed(Base):
    __tablename__ = 'reimbursed'

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, nullable=False)
    status = Column('status', TINYINT, nullable=True)
    create_time = Column('create_time', Date, nullable=True)
    update_time = Column('update_time', DateTime, nullable=True)
    total_expense = Column('total_expense', FLOAT, nullable=False)

    def __repr__(self):
        return "<Reimbursed ('%s')>" % (self.id)

class Reimsub(Base):
    __tablename__ = 'reim_sub'

    subid = Column('subid', Integer, primary_key=True)
    id = Column('id', Integer, nullable=False)
    type_id = Column('type_id', Integer, nullable=False)
    expense = Column('expense', FLOAT, nullable=False)
    comment = Column('comment', TEXT, nullable=False)

    def __repr__(self):
        return "<Reimsub ('%s')>" % (self.subid)


class Reimtype(Base):
    __tablename__ = 'reim_type'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', String(40), nullable=False)

    def __repr__(self):
        return "<Reimtype ('%s')>" % (self.type)
    
class Approve(Base):
    __tablename__ = 'approve'

    id = Column('id', Integer, primary_key=True)
    reim_id = Column('reim_id', Integer, nullable=False)
    user_name = Column('user_name', String(40), nullable=False)
    user_ids = Column('user_ids', String(40), nullable=False)
    status = Column('status', Integer, nullable=True)
    flag = Column('flag', Integer, nullable=True)
    operator = Column('operator', Integer, nullable=True)
    comment = Column('comment', TEXT, nullable=True)
    update_time = Column('update_time', DateTime, nullable=True)
    def __repr__(self):
        return "<Approve ('%s','%s','%s','%s')>" % (self.id, self.reim_id, self.user_name, self.status)