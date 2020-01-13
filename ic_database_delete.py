from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ic_database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcategory.db', pool_pre_ping=True)
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

# delete specific record
# session.query(User).filter(User.name == 'Cathie').delete()

# delete all records
session.query(Item).delete()
session.commit()

session.query(Category).delete()
session.commit()

session.query(User).delete()
session.commit()

print("done deleting")
