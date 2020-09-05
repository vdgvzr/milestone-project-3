# Import installed libraries and dependencies to the Python file.
import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    session,
    flash
)
from flask_paginate import (
    Pagination,
    get_page_parameter
)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

load_dotenv()

# Define the app here
app = Flask(__name__)

'''Set the MONGO_URI and SECRET_KEY environment
variables which are stored in the .env file.
This file is ignored from repository by the
.gitignore file.'''
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

# Set database variable
mongo = PyMongo(app)


'''Here, the app's various paths are listed,
allowing the user to perform CRUD (Create, Read,
Update and Delete) operations on the collection data,
thus rendering the templates for the app's pages.'''


'''Templates'''


@app.route('/')
def home():
    '''It is not normally best practice to query the
    satabase multiple times, however it has been necessary for
    the development of this project'''

    # Limits the highest rated books to 10
    books = mongo.db.books.find().limit(10)

    # Sorts documents in descending order and limits to 6
    recents = mongo.db.books.find().sort('_id', -1).limit(6)

    quotes = mongo.db.books.find()
    genre = mongo.db.genre.find()
    return render_template(
        'index.html',
        books=books,
        recents=recents,
        quotes=quotes,
        genre=genre
    )


@app.route('/all_books')
def all_books():
    search = False
    x = request.args.get('x')
    if x:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)
    books = mongo.db.books.find()
    pagination = Pagination(
        page=page,
        total=books.count(),
        search=search,
        record_name=books
    )

    return render_template(
        'all-books.html',
        books=books,
        pagination=pagination
    )


@app.route('/book_review/<book_id>', methods=['GET'])
def book_review(book_id):
    # Declare empty string to be used for average rating
    rating_list = []

    # Find reviews based on book id
    get_review = mongo.db.review.find({'book_id': book_id})

    # Iterates through review rating values and appends to string as integer
    for i in get_review:
        rating_list.append(int(i['rating']))

    try:
        # If reviews exist, calculate average rating to 1 decimal place
        avg_rating = format(sum(rating_list)/len(rating_list), '.1f')
    except ZeroDivisionError:
        # Else, set the value to 0 as a string
        avg_rating = '0'

    # Declare page variables
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    reviews = mongo.db.review.find({'book_id': book_id})
    no_of_docs = mongo.db.review.count_documents({'book_id': book_id})
    # Set avergage rating field with whatever is returned
    mongo.db.books.update(
        {'_id': ObjectId(book_id)},
        {'$set': {'rating': avg_rating}}
    )
    return render_template(
        'book-review.html',
        book=the_book,
        recent=the_book,
        genre=all_genre,
        review=reviews,
        average=avg_rating,
        review_amount=no_of_docs
    )


@app.route('/genre_list')
def genre_list():
    # Returns the fill list of genres from mongo collection
    return render_template('genres.html', genre=mongo.db.genre.find())


@app.route('/genre/<genre_id>')
def genre(genre_id):
    search = False
    x = request.args.get('x')
    if x:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)
    books = mongo.db.books.find()
    pagination = Pagination(
        page=page,
        total=books.count(),
        search=search,
        record_name=books
    )

    the_genre = mongo.db.genre.find_one({'_id': ObjectId(genre_id)})
    return render_template(
        'genre.html',
        books=books,
        genre=the_genre,
        pagination=pagination
    )


@app.route('/search_books')
def search_books():
    '''Search through the database for book title,
    or book author using the $regex method. If nothing is
    found, search-results.html will display a page with a
    suggestion to add a book(only for the session user)'''
    query = request.args.get('search')
    query = query.title()

    search_value = mongo.db.books.find({
        '$or': [
            {'book_title': {'$regex': query}},
            {'book_author': {'$regex': query}}
        ]
    })
    no_of_docs = mongo.db.books.count_documents({
        '$or': [
            {'book_title': {'$regex': query}},
            {'book_author': {'$regex': query}}
        ]
    })
    return render_template(
        'search-results.html',
        search=search_value,
        query=query,
        no_of_docs=no_of_docs,
    )


'''User CRUD'''


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Checks to see if the user already exists
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            # If the user exists, flash message
            flash('Username already exists')
            return redirect(url_for('register'))

        # Else, post the new user's data to mongo
        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password'))
        }
        mongo.db.users.insert_one(register)

        session['user'] = request.form.get('username').lower()
        flash('Registration Successful!')
        return redirect(url_for('profile', username=session['user']))

    return render_template('register.html')


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    # Upon successful login, render profile page
    username = mongo.db.users.find_one(
        {'username': session['user']})['username']
    return render_template('profile.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Checks to see if the user exist to proceed with login
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            # Validates the user's password hash
            if check_password_hash(
                existing_user['password'],
                request.form.get('password')
            ):
                session['user'] = request.form.get('username').lower()
                flash('Welcome, {}!'.format(request.form.get('username')))
                return redirect(url_for('profile', username=session['user']))
            else:
                '''If the user isn't found, flashed message as
                a security precaution against brute force hacking
                attempts.'''
                flash('Incorrect Username and/or Password')
                return redirect(url_for('login'))

        else:
            '''If neither username nor password can be validated
            then flash this message and return to login page'''
            flash("Incorrect Username and/or Password")
            redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Logs the current session user out of the session
    flash('You have been logged out')
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/delete_account/<username>')
def delete_account(username):
    # Removes a user's account from the username provided
    mongo.db.users.remove({'username': username})
    flash('Your account has been deleted')
    return redirect(url_for('logout'))


'''Book CRUD'''


@app.route('/add_book')
def add_book():
    '''Renders the add-book form page, passes in the genre
    variable from the "genre" collection for use with the available
    genre dropdown menu'''
    return render_template('add-book.html', genre=mongo.db.genre.find())


@app.route('/insert_book', methods=['POST'])
def insert_book():
    # Insert book as dictionary for added database security
    book = {
        'genre_name': request.form.get('genre_name'),
        'image_url': request.form.get('image_url'),
        'book_title': request.form.get('book_title'),
        'book_author': request.form.get('book_author'),
        'book_blurb': request.form.get('book_blurb'),
        'book_quote': request.form.get('book_quote'),
        'rating': request.form.get('rating'),
        'created_at': datetime.utcnow()
    }
    mongo.db.books.insert_one(book)
    return redirect(url_for('home'))


@app.route('/edit_book/<book_id>')
def edit_book(book_id):
    # Renders the edit book page, passes all values into the template
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    return render_template('edit-book.html', book=the_book, genre=all_genre)


@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    # Update the edited book as dictionary
    mongo.db.books.update({'_id': ObjectId(book_id)}, {
        'genre_name': request.form.get('genre_name'),
        'image_url': request.form.get('image_url'),
        'book_title': request.form.get('book_title'),
        'book_author': request.form.get('book_author'),
        'book_blurb': request.form.get('book_blurb'),
        'book_quote': request.form.get('book_quote'),
        'rating': request.form.get('rating'),
        'created_at': datetime.utcnow()
    })
    return redirect(url_for('home'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # Delete the book from the database
    mongo.db.books.remove({'_id': ObjectId(book_id)})
    return redirect(url_for('home'))


'''Review CRUD'''


@app.route('/add_review/<book_id>', methods=['POST'])
def add_review(book_id):
    # Add the review to mongo as a dictionary for increased security
    review_object = {
        'username': request.form.get('username'),
        'review': request.form.get('review'),
        'rating': request.form.get('rating'),
        'created_at': datetime.utcnow().strftime('%b %d %Y')
    }
    review_object['book_id'] = book_id
    mongo.db.review.insert_one(review_object)
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/edit_review/<book_id>/<review_id>')
def edit_review(book_id, review_id):
    # Edit the review from within the book_review template
    review = mongo.db.review.find_one({'_id': ObjectId(review_id)})
    return render_template('edit-review.html', review=review)


@app.route('/update_review/<review_id>/<book_id>', methods=['POST'])
def update_review(review_id, book_id):
    # Update the edited review
    mongo.db.review.update(
        {'_id': ObjectId(review_id)},
        {
            'username': request.form.get('username'),
            'review': request.form.get('review'),
            'rating': request.form.get('rating'),
            'created_at': datetime.utcnow().strftime('%b %d %Y'),
            'book_id': book_id
        })
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/delete_review/<book_id>/<review_id>')
def delete_review(book_id, review_id):
    # Delete the review from the database
    mongo.db.review.remove({'_id': ObjectId(review_id)})
    return redirect(url_for('book_review', book_id=book_id))


# Run the app
if __name__ == '__main__':
    app.run(port=os.environ.get('PORT'), debug=True)
