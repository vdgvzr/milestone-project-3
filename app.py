import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from decouple import config

app = Flask(__name__)

DB_PASSWORD = config('PASSWORD')

app.config["MONGO_DBNAME"] = 'pen_hub'
app.config["MONGO_URI"] = 'mongodb+srv://vdgvzr:' +\
                           DB_PASSWORD +\
                          '@myfirstcluster.iop5x.mongodb.net/'\
                          'pen_hub?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_books')
def get_books():
    return render_template("books.html", books=mongo.db.books.find())


@app.route('/add_book')
def add_book():
    return render_template("add-book.html", genre=mongo.db.genre.find())


@app.route('/book_review/<book_id>', methods=['GET'])
def book_review(book_id):
    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    reviews = mongo.db.review.find({"book_id": book_id})
    return render_template(
        'book-review.html',
        book=the_book,
        genre=all_genre,
        review=reviews
    )


@app.route('/insert_book', methods=['POST'])
def insert_book():
    book = mongo.db.books
    book.insert_one(request.form.to_dict())
    return redirect(url_for('book_review'))


@app.route('/edit_book/<book_id>')
def edit_book(book_id):
    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    return render_template('edit-book.html', book=the_book, genre=all_genre)


@app.route('/add_review/<book_id>', methods=['POST'])
def add_review(book_id):
    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    review_object = request.form.to_dict()
    review_object['book_id'] = book_id
    mongo.db.review.insert_one(review_object)
    return redirect(
        url_for('book_review'),
        book=the_book,
        review=review_object
    )


@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    books = mongo.db.books
    books.update({'_id': ObjectId(book_id)},
                 {
                    'genre_name': request.form.get('genre_name'),
                    'image_url': request.form.get('image_url'),
                    'book_title': request.form.get('book_title'),
                    'book_author': request.form.get('book_author'),
                    'book_isbn': request.form.get('book_isbn'),
                    'book_blurb': request.form.get('book_blurb'),
                    'book_quote': request.form.get('book_quote')
                 })
    return redirect(url_for('get_books'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    mongo.db.books.remove({'_id': ObjectId(book_id)})
    return redirect(url_for('get_books'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
