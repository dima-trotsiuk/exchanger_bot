from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///sqlite3.db?charset=utf8mb4')
engine.connect()

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)


class Chat(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    group = relationship("Group")


class Message_info(Base):
    __tablename__ = 'message_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    group = relationship("Group")
    created_on = Column(DateTime(), default=datetime.now)


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_info_id = Column(Integer, ForeignKey('messages.id', ondelete='CASCADE'))
    chat_id = Column(Integer, ForeignKey('chats.chat_id', ondelete='CASCADE'))
    message_id = Column(Integer, nullable=False)


Base.metadata.create_all(engine)
