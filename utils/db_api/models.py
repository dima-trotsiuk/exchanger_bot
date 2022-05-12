from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///sqlite3.db')
engine.connect()

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    chats = relationship("Chat")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author_id = Column(Integer, ForeignKey('groups.id'))


Base.metadata.create_all(engine)
