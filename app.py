import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_paginate import Pagination, get_page_args
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from decouple import config
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'pen_hub'
app.config["MONGO_URI"] = config('MONGO_URI')
app.secret_key = config('SECRET_KEY')

mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template(
        "index.html",
        books=mongo.db.books.find().limit(10),
        recents=mongo.db.books.find(),
        quotes=mongo.db.books.find(),
        genre=mongo.db.genre.find()
    )


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route('/delete_account/<username>')
def delete_account(username):
    mongo.db.users.remove({"username": username})
    flash("Your account has been deleted")
    return redirect(url_for('logout'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"],
                request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}!".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            redirect(url_for("login"))
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route('/add_book')
def add_book():
    return render_template("add-book.html", genre=mongo.db.genre.find())


@app.route('/all_books')
def all_books():
    page, per_page, offset = get_page_args(
        page_parameter='page',
        per_page_parameter='per_page'
    )

    per_page = 6
    offset = page * per_page

    total = mongo.db.books.find().count()

    books = mongo.db.books.find()
    paginated_books = books[offset: offset + per_page]

    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='materialize'
    )
    return render_template(
        "all-books.html",
        books=paginated_books,
        page=page,
        per_page=per_page,
        pagination=pagination
    )


@app.route('/genre_list')
def genre_list():
    return render_template("genres.html", genre=mongo.db.genre.find())


@app.route('/book_review/<book_id>', methods=['GET'])
def book_review(book_id):
    rating_list = []

    get_review = mongo.db.review.find({"book_id": book_id})
    for i in get_review:
        rating_list.append(int(i['rating']))

    try:
        avg_rating = format(sum(rating_list)/len(rating_list), '.1f')
    except ZeroDivisionError:
        avg_rating = "0"

    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    reviews = mongo.db.review.find({"book_id": book_id})
    no_of_docs = mongo.db.review.count_documents({"book_id": book_id})
    mongo.db.books.update(
        {"_id": ObjectId(book_id)},
        {"$set": {"rating": avg_rating}}
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


@app.route('/insert_book', methods=['POST'])
def insert_book():
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
    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    return render_template('edit-book.html', book=the_book, genre=all_genre)


@app.route('/edit_review/<book_id>/<review_id>')
def edit_review(book_id, review_id):
    review = mongo.db.review.find_one({"_id": ObjectId(review_id)})
    return render_template('edit-review.html', review=review)


@app.route('/update_review/<review_id>/<book_id>', methods=['POST'])
def update_review(review_id, book_id):
    reviews = mongo.db.review
    reviews.update(
        {"_id": ObjectId(review_id)},
        {
            'username': request.form.get('username'),
            'review': request.form.get('review'),
            'rating': request.form.get('rating'),
            'created_at': datetime.utcnow().strftime('%b %d %Y'),
            'book_id': book_id
        })
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/add_review/<book_id>', methods=['POST'])
def add_review(book_id):
    review_object = {
        'username': request.form.get('username'),
        'review': request.form.get('review'),
        'rating': request.form.get('rating'),
        'created_at': datetime.utcnow().strftime('%b %d %Y')
    }
    review_object['book_id'] = book_id
    mongo.db.review.insert_one(review_object)
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    books = mongo.db.books
    books.update({"_id": ObjectId(book_id)},
                 {
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
    mongo.db.books.remove({'_id': ObjectId(book_id)})
    return redirect(url_for('home'))


@app.route('/delete_review/<book_id>/<review_id>')
def delete_review(book_id, review_id):
    mongo.db.review.remove({'_id': ObjectId(review_id)})
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/genre/<genre_id>')
def genre(genre_id):
    page, per_page, offset = get_page_args(
        page_parameter='page',
        per_page_parameter='per_page'
    )

    per_page = 6
    offset = page * per_page

    total = mongo.db.books.find().count()

    books = mongo.db.books.find()
    paginated_books = books[offset: offset + per_page]

    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='materialize'
    )

    the_genre = mongo.db.genre.find_one({"_id": ObjectId(genre_id)})
    return render_template(
        'genre.html',
        genre=the_genre,
        books=paginated_books,
        page=page,
        per_page=per_page,
        pagination=pagination
    )


@app.route("/search_books")
def search_books():
    query = request.args.get("search")
    query = query.title()
    search_value = mongo.db.books.find({
        "$or": [
            {'book_title': {"$regex": query}},
            {'book_author': {"$regex": query}},
            {'book_isbn': {"$regex": query}}
        ]
    })
    no_of_docs = mongo.db.books.count_documents({
        "$or": [
            {'book_title': {"$regex": query}},
            {'book_author': {"$regex": query}},
            {'book_isbn': {"$regex": query}}
        ]
    })
    return render_template(
        "search-results.html",
        search=search_value,
        query=query,
        no_of_docs=no_of_docs,
    )


@app.route('/logout')
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
