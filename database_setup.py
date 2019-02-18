import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy import create_engine

Base = declarative_base()


# class to store user info
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))
    provider = Column(String(25))

    @property
    def serialize(self):
        # return book data in serializable format
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'image': self.image,
            'provider': self.provider,
        }


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


# class for Books Database
class BookDB(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    bookName = Column(String(250), nullable=False)
    authorName = Column(String(250), nullable=False)
    coverUrl = Column(String(450), nullable=False)
    description = Column(String(), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category = relationship(Category)

    @property
    def serialize(self):
        # return book data in serializable format
        return {
            'id': self.id,
            'name': self.bookName,
            'author': self.authorName,
            'genre': self.category_id,
            'coverUrl': self.coverUrl,
            'description': self.description,
            'creatorName': self.user.name,
            'creatorEmail': self.user.email
        }


engine = create_engine('sqlite:///BookCatalog.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
cat1 = Category(name='Fiction')
cat = session.query(Category).filter_by(name=cat1.name).first()
if not cat:
    session.add(cat1)
    cat2 = Category(name='Romance')
    cat3 = Category(name='Mystery')
    cat4 = Category(name='Fantasy')
    cat5 = Category(name='Horror')
    cat6 = Category(name='Other')
    session.add(cat2)
    session.add(cat3)
    session.add(cat4)
    session.add(cat5)
    session.add(cat6)

session.commit()
session.close()
