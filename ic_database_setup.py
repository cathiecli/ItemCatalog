from sqlalchemy import Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'
    id = Column(Integer,
                Sequence('user_id_seq', start=1, increment=1),
                primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):

    __tablename__ = 'category'
    id = Column(Integer,
                Sequence('category_id_seq', start=1, increment=1),
                primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):

    __tablename__ = 'item'
    id = Column(Integer,
                Sequence('item_id_seq', start=1, increment=1),
                primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


engine = create_engine('sqlite:///itemcategory.db')

Base.metadata.create_all(engine)

print("Completed database setup")
