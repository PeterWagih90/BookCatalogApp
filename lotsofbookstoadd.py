# coding=utf-8
import zlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, BookDB, User

engine = create_engine('sqlite:///BookCatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="admin", email="peter.wagih90@gmail.com")
session.add(User1)
session.commit()

# Dummy books data

book1 = BookDB(
    bookName="The Hobbit",
    authorName="J. R. R. Tolkien",
    coverUrl="""https://images.gr-assets.com/books/1371834025l/17157681.jpg""",
    description="The classic fantasy novel of a time before the dominion of men,"
    "this book introduces the reader to Tolkien\'s world of hobbits, dwarves, goblins and "
    "wizards. The story takes the form of a quest as the hobbit Bilbo Baggins joins Gandalf "
    "the wizard.",
    category="Fiction",
    user_id=1)

session.add(book1)
session.commit()

book2 = BookDB(
    bookName="The Woman in the Window",
    authorName="A. J. Finn",
    coverUrl="""https://images.gr-assets.com/books/1528225499l/40389527.jpg""",
    description="Anna Fox spends her day drinking wine, watching old movies, and spying on her neighbors. "
    "But when she sees something she shouldn\'t, Anna's world begins to crumble.",
    category="Fiction",
    user_id=1)

session.add(book2)
session.commit()

book3 = BookDB(
    bookName="The Crystal Crypt: A Short Science Fiction Novel",
    authorName="Philip K. Dick",
    coverUrl="""https://images.gr-assets.com/books/1328314873l/6456323.jpg""",
    description="Stark terror ruled the Inner-Flight ship on that last Mars-Terra run. For the black-clad "
    "Leiters were on the prowl ... and the grim red planet was not far behind. First published"
    " in 1954.",
    category="Fiction",
    user_id=1)

session.add(book3)
session.commit()

book4 = BookDB(
    bookName="The Great Gatsby",
    authorName="F. Scott Fitzgerald",
    coverUrl="""https://images.gr-assets.com/books/1490528560l/4671.jpg""",
    description="THE GREAT GATSBY, F. Scott Fitzgerald\'s third book, stands as the supreme achievement of "
    "his career. This exemplary novel of the Jazz Age has been acclaimed by generations of "
    "readers. The story is of the fabulously wealthy Jay Gatsby and his new love for the "
    "beautiful Daisy Buchanan, of lavish parties on Long Island at a time when The New York "
    "Times noted gin was the national drink and sex the national obsession, "
    "it is an exquisitely crafted tale of America in the 1920s.",
    category="Fiction",
    user_id=1)

session.add(book4)
session.commit()

book5 = BookDB(
    bookName="The Fault in Our Stars",
    authorName="John Green",
    coverUrl="""https://images.gr-assets.com/books/1360206420l/11870085.jpg""",
    description="Despite the tumor-shrinking medical miracle that has bought her a few years, Hazel has "
    "never been anything but terminal, her final chapter inscribed upon diagnosis. But when a "
    "gorgeous plot twist named Augustus Waters suddenly appears at Cancer Kid Support Group, "
    "Hazel\'s story is about to be completely rewritten.",
    category="Romance",
    user_id=1)

session.add(book5)
session.commit()

book6 = BookDB(
    bookName="The Time Traveler\'s Wife",
    authorName="Audrey Niffenegger",
    coverUrl="""https://images.gr-assets.com/books/1380660571l/18619684.jpg""",
    description="A funny, often poignant tale of boy meets girl with a twist: what if one of them couldn\'t "
    "stop slipping in and out of time? Highly original and imaginative, this debut novel "
    "raises questions about life, love, and the effects of time on relationships.",
    category="Romance",
    user_id=1)

session.add(book6)
session.commit()

book7 = BookDB(
    bookName="Me Before You",
    authorName="Jojo Moyes",
    coverUrl="""https://images.gr-assets.com/books/1539892546l/17347634.jpg""",
    description="Louisa Clark is an ordinary young woman living an exceedingly ordinary life steady "
    "boyfriend, close family who has never been farther afield than their tiny village. She "
    "takes a badly needed job working for ex-Master of the Universe Will Traynor, "
    "who is wheelchair-bound after an accident.",
    category="Romance",
    user_id=1)

session.add(book7)
session.commit()

book8 = BookDB(
    bookName="The Girl with the Dragon Tattoo",
    authorName="Stieg Larsson,  Reg Keeland",
    coverUrl="""https://images.gr-assets.com/books/1327868566l/2429135.jpg""",
    description="Harriet Vanger disappeared thirty-six years ago on a Swedish island owned by her powerful "
    "family. But his uncle Henrik Vanger, a retired businessman, lives obsessed with solving "
    "the mystery before dying. On the walls of his studio hang forty-three dried and framed "
    "flowers.",
    category="Mystery",
    user_id=1)

session.add(book8)
session.commit()

book9 = BookDB(
    bookName="Angels & Demons",
    authorName="Dan Brown",
    coverUrl="""https://images.gr-assets.com/books/1527091700l/960.jpg""",
    description="An ancient secret brotherhood.A devastating new weapon of destruction.An unthinkable "
    "target...",
    category="Mystery",
    user_id=1)

session.add(book9)
session.commit()

book10 = BookDB(
    bookName="Harry Potter and the Sorcerer\'s Stone",
    authorName="J.K. Rowling",
    coverUrl="""https://images.gr-assets.com/books/1474154022l/3.jpg""",
    description="Harry Potter\'s life is miserable. His parents are dead and he\'s stuck with his heartless "
    "relatives, who force him to live in a tiny closet under the stairs. But his fortune "
    "changes when he receives a letter that tells him the truth about himself",
    category="Fantasy",
    user_id=1)

session.add(book10)
session.commit()

book11 = BookDB(
    bookName="A Game of Thrones",
    authorName="George R.R. Martin",
    coverUrl="""https://images.gr-assets.com/books/1436732693l/13496.jpg""",
    description="the first volume in George R. R. Martin\'s magnificent cycle of novels that includes A Clash of Kings and A Storm of Swords. As a whole, this series comprises a genuine masterpiece of modern fantasy",
    category="Fantasy",
    user_id=1)

session.add(book11)
session.commit()

print "added Books!"
