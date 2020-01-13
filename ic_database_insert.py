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

# data for user table
user_1 = User(name="Cathie", email="cathiecli@gmail.com")
session.add(user_1)
session.commit()

user_2 = User(name="John", email="cftpgroup16@gmail.com")
session.add(user_2)
session.commit()

print("-- user data inserted")

# data for category table
category_1 = Category(name="Geese", user=user_1)
session.add(category_1)
session.commit()

category_2 = Category(name="Swans", user=user_1)
session.add(category_2)
session.commit()

category_3 = Category(name="Ducks", user=user_1)
session.add(category_3)
session.commit()

category_4 = Category(name="Grouse", user=user_2)
session.add(category_4)
session.commit()

category_5 = Category(name="Turkey", user=user_2)
session.add(category_5)
session.commit()

category_6 = Category(name="Quail", user=user_2)
session.add(category_6)
session.commit()

print("-- category data inserted")

# data for item table
item_1 = Item(name="Pink-footed Goose",
              description="Casal European vag. to Northeast; usually seen "
                          "with other geese.",
              category=category_1,
              user=user_1)
session.add(item_1)
session.commit()

item_2 = Item(name="Emperor Goose",
              description="Largely coastal goose of w. AK; casual vag. "
                          "south to CA.",
              category=category_1,
              user=user_1)
session.add(item_2)
session.commit()

item_3 = Item(name="Snow Goose",
              description="Medium-sized moderately long-necked goose with a "
                          "fairly long thick-based bill",
              category=category_1,
              user=user_1)
session.add(item_3)
session.commit()

item_4 = Item(name="Mute Swan",
              description="European species introduced into NAM.",
              category=category_2,
              user=user_1)
session.add(item_4)
session.commit()

item_5 = Item(name="Trumpeter Swan",
              description="Very large, long-bodied, long-necked swan with a "
                          "short rounded tail.",
              category=category_2,
              user=user_1)
session.add(item_5)
session.commit()

item_6 = Item(name="Wood Duck",
              description="Medium-sized, thin-necked, short-legged, "
                          "short-billed duck.",
              category=category_3,
              user=user_1)
session.add(item_6)
session.commit()

item_7 = Item(name="Muscovy Duck",
              description="Native birds found only in s. TX; domestic birds "
                          "may be seen in park ponds across NAM.  Often "
                          "perches in trees.",
              category=category_3,
              user=user_1)
session.add(item_7)
session.commit()

item_8 = Item(name="Sooty Grouse",
              description="Large, heavy-bodied, long-tailed, and "
                          "long-necked grouse with a large deep-based bill.",
              category=category_4,
              user=user_2)
session.add(item_8)
session.commit()

item_9 = Item(name="Wild Turkey",
              description="Very large heave-bodied game bird with long "
                          "thick, legs, long tail and neck, and "
                          "proportionately very small head.",
              category=category_5,
              user=user_2)
session.add(item_9)
session.commit()

item_10 = Item(name="Mountain Quail",
               description="Relatively large short-tailed quail with "
                           "distinctive long straight head plumes and bushy "
                           "crest.",
               category=category_6,
               user=user_2)
session.add(item_10)
session.commit()

item_11 = Item(name="Scaled Quail",
               description="Medium-sized short-tailed quail with a "
                           "distinctive tufted crest.",
               category=category_6,
               user=user_2)
session.add(item_11)
session.commit()

print("-- item data inserted")
