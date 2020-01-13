from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ic_database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcategory.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = create_engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

print(" ------ showing user table: ")
# view user table
users = session.query(User).all()
for user in users:
    print ("User #" + str(user.id) + ": " + user.name + " email:" + user.email)

print(" ")
print(" ------ showing category table: ")
# view category table
categories = session.query(Category).all()
for category in categories:
    print ("Category #" + str(category.id) + ":\
           " + category.name + " accessed by " + str(category.user.name))

print(" ")
print(" ------ showing item table: ")
# view item table
items = session.query(Item).all()
for item in items:
    print ("Item #" + str(item.id) + ": " + item.name + " >>> "
           "Category #" + str(item.category_id) + ": " + item.category.name +
           " accessed by " + str(item.user.name))

print(" ")
print("Completed selecting data")
