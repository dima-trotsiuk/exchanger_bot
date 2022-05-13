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
    chats = relationship("Chat")


class Chat(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    title = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))


Base.metadata.create_all(engine)
