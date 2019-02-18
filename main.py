#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookDB, User, Category
import random
import string
import httplib2
import json
import requests
# importing oauth

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# import logger
import logging

# Fix No handlers could be found for logger "sqlalchemy.pool.NullPool"
logging.basicConfig()

# app configuration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'itisasecret'
# npYA-61QzjPVLfBujMHlkxPY

# google client secret
secret_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = 'Book Catalog App'

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

engine = create_engine('sqlite:///BookCatalog.db')
Base.metadata.bind = engine


# for test only as flask using threads and sql won't
# execute database queries from other than created thread
# DBSession = sessionmaker(bind=engine)
# session = DBSession()
# .... do somthing
# session.commit() ##(insert,update,delete) should commit the change
# session.close() ## close session


# validating current loggedin user

def check_user():
    email = login_session['email']
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(email=email).one_or_none()
    session.close()
    return user


# retreive admin user details

def check_admin():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(
        email='peter.wagih90@gmail.com').one_or_none()
    session.close()
    return user


# Add new user into database

def createUser():
    if 'name' in login_session.keys():
        name = login_session['name']
    else:
        name = "No Name"

    email = login_session['email']

    if 'img' in login_session.keys():
        url = login_session['img']
    provider = login_session['provider']  # google only for now
    newUser = User(name=name, email=email, image=url, provider=provider)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add(newUser)
    session.commit()
    # always close session avoiding
    # thread changing between requests
    session.close()


def new_state():
    if 'state' in login_session.keys():
        state = login_session['state']
    else:
        state = ''.join(random.choice(string.ascii_uppercase +
                                      string.digits) for x in xrange(32))
        # print "new session created : %s " % state
        login_session['state'] = state

    return state


def queryAllBooks():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    books = session.query(BookDB).all()
    session.close()
    return books


def queryAllCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    session.close()
    return categories


def getCategorey(categorey_Id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categorey = session.query(Category).filter_by(id=categorey_Id).first()
    session.close()
    return categorey


def getCategoreyId(categorey_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categorey = session.query(Category).filter_by(name=categorey_name).first()
    session.close()
    return categorey


# App Routes

# main page

@app.route('/')
@app.route('/books/')
def showBooks():
    books = queryAllBooks()
    state = new_state()
    return render_template('main.html', books=books, currentPage='main',
                           state=state, login_session=login_session,
                           categories=queryAllCategories())


# To add new book

@app.route('/book/new/', methods=['GET', 'POST'])
def newBook():
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and \
                login_session['provider'] != 'null':
            bookName = request.form['bookName']
            bookAuthor = request.form['authorName']
            coverUrl = request.form['bookImage']
            description = request.form['bookDescription']
            description = description.replace('\n', '<br>')
            bookCategoryName = request.form['category']  # name
            # print bookCategoryName
            user_id = check_user().id

            if bookName and bookAuthor and coverUrl and description \
                    and bookCategoryName:
                newBookCat = getCategoreyId(bookCategoryName)
                newBook = BookDB(
                    bookName=bookName,
                    authorName=bookAuthor,
                    coverUrl=coverUrl,
                    description=description,
                    category_id=newBookCat.id,
                    user_id=user_id,
                )
                DBSession = sessionmaker(bind=engine)
                session = DBSession()
                session.add(newBook)
                session.commit()
                return redirect(url_for('showBooks'))
            else:

                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add New Book',
                    errorMsg='All Fields are Required!',
                    state=state,
                    login_session=login_session,
                )
        else:
            state = new_state()
            books = queryAllBooks()
            categories = queryAllCategories()
            return render_template(
                'main.html',
                categories=categories,
                books=books,
                currentPage='main',
                state=state,
                login_session=login_session,
                errorMsg='Please Login first to Add Book!',
            )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add New Book', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        books = queryAllBooks()
        categories = queryAllCategories()
        return render_template(
            'main.html',
            categories=categories,
            books=books,
            currentPage='main',
            state=state,
            login_session=login_session,
            errorMsg='Please Login first to Add Book!',
        )


# To show book of different category

@app.route('/books/category/<string:category>/')
def sortBooks(category):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    books = session.query(BookDB).filter_by(category_id=category).all()
    categories = queryAllCategories()
    session.close()

    state = new_state()
    return render_template(
        'main.html',
        categories=categories,
        books=books,
        currentPage='main',
        error='Sorry! No Book in Database With This Genre :(',
        state=state,
        login_session=login_session)


def populateHeadersinBase():
    cats = queryAllCategories()
    render_template('base.html', catList=cats)


# To show book detail

@app.route('/books/category/<int:category_id>/<int:bookId>/')
def bookDetail(category_id, bookId):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book = session.query(BookDB).filter_by(id=bookId,
                                           category_id=category_id).first()
    session.close()
    categories = queryAllCategories()
    state = new_state()
    if book:
        return render_template('itemDetail.html',
                               book=book,
                               currentPage='detail',
                               state=state,
                               login_session=login_session)
    else:
        return render_template('main.html',
                               categories=categories,
                               currentPage='main',
                               error="""No Book Found with this Category
                               and Book Id :(""",
                               state=state,
                               login_session=login_session)


# To edit book detail

@app.route('/books/category/<int:category_id>/<int:bookId>/edit/',
           methods=['GET', 'POST'])
def editBookDetails(category_id, bookId):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book = session.query(BookDB).filter_by(id=bookId,
                                           category_id=category_id).first()
    session.close()
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            bookName = request.form['bookName']
            bookAuthor = request.form['authorName']
            coverUrl = request.form['bookImage']
            description = request.form['bookDescription']

            bookCategoryName = request.form['category']  # name

            bookCategory = getCategoreyId(bookCategoryName)

            user_id = check_user().id
            admin = check_admin()
            admin_id = -1  # no admin inserted
            if admin is not None:
                admin_id = admin.id  # admin inserted we need to know id

            # check if book owner is same as logged in user or admin or not

            if book.user_id == user_id or user_id == admin_id:
                if bookName and bookAuthor and coverUrl and description \
                        and bookCategory:
                    book.bookName = bookName
                    book.authorName = bookAuthor
                    book.coverUrl = coverUrl
                    description = description.replace('\n', '<br>')
                    book.description = description
                    book.category_id = bookCategory.id
                    session.add(book)
                    session.commit()
                    return redirect(url_for('bookDetail',
                                            category_id=book.category_id,
                                            bookId=book.id))
                else:
                    state = new_state()
                    categories = queryAllCategories()
                    category = getCategorey(book.category_id)
                    return render_template(
                        'editItem.html',
                        bookCategory=category,
                        categories=categories,
                        currentPage='edit',
                        title='Edit Book Details',
                        book=book,
                        state=state,
                        login_session=login_session,
                        errorMsg='All Fields are Required!',
                    )
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    book=book,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit book Details!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                book=book,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Book Details!',
            )
    elif book:
        state = new_state()
        category = getCategorey(book.category_id)
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin = check_admin()
            admin_id = -1  # no admin inserted
            if admin is not None:
                admin_id = admin.id  # admin inserted we need to know id
            if user_id == book.user_id or user_id == admin_id:
                book.description = book.description.replace('<br>', '\n')
                categories = queryAllCategories()

                return render_template(
                    'editItem.html',
                    categories=categories,
                    bookCategory=category,
                    currentPage='edit',
                    title='Edit Book Details',
                    book=book,
                    state=state,
                    login_session=login_session,
                )
            else:
                return render_template(
                    'itemDetail.html',
                    book=book,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit book Details!')
        else:
            return render_template(
                'itemDetail.html',
                book=book,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Book Details!',
            )
    else:
        state = new_state()
        return render_template('main.html', currentPage='main',
                               error="""Error Editing Book! No Book Found
                               with this Category and Book Id :(""",
                               state=state,
                               login_session=login_session)


# To delete books

@app.route('/books/category/<int:category_id>/<int:bookId>/delete/')
def deleteBook(category_id, bookId):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book = session.query(BookDB).filter_by(category_id=category_id,
                                           id=bookId).first()
    session.close()
    state = new_state()
    if book:

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin = check_admin()
            admin_id = -1  # no admin inserted
            if admin is not None:
                admin_id = admin.id  # admin inserted we need to know id
            if user_id == book.user_id or user_id == admin_id:
                session.delete(book)
                session.commit()
                return redirect(url_for('showBooks'))
            else:
                return render_template(
                    'itemDetail.html',
                    book=book,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the Owner Can delete the book'
                )
        else:
            return render_template(
                'itemDetail.html',
                book=book,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Delete the Book!',
            )
    else:
        categories = queryAllCategories()
        return render_template('main.html',
                               categories=categories,
                               currentPage='main',
                               error="""Error Deleting Book! No Book Found
                               with this Category and Book Id :(""",
                               state=state,
                               login_session=login_session)


# ===================
# Google Signing
# ===================

# google signin function

@app.route('/gconnect', methods=['POST'])
def gConnect():
    # print "login session last "+login_session['state']
    # print "login request state "+request.args.get('state')
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        # Style done like that for PEP8
        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='https:'
                                                   '//www.googleapis.com/'
                                                   'auth/userinfo.profile '
                                                   'https:'
                                                   '//www.googleapis.com/'
                                                   'auth/userinfo.email'
                                                   ' openid')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            """Token's user ID does not
                            match given user ID."""),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    # print data

    # ADD PROVIDER TO LOGIN SESSION

    if 'name' not in data:
        login_session['name'] = 'No Name'
    else:
        login_session['name'] = data['name']

    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not check_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])


# logout user

@app.route('/logout', methods=['post'])
def logout():
    # Disconnect based on provider

    if login_session.get('provider') == 'google':
        return gdisconnect()
    else:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['access_token']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token
        del login_session['access_token']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


# ===================
# JSON Endpoints
# ===================

@app.route('/books.json/')
def booksJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    books = session.query(BookDB).all()
    session.close()
    return jsonify(Books=[book.serialize for book in books])


@app.route('/books/category/<int:category_id>.json/')
def bookCategoryJSON(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    books = session.query(BookDB).filter_by(category_id=category_id).all()
    session.close()
    return jsonify(Books=[book.serialize for book in books])


@app.route('/books/category/<int:category_id>/<int:bookId>.json/')
def bookJSON(category_id, bookId):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book = session.query(BookDB).filter_by(category_id=category_id,
                                           id=bookId).first()
    session.close()
    return jsonify(Book=book.serialize)


@app.route('/booksByCategories.json/')
def allBooksByCategoryJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        books = [
            i.serialize for i in session.query(BookDB).filter_by
            (category_id=category_dict[c]["id"]).all()
        ]
        if books:
            category_dict[c]["Books"] = books
        else:
            category_dict[c]["Books"] = []
    session.close()
    return jsonify(Category=category_dict)


@app.route('/catalog/categories.json/')
def categoriesJSON():
    return jsonify(categories=[cat.serialize for cat in queryAllCategories()])


if __name__ == '__main__':
    app.debug = True
    # app.run()
    # app.run(host='', port=5000)
    app.run(host='0.0.0.0', port=5000)
