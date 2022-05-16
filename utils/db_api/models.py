from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
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
    chat_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    title = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group")


class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group")
    chat = relationship("Chat")


Base.metadata.create_all(engine)
